import configparser
import copy
import os
import random
import string
import time
from typing import Union

from PySide2.QtCore import Signal, Slot, QObject

from constants import constants
from constants.constants import DEFAULT_TONE_NAME, DEFAULT_SYNTH_MODEL, EMPTY_TONE, EMPTY_DSP_MODULE_ID, \
    EMPTY_DSP_PARAMS_LIST, INTERNAL_MEMORY_USER_TONE_COUNT, USER_TONE_TABLE_ROW_OFFSET
from constants.enums import ParameterType, SysexType
from models.parameter import MainParameter, AdvancedParameter
from models.tone import Tone
from services.midi_service import MidiService
from services.tyrant_midi_service import TyrantMidiService
from ui.change_instrument_window import ChangeInstrumentWindow
from ui.gui_helper import GuiHelper
from utils import utils
from utils.file_operations import FileOperations
from utils.utils import decode_param_value, int_to_hex, lsb_msb_to_int, get_all_instruments
from utils.worker import Worker


# Class for managing tone state and handling all communication between GUI and Midi Service
# NB! Use int values as its method parameters, all required byte/hex conversions make in the Midi Service!
class Core(QObject):
    synchronize_tone_signal = Signal()
    status_msg_signal = Signal(str, int)

    def __init__(self, main_window, status_bar):
        super().__init__()
        self.main_window = main_window
        self.status_bar = status_bar
        self.tone: Tone = Tone()
        self.midi_service = MidiService(self)
        self.tyrant_midi_service = TyrantMidiService()
        self.timeout = 0
        self.synchronize_tone_signal.connect(self.synchronize_tone_with_synth)
        self.status_msg_signal.connect(self.show_status_msg)

        cfg = configparser.ConfigParser()
        cfg.read(constants.CONFIG_FILENAME)
        self.tone.synthesizer_model = cfg.get("Synthesizer", "Model", fallback=DEFAULT_SYNTH_MODEL)

        self.is_status_bar_update_on_pause = False

    # Synchronize all Tone data: name, main params, DSP modules and their params
    @Slot()
    def synchronize_tone_with_synth(self):
        self.log("[INFO] Synchronizing tone...")
        self.main_window.loading_animation.start()
        # self.tone = Tone()  # if enabled, then tone is initialized twice during the application startup

        try:
            self.close_midi_ports()
            self.open_midi_ports()
        except Exception as e:
            self.show_error_msg(str(e))

        if self.midi_service.midi_out.is_port_open() and self.midi_service.midi_in.is_port_open():
            self.request_tone_name()
            self.request_main_parameters()
            self.request_dsp_module(0)
            self.request_dsp_module(1)
            self.request_dsp_module(2)
            self.request_dsp_module(3)
            self.request_advanced_parameters()
            self.request_volume_values()
            self.request_pan_values()

            # upper2, lower1 and lower2 tone names
            self.request_custom_parameter(SysexType.TONE_NUMBER.value, 1, 2, 3, 0, 0)
            self.request_custom_parameter(SysexType.TONE_NUMBER.value, 2, 2, 3, 0, 0)
            self.request_custom_parameter(SysexType.TONE_NUMBER.value, 3, 2, 3, 0, 0)

        self.main_window.central_widget.on_tab_changed(0)  # updates help tab and JSON (if JSON-tab opened)

        worker = Worker(self.redraw_main_and_advanced_params_pages)
        worker.signals.error.connect(lambda error: self.show_error_msg(str(error[1])))
        worker.start()
        self.main_window.loading_animation.stop()

    def redraw_main_and_advanced_params_pages(self):
        self.main_window.central_widget.redraw_main_params_panel_signal.emit()
        self.main_window.central_widget.redraw_advanced_params_panel_signal.emit()

    # Request tone name from synth
    def request_tone_name(self):
        try:
            self.midi_service.request_tone_name()
        except Exception as e:
            self.show_error_msg(str(e))

    # Process tone name from synth response
    def process_tone_name_response(self, response):
        tone_name = ''.join(chr(i) for i in response if chr(i).isprintable()).strip()
        self.log(f"[INFO] Synth tone name: {tone_name}")
        if tone_name:
            # Works only with user tones?
            self.main_window.top_widget.tone_name_input.setStyleSheet("color: black")
            self.tone.name = tone_name
        elif self.tone.name is None:
            self.tone.name = constants.DEFAULT_TONE_NAME
            self.request_tone_number_from_performance_params()

        self.main_window.top_widget.update_tone_name_input_and_parent_info()

    # A new method for retrieving tone number and name
    def request_tone_number_from_performance_params(self):
        try:
            self.midi_service.request_parameter_value_full(0, SysexType.TONE_NUMBER.value, 2, 3, 0, 0)
        except Exception as e:
            self.show_error_msg(str(e))

    def process_tone_number_from_performance_params_response(self, tone_number, block0):
        for instrument in get_all_instruments():
            if instrument.id == tone_number:
                self.log(f"[INFO] Tone name (by number from performance params): {instrument.name}")

                if block0 == 0:
                    self.tone.name = instrument.name
                    self.tone.parent_tone = instrument

                    self.main_window.central_widget.instrument_list.set_current_row_from_thread(
                        self.tone.parent_tone.id - 1)

                    # tone_id_and_name = self.get_tone_id_and_name()
                    self.main_window.top_widget.tone_name_input.setText(self.tone.name)
                else:
                    self.main_window.top_widget.select_item_by_id(block0, instrument.id)

                break

    # Request main parameter value from synth
    def request_main_parameters(self):
        for parameter in self.tone.main_parameter_list:
            self.log("[INFO] Requesting parameter: " + parameter.name)
            try:
                self.midi_service.request_parameter_value(parameter.block0, parameter.param_number)
            except Exception as e:
                self.show_error_msg(str(e))

    # Request advanced parameter value from synth
    def request_advanced_parameters(self):
        for parameter in self.tone.advanced_parameter_list:
            self.log("[INFO] Requesting parameter: " + parameter.name)
            try:
                self.midi_service.request_parameter_value(parameter.block0, parameter.param_number)
            except Exception as e:
                self.show_error_msg(str(e))

    # Process main/advanced parameter value response
    def process_parameter_response(self, param_number, block0, param_set, response):
        for parameter in self.tone.main_parameter_list:
            if parameter.param_number == param_number and parameter.block0 == block0:
                self.log(f"[INFO] {parameter.name}: {str(response)}")
                if parameter.type == ParameterType.SPECIAL_ATK_REL_KNOB:
                    value = int(int_to_hex(response[1]) + int_to_hex(response[0]), 16)
                elif len(response) == 1:
                    value = response[0]
                else:
                    value = lsb_msb_to_int(response[0], response[1])
                parameter.value = decode_param_value(value, parameter)
                break
        for parameter in self.tone.advanced_parameter_list:
            if parameter.param_number == param_number and parameter.block0 == block0:
                self.log(f"[INFO] {parameter.name}: {str(response)}")
                if len(response) == 1:
                    value = response[0]
                    if parameter.name == "Sound A Timbre Type" or parameter.name == "Sound B Timbre Type":
                        value = int(value / 2)
                else:
                    value = lsb_msb_to_int(response[0], response[1])
                parameter.value = decode_param_value(value, parameter)
                break
        if self.main_window.top_widget.upper1_volume.param_number == param_number:  # and cat==2
            # not only upper1_volume, but all 4 layers
            self.main_window.top_widget.redraw_volume_knob_signal.emit(block0, response[0])
        elif self.main_window.top_widget.upper1_pan.param_number == param_number:  # and cat==2
            parameter = self.main_window.top_widget.upper1_pan
            value = decode_param_value(response[0], parameter)
            self.main_window.top_widget.redraw_pan_knob_signal.emit(block0, value)

    # Send message to update synth's main parameter
    def send_parameter_change_sysex(self, parameter: Union[MainParameter, AdvancedParameter]):
        self.log(
            "[INFO] Param " + str(parameter.name) + ": " + str(parameter.param_number) + ", " + str(parameter.value))
        value = utils.encode_value_by_type(parameter)
        if parameter.name == "Sound A Timbre Type" or parameter.name == "Sound B Timbre Type":
            value = int(value * 2)

        try:
            if parameter.type == ParameterType.SPECIAL_ATK_REL_KNOB:
                self.midi_service.send_atk_rel_parameter_change_sysex(parameter.block0,
                                                                      parameter.param_number, value)
            elif parameter.name in constants.SHORT_PARAMS:
                self.midi_service.send_parameter_change_short_sysex(parameter.block0,
                                                                    parameter.param_number, value)
            else:
                self.midi_service.send_parameter_change_sysex(parameter.block0, parameter.param_number, value)
        except Exception as e:
            self.show_error_msg(str(e))

    def send_performance_param_change_sysex(self, parameter: AdvancedParameter):
        self.log(
            "[INFO] Param " + str(parameter.name) + ": " + str(parameter.param_number) + ", " + str(parameter.value))
        value = utils.encode_value_by_type(parameter)
        self.midi_service.send_parameter_value_full(parameter.block0, parameter.param_number, 2, 3, 0, value, 0)

    # Request DSP module from synth
    def request_dsp_module(self, block0):
        try:
            self.midi_service.request_dsp_module(block0)
        except Exception as e:
            self.show_error_msg(str(e))

    # Process DSP module from synth response
    def process_dsp_module_response(self, block0: int, dsp_module_id: int):
        self.update_tone_dsp_module_and_refresh_gui(block0, dsp_module_id)
        self.request_dsp_module_parameters(block0, dsp_module_id)

    # On list widget changed: update tone dsp and send module change sysex
    def update_dsp_module_from_list(self, block0, dsp_module_id):
        self.update_tone_dsp_module_and_refresh_gui(block0, dsp_module_id)

        try:
            if dsp_module_id is None:
                self.midi_service.send_dsp_module_change_sysex(block0, EMPTY_DSP_MODULE_ID)
                self.midi_service.send_dsp_params_change_sysex(block0, EMPTY_DSP_PARAMS_LIST)
                self.midi_service.send_dsp_bypass_sysex(block0, True)
                if self.main_window.central_widget.current_dsp_page:
                    self.main_window.central_widget.current_dsp_page.redraw_dsp_params_panel_signal.emit()
            else:
                self.midi_service.send_dsp_bypass_sysex(block0, False)
                self.midi_service.send_dsp_module_change_sysex(block0, dsp_module_id)
                self.request_dsp_module_parameters(block0, dsp_module_id)
        except Exception as e:
            self.show_error_msg(str(e))

    # Update tone dsp module and refresh GUI
    def update_tone_dsp_module_and_refresh_gui(self, block0, dsp_module_id):
        dsp_module_attr, dsp_page_attr = constants.BLOCK_MAPPING[block0]
        setattr(self.tone, dsp_module_attr, copy.deepcopy(Tone.get_dsp_module_by_id(dsp_module_id)))
        dsp_page = getattr(self.main_window.central_widget, dsp_page_attr)
        dsp_page.dsp_module = getattr(self.tone, dsp_module_attr)
        if dsp_page.dsp_module:
            self.log(f"[INFO] DSP module: {dsp_page.dsp_module.name}")
            dsp_page.dsp_module.bypass.value = 0
            self.main_window.central_widget.tab_widget.setTabIcon(block0 + 1, GuiHelper.get_green_icon())
            # self.main_window.central_widget.tab_widget.setTabText(block0 + 1, dsp_page.dsp_module.name)
        else:
            self.main_window.central_widget.tab_widget.setTabIcon(block0 + 1, GuiHelper.get_white_icon())
            # self.main_window.central_widget.tab_widget.setTabText(block0 + 1, "DSP X")

        dsp_page.list_widget.blockSignals(True)
        dsp_page.list_widget.setCurrentItem(dsp_page.get_list_item_by_dsp_id(dsp_module_id))
        dsp_page.list_widget.blockSignals(False)

        if dsp_page == self.main_window.central_widget.current_dsp_page:
            self.main_window.central_widget.update_help_text_panel_signal.emit()

    # Request DSP module parameters from synth
    def request_dsp_module_parameters(self, block0, dsp_module_id):
        if dsp_module_id is not None:
            try:
                self.midi_service.request_dsp_params(block0)
            except Exception as e:
                self.show_error_msg(str(e))

    # Process DSP module parameters from synth response
    def process_dsp_module_parameters_response(self, block0, synth_dsp_params):
        dsp_module_attr, dsp_page_attr = constants.BLOCK_MAPPING[block0]
        dsp_module = getattr(self.tone, dsp_module_attr)
        if dsp_module is not None:
            for idx, dsp_param in enumerate(dsp_module.dsp_parameter_list):
                if dsp_param.type == ParameterType.SPECIAL_DELAY_KNOB:
                    dsp_param.value = int(str(synth_dsp_params[12]) + str(synth_dsp_params[13]))
                else:
                    dsp_param.value = decode_param_value(synth_dsp_params[idx], dsp_param)

        if self.main_window.central_widget.current_dsp_page:
            self.main_window.central_widget.current_dsp_page.redraw_dsp_params_panel_signal.emit()

    def request_volume_values(self):
        try:
            self.midi_service.request_parameter_value_full(self.main_window.top_widget.upper1_volume.block0,
                                                           self.main_window.top_widget.upper1_volume.param_number,
                                                           2, 3, 0, 0)
            self.midi_service.request_parameter_value_full(self.main_window.top_widget.upper2_volume.block0,
                                                           self.main_window.top_widget.upper2_volume.param_number,
                                                           2, 3, 0, 0)
            self.midi_service.request_parameter_value_full(self.main_window.top_widget.lower1_volume.block0,
                                                           self.main_window.top_widget.lower1_volume.param_number,
                                                           2, 3, 0, 0)
            self.midi_service.request_parameter_value_full(self.main_window.top_widget.lower2_volume.block0,
                                                           self.main_window.top_widget.lower2_volume.param_number,
                                                           2, 3, 0, 0)

        except Exception as e:
            self.show_error_msg(str(e))

    def request_pan_values(self):
        try:
            self.midi_service.request_parameter_value_full(self.main_window.top_widget.upper1_pan.block0,
                                                           self.main_window.top_widget.upper1_pan.param_number,
                                                           2, 3, 0, 0)
            self.midi_service.request_parameter_value_full(self.main_window.top_widget.upper2_pan.block0,
                                                           self.main_window.top_widget.upper2_pan.param_number,
                                                           2, 3, 0, 0)
            self.midi_service.request_parameter_value_full(self.main_window.top_widget.lower1_pan.block0,
                                                           self.main_window.top_widget.lower1_pan.param_number,
                                                           2, 3, 0, 0)
            self.midi_service.request_parameter_value_full(self.main_window.top_widget.lower2_pan.block0,
                                                           self.main_window.top_widget.lower2_pan.param_number,
                                                           2, 3, 0, 0)

        except Exception as e:
            self.show_error_msg(str(e))

    # Send message to update synth's DSP parameters
    def set_synth_dsp_params(self, _):
        try:
            dsp_page = self.main_window.central_widget.current_dsp_page
            if dsp_page:
                self.midi_service.send_dsp_params_change_sysex(dsp_page.block0, dsp_page.get_dsp_params_as_list())
        except Exception as e:
            self.show_error_msg(str(e))

    def send_dsp_bypass(self, block0, bypass):
        try:
            self.midi_service.send_dsp_bypass_sysex(block0, bypass)
        except Exception as e:
            self.show_error_msg(str(e))

    # Send program change message
    def change_instrument_by_id_from_list(self, instrument_id):
        instrument = Tone.get_instrument_by_id(instrument_id)
        if instrument:
            self.tone.name = instrument.name
            self.tone.parent_tone = instrument
            self.log(f"[INFO] Selected tone: {instrument_id} - {self.tone.parent_tone.name}")
            try:
                self.midi_service.send_change_tone_msg(instrument_id, 0)
                self.main_window.top_widget.tone_name_input.setStyleSheet("color: #1B998B")
                self.synchronize_tone_signal.emit()
            except Exception as e:
                self.show_error_msg(str(e))

    # Select calibration tone
    def select_calibration_tone(self, instrument):
        try:
            self.midi_service.send_change_tone_msg_2(instrument.id)
            self.main_window.top_widget.tone_name_input.setStyleSheet("color: #1B998B")
            self.tone.name = instrument.name
            self.tone.parent_tone = None
            self.synchronize_tone_signal.emit()
        except Exception as e:
            self.show_error_msg(str(e))

    # Intercept instrument change messages from synth
    def process_instrument_select_response(self, bank, program):
        self.log("[INFO] Instrument: " + str(bank) + ", " + str(program))
        self.find_instrument_and_update_tone(bank, program)

        # tone_id_and_name = self.get_tone_id_and_name()
        self.main_window.top_widget.tone_name_input.setText(self.tone.name)

    # Deprecated
    def get_tone_id_and_name(self):
        if self.tone.parent_tone:
            tone_id_and_name = "{:03}".format(self.tone.parent_tone.id) + " " + self.tone.name
        else:
            tone_id_and_name = self.tone.name
        return tone_id_and_name

    def find_instrument_and_update_tone(self, bank, program):
        is_found = False
        for instrument in get_all_instruments():
            if instrument.bank == bank and instrument.program == program:
                is_found = True
                self.tone.name = instrument.name
                self.tone.parent_tone = instrument
                self.main_window.central_widget.instrument_list.set_current_row_from_thread(
                    self.tone.parent_tone.id - 1)
                break
        if not is_found:
            self.tone.name = DEFAULT_TONE_NAME
            self.tone.parent_tone = None
            self.main_window.central_widget.instrument_list.clearSelection()

    def countdown_and_autosynchronize(self, timeout):
        try:
            if self.timeout > 0:
                # countdown timer exists: reset time and exit
                self.timeout = timeout
            else:
                # start countdown
                self.timeout = timeout
                while self.timeout > 0:
                    text = f"Auto-synchronize countdown: {self.timeout}"
                    self.status_msg_signal.emit(text, 1000)
                    self.timeout -= 1
                    time.sleep(1)

                self.synchronize_tone_signal.emit()
        except Exception as e:
            self.show_error_msg(str(e))

    # Open midi ports
    def open_midi_ports(self):
        self.midi_service.open_midi_ports()

    # Close midi ports
    def close_midi_ports(self):
        self.midi_service.close_midi_ports()

    # Load Tone from JSON
    def load_tone_from_json(self, json_tone: dict):
        def _get_block0(dsp_id):
            block0_mapping = {
                "dsp_1": 0,
                "dsp_2": 1,
                "dsp_3": 2,
                "dsp_4": 3
            }
            return block0_mapping.get(dsp_id)

        # Name
        if "name" in json_tone:
            self.tone.name = json_tone["name"]

        # Parent tone
        show_modal_window = False
        current_parent_tone = self.tone.parent_tone
        json_synthesizer_model = json_tone["synthesizer_model"] if "synthesizer_model" in json_tone else None
        json_parent_id = None
        json_parent_bank = None
        json_parent_program = None
        json_parent_name = None
        json_parent_tone = json_tone.get("parent_tone")

        if json_parent_tone:
            json_parent_id = json_parent_tone.get("id")
            json_parent_bank = json_parent_tone.get("bank")
            json_parent_program = json_parent_tone.get("program")
            json_parent_name = json_parent_tone.get("name")

            if json_parent_bank is not None and json_parent_program is not None:
                self.tone.parent_tone = None
                self.find_instrument_and_update_tone(json_parent_bank, json_parent_program)

                if self.tone.parent_tone is not None and self.tone.parent_tone.id is not None:
                    # Parent tone is found: automatically select instrument
                    try:
                        self.midi_service.send_change_tone_msg(self.tone.parent_tone.id, 0)
                        self.main_window.top_widget.tone_name_input.setStyleSheet("color: #1B998B")
                        self.main_window.top_widget.tone_name_input.setText(self.tone.name)
                    except Exception as e:
                        self.show_error_msg(str(e))
                else:
                    show_modal_window = True  # refactor that ladder :)
            else:
                show_modal_window = True
        else:
            show_modal_window = True

        if show_modal_window:
            # Parent tone is not found: show modal window
            json_synthesizer_model_str = "unknown synthesizer model" if json_synthesizer_model is None else str(
                json_synthesizer_model)
            json_parent_id_str = "" if json_parent_id is None else str(json_parent_id) + " "
            json_parent_name_str = "Unknown Name" if not json_parent_name else json_parent_name
            json_parent_bank_str = "???" if json_parent_bank is None else str(json_parent_bank)
            json_parent_program_str = "???" if json_parent_program is None else str(json_parent_program)

            modal_window_message = "<br/>The required parent tone from the " + json_synthesizer_model_str + " was not found:<br/><b>" \
                                   + json_parent_id_str + json_parent_name_str + " (bank: " + json_parent_bank_str + ", program: " + json_parent_program_str \
                                   + ")</b><br/><br/>You can apply parameters from a JSON file to the currently selected tone."
            button_text = " Apply Parameters to Current Tone (" + str(current_parent_tone.id) + " " \
                          + current_parent_tone.name + ")"
            self.show_status_msg("Select a parent tone to proceed", 0)
            modal_window = ChangeInstrumentWindow(self, modal_window_message, button_text)
            modal_window.exec_()

            self.show_status_msg("", 0)
            self.tone.parent_tone = current_parent_tone
            self.main_window.top_widget.tone_name_input.setText(self.tone.name)

        # Main parameters
        if "parameters" in json_tone:
            for json_main_parameter in json_tone["parameters"]:
                if "name" in json_main_parameter and "value" in json_main_parameter:
                    tone_main_parameter = next(
                        (param for param in self.tone.main_parameter_list if param.name == json_main_parameter["name"]),
                        None)
                    if tone_main_parameter:
                        tone_main_parameter.value = json_main_parameter["value"] - 1 if \
                            tone_main_parameter.type == ParameterType.COMBO else json_main_parameter["value"]
                        self.send_parameter_change_sysex(tone_main_parameter)
            self.main_window.central_widget.redraw_main_params_panel_signal.emit()

        # Advanced parameters
        if "advanced_parameters" in json_tone:
            for json_advanced_parameter in json_tone["advanced_parameters"]:
                if "name" in json_advanced_parameter and "value" in json_advanced_parameter:
                    tone_advanced_parameter = next(
                        (param for param in self.tone.advanced_parameter_list if
                         param.name == json_advanced_parameter["name"]), None)
                    if tone_advanced_parameter:
                        tone_advanced_parameter.value = json_advanced_parameter["value"] - 1 if \
                            tone_advanced_parameter.type == ParameterType.COMBO else json_advanced_parameter["value"]
                        self.send_parameter_change_sysex(tone_advanced_parameter)
            self.main_window.central_widget.redraw_advanced_params_panel_signal.emit()

        # DSP
        if "dsp_modules" in json_tone:
            for json_dsp_id, json_dsp_module in json_tone["dsp_modules"].items():
                block0 = _get_block0(json_dsp_id)
                if block0 is not None and json_dsp_module is not None and "name" in json_dsp_module:
                    self._load_dsp_from_json(block0, json_dsp_module)

    def _load_dsp_from_json(self, block0, json_dsp_module):
        dsp_module = next(
            (dsp_module for dsp_module in constants.ALL_DSP_MODULES if
             dsp_module.name == json_dsp_module["name"]), None)
        if dsp_module:
            dsp_module_id = dsp_module.id
            self.update_tone_dsp_module_and_refresh_gui(block0, dsp_module_id)
            try:
                if dsp_module_id is None:
                    self.midi_service.send_dsp_bypass_sysex(block0, True)
                    if self.main_window.central_widget.current_dsp_page:
                        self.main_window.central_widget.current_dsp_page.redraw_dsp_params_panel_signal.emit()
                else:
                    self.midi_service.send_dsp_bypass_sysex(block0, False)
                    self.midi_service.send_dsp_module_change_sysex(block0, dsp_module_id)
            except Exception as e:
                self.show_error_msg(str(e))

            dsp_module_attr, dsp_page_attr = constants.BLOCK_MAPPING[block0]
            dsp_page = getattr(self.main_window.central_widget, dsp_page_attr)
            dsp_page.dsp_module = getattr(self.tone, dsp_module_attr)

            if dsp_page.dsp_module and "bypass" in json_dsp_module:
                dsp_page.dsp_module.bypass.value = json_dsp_module["bypass"]

            if "parameters" in json_dsp_module:
                for json_dsp_parameter in json_dsp_module["parameters"]:
                    if "name" in json_dsp_parameter and "value" in json_dsp_parameter:
                        tone_dsp_parameter = next(
                            (param for param in dsp_page.dsp_module.dsp_parameter_list if
                             param.name == json_dsp_parameter["name"]), None)
                        if tone_dsp_parameter:
                            tone_dsp_parameter.value = json_dsp_parameter["value"] - 1 if \
                                tone_dsp_parameter.type == ParameterType.COMBO else json_dsp_parameter["value"]

                time.sleep(0.3)
                try:
                    self.midi_service.send_dsp_params_change_sysex(block0,
                                                                   dsp_page.get_dsp_params_as_list())
                except Exception as e:
                    self.show_error_msg(str(e))

                if self.main_window.central_widget.current_dsp_page:
                    self.main_window.central_widget.current_dsp_page.redraw_dsp_params_panel_signal.emit()

    def send_custom_midi_msg(self, midi_msg: str):
        self.midi_service.send_custom_midi_msg(midi_msg)

    def request_custom_parameter(self, number: int, block0: int, category: int, memory: int, parameter_set: int,
                                 size: int):
        self.midi_service.request_parameter_value_full(block0, number, category, memory, parameter_set, size)

    def send_instrument_change_sysex(self, block0, tone_number):
        self.midi_service.send_change_tone_msg(tone_number, block0)

    @Slot()
    def show_status_msg(self, text: str, msecs: int):
        if not self.is_status_bar_update_on_pause:
            self.status_bar.setStyleSheet("background-color: white; color: black")
            self.status_bar.showMessage(text, msecs)

    def show_error_msg(self, text: str):
        self.log("[ERROR] " + text)
        self.status_bar.setStyleSheet("background-color: white; color: red")
        self.status_bar.showMessage(text, 5000)

        self.main_window.loading_animation.stop()

    def pause_status_bar_updates(self, is_status_bar_update_on_pause: bool):
        self.is_status_bar_update_on_pause = is_status_bar_update_on_pause

    def log(self, msg: str):
        self.main_window.log_texbox.log(msg)

    def start_ton_file_save_worker(self, file_name):
        self.main_window.loading_animation.start()
        self.status_msg_signal.emit("Saving... Please wait!", 10000)
        self.log(f"[INFO] Saving tone file: {file_name}")

        if not self.tone.name:
            file_name_without_extension = os.path.splitext(os.path.basename(file_name))[0]
            self.tone.name = file_name_without_extension

        worker = Worker(self.get_current_tone_as_ton_file, self.tone.name)
        worker.signals.error.connect(lambda error: self.show_error_msg(str(error[1])))
        worker.signals.result.connect(lambda ton_file_data: self.save_file(file_name, ton_file_data))
        worker.start()

    def get_current_tone_as_ton_file(self, tone_name: str):
        new_tone_name = tone_name[:8]  # trim to first 8 symbols
        current_tone = self.tyrant_midi_service.read_current_tone(new_tone_name)
        ton_file_data = self.tyrant_midi_service.wrap_tone_file(current_tone)

        # Restore default MIDI-in callback after using tyrant_midi_service
        self.close_midi_ports()
        self.open_midi_ports()

        return ton_file_data

    def save_file(self, file_name, ton_file_data):
        FileOperations.save_binary_file(file_name, ton_file_data)
        self.status_msg_signal.emit("File successfully saved!", 3000)
        self.main_window.loading_animation.stop()

    def start_tone_upload_worker(self, tone_number):
        if tone_number < 801 or tone_number > 900:
            raise Exception("The 'Tone Number' must be in the range of 801 to 900.")

        self.main_window.loading_animation.start()
        self.status_msg_signal.emit("Saving... Please wait!", 10000)
        self.log(f"[INFO] Saving tone number: {tone_number}")

        worker = Worker(self.upload_tone, tone_number, self.tone.name)
        worker.signals.error.connect(lambda error: self.show_error_msg(str(error[1])))
        worker.start()

    # upload_tone: used in old separate rename-dialog
    def upload_tone(self, tone_number, tone_name):
        if not tone_name:
            tone_name = DEFAULT_TONE_NAME

        current_tone = self.tyrant_midi_service.read_current_tone(tone_name[:8])

        self.tyrant_midi_service.bulk_upload(tone_number - USER_TONE_TABLE_ROW_OFFSET, current_tone, memory=1,
                                             category=3)
        self.close_midi_ports()
        self.open_midi_ports()

        # self.synchronize_tone_signal.emit()
        self.status_msg_signal.emit("Tone successfully saved!", 3000)
        self.main_window.loading_animation.stop()

    # @Deprecated(used in old separate rename-dialog)
    def start_tone_rename_worker(self, tone_number, new_name):
        if tone_number < 801 or tone_number > 900:
            raise Exception("The 'Tone Number' must be in the range of 801 to 900.")

        self.main_window.loading_animation.start()
        self.status_msg_signal.emit("Renaming... Please wait!", 10000)
        self.log(f"[INFO] Renaming tone number: {tone_number}")

        worker = Worker(self.rename_tone_from_main_menu, tone_number, new_name)
        worker.signals.error.connect(lambda error: self.show_error_msg(str(error[1])))
        worker.start()

    # @Deprecated(used in old separate rename-dialog)
    def rename_tone_from_main_menu(self, tone_number, new_name):
        tone_data = self.tyrant_midi_service.bulk_download(tone_number - USER_TONE_TABLE_ROW_OFFSET, memory=1,
                                                           category=3)

        if new_name:
            tone_data = bytearray(tone_data)  # Convert the tone data to a mutable bytearray
            new_tone_name_bytes = new_name.encode('utf-8')
            tone_data[0x1A6:0x1B6] = new_tone_name_bytes.ljust(16, b' ')
            tone_data[0x1A6 + 8] = 0x00

        self.tyrant_midi_service.bulk_upload(tone_number - USER_TONE_TABLE_ROW_OFFSET, tone_data, memory=1, category=3)
        self.close_midi_ports()
        self.open_midi_ports()

        self.synchronize_tone_signal.emit()
        self.status_msg_signal.emit("Tone successfully renamed!", 3000)
        self.main_window.loading_animation.stop()

    def rename_tone(self, tone_number, new_tone_name):
        """Tone manager: Rename tone"""
        if tone_number < 801 or tone_number > 900:
            raise Exception("The 'Tone Number' must be in the range of 801 to 900.")

        self.log(f"[INFO] Renaming tone: {tone_number} - {new_tone_name}")
        tone_data = self.tyrant_midi_service.bulk_download(tone_number - USER_TONE_TABLE_ROW_OFFSET, memory=1,
                                                           category=3)

        if new_tone_name:
            tone_data = bytearray(tone_data)  # Convert the tone data to a mutable bytearray
            new_tone_name_bytes = new_tone_name.encode('utf-8')[:8]  # trim to first 8 symbols and get bytes
            tone_data[0x1A6:0x1B6] = new_tone_name_bytes.ljust(16, b' ')
            tone_data[0x1A6 + 8] = 0x00

        self.tyrant_midi_service.bulk_upload(tone_number - USER_TONE_TABLE_ROW_OFFSET, tone_data, memory=1, category=3)
        self.close_midi_ports()
        self.open_midi_ports()

        self.main_window.user_tone_manager_window.load_memory_tone_names()  # reload list and stop loading animation
        self.status_msg_signal.emit("Tone successfully renamed!", 3000)

    # @Deprecated (used in old separate delete-dialog)
    def start_tone_delete_worker(self, tone_number):
        if tone_number < 801 or tone_number > 900:
            raise Exception("The 'Tone Number' must be in the range of 801 to 900.")

        self.main_window.loading_animation.start()
        self.status_msg_signal.emit("Deleting... Please wait!", 10000)
        self.log(f"[INFO] Deleting tone number: {tone_number}")

        worker = Worker(self.delete_tone, tone_number)
        worker.signals.error.connect(lambda error: self.show_error_msg(str(error[1])))
        worker.start()

    # @Deprecated (used in old separate delete-dialog)
    def delete_tone(self, tone_number):
        self.tyrant_midi_service.bulk_upload(tone_number - USER_TONE_TABLE_ROW_OFFSET, EMPTY_TONE, memory=1, category=3)
        self.close_midi_ports()
        self.open_midi_ports()

        self.synchronize_tone_signal.emit()
        self.status_msg_signal.emit("Tone successfully deleted!", 3000)
        self.main_window.loading_animation.stop()

    def delete_next_tone(self, tone_number, tone_name):
        """Tone manager: Delete tone"""
        if tone_number < 801 or tone_number > 900:
            raise Exception("The 'Tone Number' must be in the range of 801 to 900.")

        self.log(f"[INFO] Deleting tone: {tone_number} - {tone_name}")
        self.tyrant_midi_service.bulk_upload(tone_number - USER_TONE_TABLE_ROW_OFFSET, EMPTY_TONE, memory=1, category=3)
        self.main_window.user_tone_manager_window.delete_next_tone()

    def after_all_selected_tones_deleted(self):
        self.close_midi_ports()
        self.open_midi_ports()

        self.main_window.user_tone_manager_window.load_memory_tone_names()  # reload list and stop loading animation
        self.status_msg_signal.emit("Tone(s) successfully deleted!", 3000)

    def request_user_memory_tone_names(self):
        for i in range(0, INTERNAL_MEMORY_USER_TONE_COUNT):
            self.request_user_memory_tone_name(i)

    def request_user_memory_tone_name(self, tone_number):
        self.midi_service.request_parameter_value_full(0, 0, 3, 1, tone_number, 12)

    def process_user_memory_tone_name_response(self, tone_number_response, tone_name_response):
        tone_number = lsb_msb_to_int(tone_number_response[0], tone_number_response[1])
        tone_name = ''.join(chr(i) for i in tone_name_response if chr(i).isprintable()).strip()
        if self.main_window.user_tone_manager_window:
            self.main_window.user_tone_manager_window.add_item(tone_number, tone_name)

    def load_tone_data(self, tone_number):
        if tone_number < 801 or tone_number > 900:
            raise Exception("The 'Tone Number' must be in the range of 801 to 900.")

        tone_data = self.tyrant_midi_service.bulk_download(tone_number - USER_TONE_TABLE_ROW_OFFSET, memory=1,
                                                           category=3)
        self.close_midi_ports()
        self.open_midi_ports()

        return tone_data

    def save_tone_data(self, tone_number, tone_data):
        if tone_number < 801 or tone_number > 900:
            raise Exception("The 'Tone Number' must be in the range of 801 to 900.")

        self.tyrant_midi_service.bulk_upload(tone_number - USER_TONE_TABLE_ROW_OFFSET, tone_data, memory=1, category=3)
        self.close_midi_ports()
        self.open_midi_ports()

    def upload_current_tone(self, tone_number):
        """Tone manager: Save current tone"""
        tone_name = self.tone.name
        if not tone_name:
            tone_name = DEFAULT_TONE_NAME

        current_tone = self.tyrant_midi_service.read_current_tone(tone_name[:8])

        self.tyrant_midi_service.bulk_upload(tone_number - USER_TONE_TABLE_ROW_OFFSET, current_tone, memory=1,
                                             category=3)
        self.close_midi_ports()
        self.open_midi_ports()

        self.main_window.user_tone_manager_window.load_memory_tone_names()  # reload list and stop loading animation
        self.status_msg_signal.emit("Tone successfully saved!", 3000)

    def on_randomize_tone_button_pressed(self):
        msg = "Setting random main parameters and selecting 1–2 random DSP modules"
        self.log(f"[INFO] {msg}...")
        self.main_window.loading_animation.start()

        # Random parent tone
        if self.main_window.change_parent_tone_checkbox.isChecked():
            max_number = self.main_window.central_widget.instrument_list.count()
            if max_number > 800:
                max_number = 800  # do not choose user tones
            new_number = random.randint(1, max_number)
            self.send_instrument_change_sysex(0, new_number)
            self.process_tone_number_from_performance_params_response(new_number, 0)

        # Random name and main params
        self.generate_random_name()
        self.main_window.central_widget.on_random_button_pressed()

        # Random DSP modules
        random_dsp_1 = random.randint(0, self.main_window.central_widget.dsp_page_1.list_widget.count() - 1)
        random_dsp_2 = random.randint(0, self.main_window.central_widget.dsp_page_2.list_widget.count() - 1)

        if random_dsp_1 == 0 and random_dsp_2 > 0:  # swap
            random_dsp_1, random_dsp_2 = random_dsp_2, random_dsp_1

        self.main_window.central_widget.dsp_page_1.list_widget.setCurrentRow(random_dsp_1)

        if self.tone.dsp_module_1 and self.tone.dsp_module_1.name == "Distortion":
            random_dsp_2 = 0  # if  DSP 1 is distortion, do not select another DSP module

        self.main_window.central_widget.dsp_page_2.list_widget.setCurrentRow(random_dsp_2)

        if self.tone.dsp_module_2 and self.tone.dsp_module_2.name == "Distortion":
            # move distortion to DSP 1, do not select DSP 2
            random_dsp_1 = random_dsp_2
            random_dsp_2 = 0
            self.main_window.central_widget.dsp_page_1.list_widget.setCurrentRow(random_dsp_1)
            self.main_window.central_widget.dsp_page_2.list_widget.setCurrentRow(random_dsp_2)

        if random_dsp_1 > 0 or random_dsp_2 > 0:
            msg += ": " + ", ".join(filter(None, [
                self.tone.dsp_module_1.name if random_dsp_1 > 0 else None,
                self.tone.dsp_module_2.name if random_dsp_2 > 0 else None
            ]))

        self.show_status_msg(msg, 3000)
        self.pause_status_bar_updates(True)

        # Random DSP params
        worker = Worker(self.randomize_dsp_params, random_dsp_1, random_dsp_2)
        worker.signals.error.connect(lambda error: self.show_error_msg(str(error[1])))
        worker.start()

    def randomize_dsp_params(self, random_dsp_1, random_dsp_2):
        if random_dsp_1 > 0:
            time.sleep(0.3)
            self.main_window.central_widget.dsp_page_1.on_random_button_pressed(
                self.main_window.central_widget.dsp_page_1.block0)

        if random_dsp_2 > 0:
            time.sleep(0.3)
            self.main_window.central_widget.dsp_page_2.on_random_button_pressed(
                self.main_window.central_widget.dsp_page_2.block0)

        self.pause_status_bar_updates(False)
        self.main_window.loading_animation.stop()

    def generate_random_name(self):
        self.tone.name = self.generate_random_word()
        self.main_window.top_widget.tone_name_input.setText(self.tone.name)

    @staticmethod
    def generate_random_word():
        letters = string.ascii_letters
        digits = string.digits
        symbols = "-_"

        first_char = random.choice(string.ascii_uppercase)
        second_char = random.choice(string.ascii_lowercase + symbols)
        third_char = random.choice(letters + symbols)
        middle_chars = ''.join(random.choices(letters + digits + symbols, k=4))
        last_char = random.choice(letters + digits + "!")

        return first_char + second_char + third_char + middle_chars + last_char
