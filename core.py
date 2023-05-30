import copy
import time

from PySide2.QtCore import QReadWriteLock, Signal, Slot, QObject

from constants import constants
from model.tone import Tone
from services.midi_service import MidiService
from utils.utils import decode_param_value


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
        print("Synchronizing tone!")
        # self.main_window.status_msg_signal.emit("Synchronizing tone...", 1000)
        # self.tone = Tone()  # if enabled, then tone is initialized twice during the application startup

        self.request_tone_name()
        self.request_dsp_module(0)
        self.request_dsp_module(1)
        self.request_dsp_module(2)
        self.request_dsp_module(3)

        self.main_window.central_widget.on_tab_changed(0)  # updates help tab and JSON (if JSON-tab opened)
        self.lock.unlock()

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
        if self.tone.base_tone and tone_name:
            self.tone.name = f"{self.tone.base_tone.id} {tone_name}"
        elif self.tone.base_tone is None and tone_name:
            self.tone.name = tone_name
        elif self.tone.name is None:
            self.tone.name = constants.DEFAULT_TONE_NAME

        self.main_window.top_widget.tone_name_label.setText(self.tone.name)
        self.lock.unlock()

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
        print("request_dsp_module_parameters...")
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
                print("Param before: " + str(synth_dsp_params[idx]) +
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
        self.tone.base_tone = instrument
        print("Instrument id: " + str(instrument_id) + " " + self.tone.base_tone.name)
        try:
            self.midi_service.send_change_tone_msg(self.tone.base_tone)
        except Exception as e:
            self.main_window.show_error_msg(str(e))

    # Intercept instrument change messages from synth
    def process_instrument_select_response(self, bank, program_change):
        self.lock.lockForWrite()
        print("\tInstrument: " + str(bank) + ", " + str(program_change))
        self.tone.name = "Unknown Tone"
        for instrument in constants.ALL_INSTRUMENTS:
            if instrument.bank == bank and instrument.program_change == program_change:
                self.tone.name = "{:03}".format(instrument.id) + " " + instrument.name
                self.tone.base_tone = instrument
                break
        self.main_window.top_widget.tone_name_label.setText(self.tone.name)
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

    def send_parameter_change_sysex(self, block_id, action_number, value):
        try:
            self.midi_service.send_parameter_change_sysex(block_id, action_number, value)
        except Exception as e:
            self.main_window.show_error_msg(str(e))
