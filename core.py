import configparser
import copy
import os
import time

from PySide2.QtCore import Signal, Slot, QObject

from constants import constants
from constants.constants import DEFAULT_TONE_NAME, DEFAULT_SYNTH_MODEL, EMPTY_TONE, EMPTY_DSP_MODULE_ID, \
    EMPTY_DSP_PARAMS_LIST
from constants.enums import ParameterType
from models.parameter import MainParameter
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
        # self.lock = QReadWriteLock()
        self.timeout = 0
        self.synchronize_tone_signal.connect(self.synchronize_tone_with_synth)
        self.status_msg_signal.connect(self.show_status_msg)

        cfg = configparser.ConfigParser()
        cfg.read(constants.CONFIG_FILENAME)
        self.tone.synthesizer_model = cfg.get("Synthesizer", "Model", fallback=DEFAULT_SYNTH_MODEL)

    # Synchronize all Tone data: name, main params, DSP modules and their params
    @Slot()
    def synchronize_tone_with_synth(self):
        # self.lock.lockForWrite()
        self.log("[INFO] Synchronizing tone...")
        self.midi_service.active_sync_job_count = 0
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
            self.request_upper_volume()

        self.main_window.central_widget.on_tab_changed(0)  # updates help tab and JSON (if JSON-tab opened)

        # self.lock.unlock()

        worker = Worker(self.redraw_main_and_advanced_params_pages)
        worker.signals.error.connect(lambda error: self.show_error_msg(str(error[1])))
        worker.start()
        self.main_window.loading_animation.stop()

    def redraw_main_and_advanced_params_pages(self):
        for i in range(0, 10):
            # self.lock.lockForWrite()
            if self.midi_service.active_sync_job_count == 0:
                # self.lock.unlock()
                self.main_window.central_widget.redraw_main_params_panel_signal.emit()
                self.main_window.central_widget.redraw_advanced_params_panel_signal.emit()
                break
            # self.lock.unlock()
            time.sleep(0.5)

    # Request tone name from synth
    def request_tone_name(self):
        try:
            self.midi_service.request_tone_name()
        except Exception as e:
            self.show_error_msg(str(e))

    # Process tone name from synth response
    def process_tone_name_response(self, response):
        # self.lock.lockForWrite()
        tone_name = ''.join(chr(i) for i in response if chr(i).isprintable()).strip()
        self.log("[INFO] Synth tone name: " + tone_name)
        if tone_name:
            self.tone.name = tone_name
        elif self.tone.name is None:
            self.tone.name = constants.DEFAULT_TONE_NAME

        tone_id_and_name = self.get_tone_id_and_name()
        self.main_window.top_widget.tone_name_label.setText(tone_id_and_name)
        # self.lock.unlock()

    # Request main parameter value from synth
    def request_main_parameters(self):
        for parameter in self.tone.main_parameter_list:
            self.log("[INFO] Requesting parameter: " + parameter.name)
            try:
                self.midi_service.request_parameter_value(parameter.block_id, parameter.param_number)
            except Exception as e:
                self.show_error_msg(str(e))

    # Request advanced parameter value from synth
    def request_advanced_parameters(self):
        for parameter in self.tone.advanced_parameter_list:
            self.log("[INFO] Requesting parameter: " + parameter.name)
            try:
                self.midi_service.request_parameter_value(parameter.block_id, parameter.param_number)
            except Exception as e:
                self.show_error_msg(str(e))

    # Process main/advanced parameter value response
    def process_parameter_response(self, param_number, block_id, response):
        for parameter in self.tone.main_parameter_list:
            if parameter.param_number == param_number and parameter.block_id == block_id:
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
            if parameter.param_number == param_number and parameter.block_id == block_id:
                self.log(f"[INFO] {parameter.name}: {str(response)}")
                if len(response) == 1:
                    value = response[0]
                    if parameter.name == "Sound A Timbre Type" or parameter.name == "Sound B Timbre Type":
                        value = int(value / 2)
                else:
                    value = lsb_msb_to_int(response[0], response[1])
                parameter.value = decode_param_value(value, parameter)
                break
        if self.tone.upper_volume.param_number == param_number and self.tone.upper_volume.block_id == block_id:
            self.tone.upper_volume.value = response[0]
            self.main_window.top_widget.redraw_upper_volume_knob_signal.emit()

    # Send message to update synth's main parameter
    def send_parameter_change_sysex(self, parameter: MainParameter):
        self.log(
            "[INFO] Param " + str(parameter.name) + ": " + str(parameter.param_number) + ", " + str(parameter.value))
        value = utils.encode_value_by_type(parameter)
        if parameter.name == "Sound A Timbre Type" or parameter.name == "Sound B Timbre Type":
            value = int(value * 2)

        try:
            if parameter.type == ParameterType.SPECIAL_ATK_REL_KNOB:
                self.midi_service.send_atk_rel_parameter_change_sysex(parameter.block_id,
                                                                      parameter.param_number, value)
            elif parameter.name in constants.SHORT_PARAMS:
                self.midi_service.send_parameter_change_short_sysex(parameter.block_id,
                                                                    parameter.param_number, value)
            else:
                self.midi_service.send_parameter_change_sysex(parameter.block_id, parameter.param_number, value)
        except Exception as e:
            self.show_error_msg(str(e))

    # Request DSP module from synth
    def request_dsp_module(self, block_id):
        try:
            self.midi_service.request_dsp_module(block_id)
        except Exception as e:
            self.show_error_msg(str(e))

    # Process DSP module from synth response
    def process_dsp_module_response(self, block_id: int, dsp_module_id: int):
        # self.lock.lockForWrite()
        self.update_tone_dsp_module_and_refresh_gui(block_id, dsp_module_id)
        self.request_dsp_module_parameters(block_id, dsp_module_id)
        # self.lock.unlock()

    # On list widget changed: update tone dsp and send module change sysex
    def update_dsp_module_from_list(self, block_id, dsp_module_id):
        self.update_tone_dsp_module_and_refresh_gui(block_id, dsp_module_id)

        try:
            if dsp_module_id is None:
                self.midi_service.send_dsp_module_change_sysex(block_id, EMPTY_DSP_MODULE_ID)
                self.midi_service.send_dsp_params_change_sysex(block_id, EMPTY_DSP_PARAMS_LIST)
                self.midi_service.send_dsp_bypass_sysex(block_id, True)
                if self.main_window.central_widget.current_dsp_page:
                    self.main_window.central_widget.current_dsp_page.redraw_dsp_params_panel_signal.emit()
            else:
                self.midi_service.send_dsp_bypass_sysex(block_id, False)
                self.midi_service.send_dsp_module_change_sysex(block_id, dsp_module_id)
                self.request_dsp_module_parameters(block_id, dsp_module_id)
        except Exception as e:
            self.show_error_msg(str(e))

    # Update tone dsp module and refresh GUI
    def update_tone_dsp_module_and_refresh_gui(self, block_id, dsp_module_id):
        dsp_module_attr, dsp_page_attr = constants.BLOCK_MAPPING[block_id]
        setattr(self.tone, dsp_module_attr, copy.deepcopy(Tone.get_dsp_module_by_id(dsp_module_id)))
        dsp_page = getattr(self.main_window.central_widget, dsp_page_attr)
        dsp_page.dsp_module = getattr(self.tone, dsp_module_attr)
        if dsp_page.dsp_module:
            self.log(f"[INFO] DSP module: {dsp_page.dsp_module.name}")
            dsp_page.dsp_module.bypass.value = 0
            self.main_window.central_widget.tab_widget.setTabIcon(block_id + 1, GuiHelper.get_green_icon())
            # self.main_window.central_widget.tab_widget.setTabText(block_id + 1, dsp_page.dsp_module.name)
        else:
            self.main_window.central_widget.tab_widget.setTabIcon(block_id + 1, GuiHelper.get_white_icon())
            # self.main_window.central_widget.tab_widget.setTabText(block_id + 1, "DSP X")

        dsp_page.list_widget.blockSignals(True)
        dsp_page.list_widget.setCurrentItem(dsp_page.get_list_item_by_dsp_id(dsp_module_id))
        dsp_page.list_widget.blockSignals(False)

        if dsp_page == self.main_window.central_widget.current_dsp_page:
            self.main_window.central_widget.update_help_text_panel_signal.emit()

    # Request DSP module parameters from synth
    def request_dsp_module_parameters(self, block_id, dsp_module_id):
        if dsp_module_id is not None:
            try:
                self.midi_service.request_dsp_params(block_id)
            except Exception as e:
                self.show_error_msg(str(e))

    # Process DSP module parameters from synth response
    def process_dsp_module_parameters_response(self, block_id, synth_dsp_params):
        dsp_module_attr, dsp_page_attr = constants.BLOCK_MAPPING[block_id]
        dsp_module = getattr(self.tone, dsp_module_attr)
        if dsp_module is not None:
            for idx, dsp_param in enumerate(dsp_module.dsp_parameter_list):
                if dsp_param.type == ParameterType.SPECIAL_DELAY_KNOB:
                    dsp_param.value = int(str(synth_dsp_params[12]) + str(synth_dsp_params[13]))
                else:
                    dsp_param.value = decode_param_value(synth_dsp_params[idx], dsp_param)

        if self.main_window.central_widget.current_dsp_page:
            self.main_window.central_widget.current_dsp_page.redraw_dsp_params_panel_signal.emit()

    def request_upper_volume(self):
        try:
            self.midi_service.request_parameter_value(self.tone.upper_volume.block_id,
                                                      self.tone.upper_volume.param_number)
        except Exception as e:
            self.show_error_msg(str(e))

    # Send message to update synth's DSP parameters
    def set_synth_dsp_params(self, _):
        try:
            dsp_page = self.main_window.central_widget.current_dsp_page
            if dsp_page:
                self.midi_service.send_dsp_params_change_sysex(dsp_page.block_id, dsp_page.get_dsp_params_as_list())
        except Exception as e:
            self.show_error_msg(str(e))

    def send_dsp_bypass(self, block_id, bypass):
        try:
            self.midi_service.send_dsp_bypass_sysex(block_id, bypass)
        except Exception as e:
            self.show_error_msg(str(e))

    # Send program change message
    def change_instrument_by_id_from_list(self, instrument_id):
        instrument = Tone.get_instrument_by_id(instrument_id)
        self.tone.name = instrument.name
        self.tone.parent_tone = instrument
        self.log("[INFO] Instrument id: " + str(instrument_id) + " " + self.tone.parent_tone.name)
        try:
            self.midi_service.send_change_tone_msg(self.tone.parent_tone)
        except Exception as e:
            self.show_error_msg(str(e))

    # Intercept instrument change messages from synth
    def process_instrument_select_response(self, bank, program):
        # self.lock.lockForWrite()
        self.main_window.central_widget.instrument_list.blockSignals(True)
        self.log("[INFO] Instrument: " + str(bank) + ", " + str(program))
        self.find_instrument_and_update_tone(bank, program)

        tone_id_and_name = self.get_tone_id_and_name()
        self.main_window.top_widget.tone_name_label.setText(tone_id_and_name)
        self.main_window.central_widget.instrument_list.blockSignals(False)
        # self.lock.unlock()

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
                self.main_window.central_widget.instrument_list.setCurrentRow(self.tone.parent_tone.id - 1)
                break
        if not is_found:
            self.tone.name = DEFAULT_TONE_NAME
            self.tone.parent_tone = None
            self.main_window.central_widget.instrument_list.clearSelection()

    def countdown_and_autosynchronize(self, timeout):
        # self.lock.lockForWrite()
        is_active = self.timeout > 0
        # self.lock.unlock()

        if is_active:
            # worker exists: reset timer and exit
            # self.lock.lockForWrite()
            self.timeout = timeout
            # self.lock.unlock()
        else:
            # start countdown
            # self.lock.lockForWrite()
            self.timeout = timeout
            # self.lock.unlock()
            while True:
                # self.lock.lockForWrite()
                is_active = self.timeout > 0
                # self.lock.unlock()

                if is_active:
                    # self.lock.lockForWrite()
                    text = "Autosynchronize countdown: " + str(self.timeout)
                    self.status_msg_signal.emit(text, 1000)
                    self.timeout = self.timeout - 1
                    # self.lock.unlock()
                    time.sleep(1)
                else:
                    break

            # self.lock.lockForWrite()
            # self.main_window.loading_animation.start()
            self.synchronize_tone_signal.emit()
            # self.lock.unlock()

    # Open midi ports
    def open_midi_ports(self):
        # self.lock.lockForWrite()
        self.midi_service.open_midi_ports()
        # self.lock.unlock()

    # Close midi ports
    def close_midi_ports(self):
        # self.lock.lockForWrite()
        self.midi_service.close_midi_ports()
        # self.lock.unlock()

    # Load Tone from JSON
    def load_tone_from_json(self, json_tone: dict):
        def _get_block_id(dsp_id):
            block_id_mapping = {
                "dsp_1": 0,
                "dsp_2": 1,
                "dsp_3": 2,
                "dsp_4": 3
            }
            return block_id_mapping.get(dsp_id)

        # Name
        if "name" in json_tone:
            self.tone.name = json_tone["name"]
            self.main_window.top_widget.tone_name_label.setText(self.tone.name)

        # Parent tone
        self.tone.parent_tone = None
        json_id = json_tone["id"] if "id" in json_tone else None
        json_synthesizer_model = json_tone["synthesizer_model"] if "synthesizer_model" in json_tone else None
        json_bank = None
        json_program = None
        modal_window_message = ""
        json_parent_tone = json_tone.get("parent_tone")
        if json_parent_tone:
            json_bank = json_parent_tone.get("bank")
            json_program = json_parent_tone.get("program")
            if json_bank is not None and json_program is not None:
                self.find_instrument_and_update_tone(json_bank, json_program)
                if self.tone.parent_tone is not None:
                    modal_window_message = "Please, use your " + self.tone.synthesizer_model \
                                           + " synthesizer controls to manually select the parent tone:<h2>" \
                                           + str(self.tone.parent_tone.id) + " " + str(self.tone.parent_tone.name) \
                                           + "</h2><h5>(bank: " + str(self.tone.parent_tone.bank) \
                                           + ", program: " + str(self.tone.parent_tone.program) \
                                           + ")</h5>Then, press the 'Continue' button to apply the parameter changes from the JSON file."

        if self.tone.parent_tone is None:
            json_synthesizer_model_str = "unknown synthesizer model" if json_synthesizer_model is None else str(
                json_synthesizer_model)
            id_str = "" if json_id is None else str(json_id) + " "
            tone_name_str = "?????" if self.tone.name is None else self.tone.name
            json_bank_str = "unknown" if json_bank is None else str(json_bank)
            json_program_str = "unknown" if json_program is None else str(json_program)
            modal_window_message = "The parent tone (from " + json_synthesizer_model_str + " model) is unknown:<h2>" \
                                   + id_str + tone_name_str \
                                   + "</h2><h5>(bank: " + json_bank_str + ", program: " + json_program_str \
                                   + ")</h5>You can select any other source tone using your synthesizer controls.<br/>" \
                                   + "Then, press the 'Continue' button to apply the parameter changes from the JSON file."

        self.show_status_msg(
            "Manual tone selection is necessary because selecting the UPPER Tone is not possible via SysEx messages.",
            0)
        modal_window = ChangeInstrumentWindow(modal_window_message)
        modal_window.exec_()
        self.show_status_msg("", 0)

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
                block_id = _get_block_id(json_dsp_id)
                if block_id is not None and json_dsp_module is not None and "name" in json_dsp_module:
                    self._load_dsp_from_json(block_id, json_dsp_module)

    def _load_dsp_from_json(self, block_id, json_dsp_module):
        dsp_module = next(
            (dsp_module for dsp_module in constants.ALL_DSP_MODULES if
             dsp_module.name == json_dsp_module["name"]), None)
        if dsp_module:
            dsp_module_id = dsp_module.id
            self.update_tone_dsp_module_and_refresh_gui(block_id, dsp_module_id)
            try:
                if dsp_module_id is None:
                    self.midi_service.send_dsp_bypass_sysex(block_id, True)
                    if self.main_window.central_widget.current_dsp_page:
                        self.main_window.central_widget.current_dsp_page.redraw_dsp_params_panel_signal.emit()
                else:
                    self.midi_service.send_dsp_bypass_sysex(block_id, False)
                    self.midi_service.send_dsp_module_change_sysex(block_id, dsp_module_id)
            except Exception as e:
                self.show_error_msg(str(e))

            dsp_module_attr, dsp_page_attr = constants.BLOCK_MAPPING[block_id]
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

                time.sleep(0.5)
                try:
                    self.midi_service.send_dsp_params_change_sysex(block_id,
                                                                   dsp_page.get_dsp_params_as_list())
                except Exception as e:
                    self.show_error_msg(str(e))

                if self.main_window.central_widget.current_dsp_page:
                    self.main_window.central_widget.current_dsp_page.redraw_dsp_params_panel_signal.emit()

    def send_custom_midi_msg(self, midi_msg: str):
        self.midi_service.send_custom_midi_msg(midi_msg)

    def request_custom_parameter(self, number: int, block_id: int, category: int, memory: int, parameter_set: int,
                                 size: int):
        self.midi_service.request_parameter_value_full(block_id, number, category, memory, parameter_set, size)

    @Slot()
    def show_status_msg(self, text: str, msecs: int):
        self.status_bar.setStyleSheet("background-color: white; color: black")
        self.status_bar.showMessage(text, msecs)

    def show_error_msg(self, text: str):
        self.log("[ERROR] " + text)
        self.status_bar.setStyleSheet("background-color: white; color: red")
        self.status_bar.showMessage(text, 5000)

        self.main_window.loading_animation.stop()

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

    def upload_tone(self, tone_number, tone_name):
        if not tone_name:
            tone_name = DEFAULT_TONE_NAME

        current_tone = self.tyrant_midi_service.read_current_tone(tone_name[:8])

        self.tyrant_midi_service.bulk_upload(tone_number - 801, current_tone, memory=1, category=3)
        self.close_midi_ports()
        self.open_midi_ports()

        # self.synchronize_tone_signal.emit()
        self.status_msg_signal.emit("Tone successfully saved!", 3000)
        self.main_window.loading_animation.stop()

    def start_tone_rename_worker(self, tone_number, new_name):
        if tone_number < 801 or tone_number > 900:
            raise Exception("The 'Tone Number' must be in the range of 801 to 900.")

        self.main_window.loading_animation.start()
        self.status_msg_signal.emit("Renaming... Please wait!", 10000)
        self.log(f"[INFO] Renaming tone number: {tone_number}")

        worker = Worker(self.rename_tone, tone_number, new_name)
        worker.signals.error.connect(lambda error: self.show_error_msg(str(error[1])))
        worker.start()

    def rename_tone(self, tone_number, new_name):
        tone_data = self.tyrant_midi_service.bulk_download(tone_number - 801, memory=1, category=3)

        if new_name:
            tone_data = bytearray(tone_data)  # Convert the tone data to a mutable bytearray
            new_tone_name_bytes = new_name.encode('utf-8')
            tone_data[0x1A6:0x1B6] = new_tone_name_bytes.ljust(16, b' ')
            tone_data[0x1A6 + 8] = 0x00

        self.tyrant_midi_service.bulk_upload(tone_number - 801, tone_data, memory=1, category=3)
        self.close_midi_ports()
        self.open_midi_ports()

        self.synchronize_tone_signal.emit()
        self.status_msg_signal.emit("Tone successfully renamed!", 3000)
        self.main_window.loading_animation.stop()

    def start_tone_delete_worker(self, tone_number):
        if tone_number < 801 or tone_number > 900:
            raise Exception("The 'Tone Number' must be in the range of 801 to 900.")

        self.main_window.loading_animation.start()
        self.status_msg_signal.emit("Deleting... Please wait!", 10000)
        self.log(f"[INFO] Deleting tone number: {tone_number}")

        worker = Worker(self.delete_tone, tone_number)
        worker.signals.error.connect(lambda error: self.show_error_msg(str(error[1])))
        worker.start()

    def delete_tone(self, tone_number):
        self.tyrant_midi_service.bulk_upload(tone_number - 801, EMPTY_TONE, memory=1, category=3)
        self.close_midi_ports()
        self.open_midi_ports()

        self.synchronize_tone_signal.emit()
        self.status_msg_signal.emit("Tone successfully deleted!", 3000)
        self.main_window.loading_animation.stop()

    def request_user_memory_tone_names(self):
        for i in range(0, 100):
            self.request_user_memory_tone_name(i)

    def request_user_memory_tone_name(self, tone_number):
        self.midi_service.request_parameter_value_full(0, 0, 3, 1, tone_number, 12)

    def process_user_memory_tone_name_response(self, response):
        tone_name = ''.join(chr(i) for i in response if chr(i).isprintable()).strip()
        # print(f"Tone name: {tone_name}")
