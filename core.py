import copy
import time

from PySide2.QtCore import QReadWriteLock, Signal, Slot, QObject, QThreadPool

from constants import constants
from constants.enums import ParameterType
from external.worker import Worker
from model.parameter import MainParameter
from model.tone import Tone
from services.midi_service import MidiService
from utils import utils
from utils.utils import decode_param_value, decimal_to_hex, hex_hex_to_decimal


# Class for managing tone state and handling all communication between GUI and Midi Service
# NB! Use int values as its method parameters, all required byte/hex conversions make in the Midi Service!
class Core(QObject):
    synchronize_tone_signal = Signal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.tone: Tone = Tone()
        self.midi_service = MidiService.get_instance()
        self.midi_service.core = self
        self.lock = QReadWriteLock()
        self.timeout = 0
        self.synchronize_tone_signal.connect(self.synchronize_tone_with_synth)

    # Synchronize all Tone data: name, main params, DSP modules and their params
    @Slot()
    def synchronize_tone_with_synth(self):
        self.lock.lockForWrite()
        print("\tSynchronizing tone!")
        self.midi_service.active_sync_job_count = 0
        # self.tone = Tone()  # if enabled, then tone is initialized twice during the application startup

        self.request_tone_name()
        self.request_main_parameters()
        self.request_dsp_module(0)
        self.request_dsp_module(1)
        self.request_dsp_module(2)
        self.request_dsp_module(3)

        self.main_window.central_widget.on_tab_changed(0)  # updates help tab and JSON (if JSON-tab opened)
        self.lock.unlock()

        QThreadPool().start(Worker(self.update_main_params_page))

    def update_main_params_page(self):
        for i in range(0, 10):
            self.lock.lockForWrite()
            if self.midi_service.active_sync_job_count == 0:
                self.lock.unlock()
                self.main_window.central_widget.redraw_main_params_panel_signal.emit()
                break
            self.lock.unlock()
            time.sleep(0.5)

    # Request tone name from synth
    def request_tone_name(self):
        try:
            self.midi_service.request_tone_name()
        except Exception as e:
            self.main_window.show_error_msg(str(e))

    # Process tone name from synth response
    def process_tone_name_response(self, response):
        self.lock.lockForWrite()
        tone_name = ''.join(chr(i) for i in response if chr(i).isprintable()).strip()
        print("\tSynth tone name: " + tone_name)
        if self.tone.parent_tone and tone_name:
            self.tone.name = f"{self.tone.parent_tone.id} {tone_name}"
        elif self.tone.parent_tone is None and tone_name:
            self.tone.name = tone_name
        elif self.tone.name is None:
            self.tone.name = constants.DEFAULT_TONE_NAME

        self.main_window.top_widget.tone_name_label.setText(self.tone.name)
        self.lock.unlock()

    # Request main parameter value from synth
    def request_main_parameters(self):
        for parameter in self.tone.main_parameter_list:
            print("\tRequesting parameter: " + parameter.name)
            try:
                self.midi_service.request_parameter_value(parameter.block_id, parameter.action_number)
            except Exception as e:
                self.main_window.show_error_msg(str(e))

    # Process main parameter value response
    def process_main_parameter_response(self, param_number, block_id, response):
        for parameter in self.tone.main_parameter_list:
            if parameter.action_number == param_number and parameter.block_id == block_id:
                print("\tProcessing parameter: " + parameter.name + ", " + str(param_number) + ", "
                      + str(block_id) + ", " + str(response))
                if parameter.type == ParameterType.SPECIAL_ATK_REL_KNOB:
                    value = int(decimal_to_hex(response[1]) + decimal_to_hex(response[0]), 16)
                elif len(response) == 1:
                    value = response[0]
                else:
                    value = hex_hex_to_decimal(response[0], response[1])
                parameter.value = decode_param_value(value, parameter)
                break

    # Send message to update synth's main parameter
    def send_parameter_change_sysex(self, parameter: MainParameter):
        print("\tParam " + str(parameter.name) + ": " + str(parameter.action_number) + ", " + str(parameter.value))
        value = utils.encode_value_by_type(parameter)
        try:
            if parameter.type == ParameterType.SPECIAL_ATK_REL_KNOB:
                self.midi_service.send_atk_rel_parameter_change_sysex(parameter.block_id,
                                                                      parameter.action_number, value)
            elif parameter.name in constants.SHORT_PARAMS:
                self.midi_service.send_parameter_change_short_sysex(parameter.block_id,
                                                                    parameter.action_number, value)
            else:
                self.midi_service.send_parameter_change_sysex(parameter.block_id, parameter.action_number, value)
        except Exception as e:
            self.main_window.show_error_msg(str(e))

    # Request DSP module from synth
    def request_dsp_module(self, block_id):
        try:
            self.midi_service.request_dsp_module(block_id)
        except Exception as e:
            self.main_window.show_error_msg(str(e))

    # Process DSP module from synth response
    def process_dsp_module_response(self, block_id: int, dsp_module_id: int):
        self.lock.lockForWrite()
        self.update_tone_dsp_module_and_refresh_gui(block_id, dsp_module_id)
        self.request_dsp_module_parameters(block_id, dsp_module_id)
        self.lock.unlock()

    # On list widget changed: update tone dsp and send module change sysex
    def update_dsp_module_from_list(self, block_id, dsp_module_id):
        self.update_tone_dsp_module_and_refresh_gui(block_id, dsp_module_id)

        if dsp_module_id is None:
            # TODO: turn DSP off
            self.main_window.show_status_msg("Not implemented!!", 1000)
        else:
            try:
                self.midi_service.send_dsp_module_change_sysex(block_id, dsp_module_id)
                self.request_dsp_module_parameters(block_id, dsp_module_id)
            except Exception as e:
                self.main_window.show_error_msg(str(e))

    # Update tone dsp module and refresh GUI
    def update_tone_dsp_module_and_refresh_gui(self, block_id, dsp_module_id):
        dsp_module_attr, dsp_page_attr = constants.BLOCK_MAPPING[block_id]
        setattr(self.tone, dsp_module_attr, copy.deepcopy(Tone.get_dsp_module_by_id(dsp_module_id)))
        dsp_page = getattr(self.main_window.central_widget, dsp_page_attr)
        dsp_page.dsp_module = getattr(self.tone, dsp_module_attr)

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
                self.main_window.show_error_msg(str(e))

    # Process DSP module parameters from synth response
    def process_dsp_module_parameters_response(self, block_id, synth_dsp_params):
        dsp_module_attr, dsp_page_attr = constants.BLOCK_MAPPING[block_id]
        dsp_module = getattr(self.tone, dsp_module_attr)
        if dsp_module is not None:
            for idx, dsp_param in enumerate(dsp_module.dsp_parameter_list):
                print("\tParam before: " + str(synth_dsp_params[idx]) +
                      ", after: " + str(decode_param_value(synth_dsp_params[idx], dsp_param)))
                dsp_param.value = decode_param_value(synth_dsp_params[idx], dsp_param)

        if self.main_window.central_widget.current_dsp_page:
            self.main_window.central_widget.current_dsp_page.redraw_dsp_params_panel_signal.emit()

    # Send message to update synth's DSP parameters
    def set_synth_dsp_params(self, _):
        try:
            dsp_page = self.main_window.central_widget.current_dsp_page
            self.midi_service.send_dsp_params_change_sysex(dsp_page.block_id, dsp_page.get_dsp_params_as_list())
        except Exception as e:
            self.main_window.show_error_msg(str(e))

    # Send program change message
    def change_instrument_by_id_from_list(self, instrument_id):
        instrument = Tone.get_instrument_by_id(instrument_id)
        self.tone.name = instrument.name  # TODO: read from synth
        self.tone.parent_tone = instrument
        print("\tInstrument id: " + str(instrument_id) + " " + self.tone.parent_tone.name)
        try:
            self.midi_service.send_change_tone_msg(self.tone.parent_tone)
        except Exception as e:
            self.main_window.show_error_msg(str(e))

    # Intercept instrument change messages from synth
    def process_instrument_select_response(self, bank, program_change):
        self.lock.lockForWrite()
        self.main_window.central_widget.instrument_list.blockSignals(True)
        print("\tInstrument: " + str(bank) + ", " + str(program_change))
        is_found = False
        for instrument in constants.ALL_INSTRUMENTS_3000_5000:
            if instrument.bank == bank and instrument.program_change == program_change:
                is_found = True
                self.tone.name = "{:03}".format(instrument.id) + " " + instrument.name
                self.tone.parent_tone = instrument
                self.main_window.central_widget.instrument_list.setCurrentRow(self.tone.parent_tone.id - 1)
                break

        if not is_found:
            self.tone.name = "Unknown Tone"
            self.tone.parent_tone = None
            self.main_window.central_widget.instrument_list.clearSelection()

        self.main_window.top_widget.tone_name_label.setText(self.tone.name)
        self.main_window.central_widget.instrument_list.blockSignals(False)
        self.lock.unlock()

    def countdown_and_autosynchronize(self, timeout):
        self.lock.lockForWrite()
        is_active = self.timeout > 0
        self.lock.unlock()

        if is_active:
            # worker exists: reset timer and exit
            self.lock.lockForWrite()
            self.timeout = timeout
            self.lock.unlock()
        else:
            # start countdown
            self.lock.lockForWrite()
            self.timeout = timeout
            self.lock.unlock()
            while True:
                self.lock.lockForWrite()
                is_active = self.timeout > 0
                self.lock.unlock()

                if is_active:
                    self.lock.lockForWrite()
                    text = "Autosynchronize countdown: " + str(self.timeout)
                    print(text)
                    self.main_window.status_msg_signal.emit(text, 1000)
                    self.timeout = self.timeout - 1
                    self.lock.unlock()
                    time.sleep(1)
                else:
                    break

            self.lock.lockForWrite()
            self.synchronize_tone_signal.emit()
            self.lock.unlock()

    # Close midi ports
    def close_midi_ports(self):
        self.midi_service.close_midi_ports()

    def load_tone_from_json(self, json_tone: dict):
        if "name" in json_tone:
            self.tone.name = json_tone["name"]
            self.main_window.top_widget.tone_name_label.setText(self.tone.name)
        if "parent_tone" in json_tone:
            if json_tone["parent_tone"] is None:
                self.tone.parent_tone = None
            else:
                pass  # FIXME
        if "parameters" in json_tone:
            for json_main_parameter in json_tone["parameters"]:
                if "name" in json_main_parameter and "value" in json_main_parameter:
                    for tone_main_parameter in self.tone.main_parameter_list:
                        if tone_main_parameter.name == json_main_parameter["name"]:
                            print("Setting: " + json_main_parameter["name"])
                            if tone_main_parameter.type == ParameterType.COMBO:
                                tone_main_parameter.value = json_main_parameter["value"] - 1
                            else:
                                tone_main_parameter.value = json_main_parameter["value"]
                            self.send_parameter_change_sysex(tone_main_parameter)
                            break
            self.main_window.central_widget.redraw_main_params_panel_signal.emit()

        if "dsp_modules" in json_tone:
            for dsp_data in json_tone["dsp_modules"].items():
                block_id = None
                if dsp_data[0] == "dsp_1":
                    block_id = 0
                elif dsp_data[0] == "dsp_2":
                    block_id = 1
                elif dsp_data[0] == "dsp_3":
                    block_id = 2
                elif dsp_data[0] == "dsp_4":
                    block_id = 3

                if block_id is not None and dsp_data[1] is not None:
                    print(dsp_data[0])
                    json_dsp_module = dsp_data[1]
                    if "name" in json_dsp_module:
                        print(json_dsp_module["name"])

                        dsp_module_id = None
                        for dsp_module in constants.ALL_DSP_MODULES:
                            if dsp_module.name == json_dsp_module["name"]:
                                print("Setting: " + json_dsp_module["name"])
                                dsp_module_id = dsp_module.id
                                break

                        if block_id is not None and dsp_module_id is not None:
                            self.update_tone_dsp_module_and_refresh_gui(block_id, dsp_module_id)

                            dsp_module_attr, dsp_page_attr = constants.BLOCK_MAPPING[block_id]
                            dsp_page = getattr(self.main_window.central_widget, dsp_page_attr)
                            dsp_page.dsp_module = getattr(self.tone, dsp_module_attr)

                            if "parameters" in json_dsp_module:
                                for json_dsp_parameter in json_dsp_module["parameters"]:
                                    if "name" in json_dsp_parameter and "value" in json_dsp_parameter:
                                        for tone_parameter in dsp_page.dsp_module.dsp_parameter_list:
                                            if tone_parameter.name == json_dsp_parameter["name"]:
                                                print("Setting2: " + json_dsp_parameter["name"])
                                                if tone_parameter.type == ParameterType.COMBO:
                                                    tone_parameter.value = json_dsp_parameter["value"] - 1
                                                else:
                                                    tone_parameter.value = json_dsp_parameter["value"]
                                                break

                                try:
                                    self.midi_service.send_dsp_params_change_sysex(block_id,
                                                                                   dsp_page.get_dsp_params_as_list())
                                except Exception as e:
                                    self.main_window.show_error_msg(str(e))

                                if self.main_window.central_widget.current_dsp_page:
                                    self.main_window.central_widget.current_dsp_page.redraw_dsp_params_panel_signal.emit()
