import copy

from constants.enums import ParameterType
from model.dsp_parameter import DspParameter
from model.tone import Tone
from services.midi_service import MidiService


# Class for managing tone state and handling all communication with the Midi Service
class Core:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tone: Tone = Tone()
        self.midi_service = MidiService.get_instance()
        self.midi_service.core = self

    def synchronize_tone_with_synth(self):
        print("Synchronizing tone!")
        self.tone = Tone()  # TODO: fix -> tone is initialized twice during the application startup

        try:
            self.midi_service.request_tone_name()
        except Exception as e:
            self.main_window.show_error_msg(str(e))

        # self.reload_dsp_page(self.main_window.central_widget.dsp_page_1)
        # self.reload_dsp_page(self.main_window.central_widget.dsp_page_2)
        # self.reload_dsp_page(self.main_window.central_widget.dsp_page_3)
        # self.reload_dsp_page(self.main_window.central_widget.dsp_page_4)
        self.main_window.central_widget.on_tab_changed(0)

    # def reload_dsp_page(self, dsp_page):
    #     self.midi_request_dsp_module_by_block_id(None)
    #     if dsp_page.dsp_module is not None:
    #         dsp_page.list_widget.setCurrentItem(dsp_page.get_list_item_by_dsp_id(dsp_page.dsp_module.id))

    def update_tone_name(self, response):
        tone_name = ''.join(chr(i) for i in response if chr(i).isprintable())
        print("Synth tone name: " + tone_name)
        if tone_name is not None and len(tone_name.strip()) > 0:
            self.tone.name = tone_name
        else:
            self.tone.name = "Unknown Tone"
        self.main_window.top_widget.tone_name_label.setText(self.tone.name)

    def change_instrument_by_id(self, instrument_id):
        instrument = Tone.get_instrument_by_id(instrument_id)
        self.tone.name = instrument.name  # TODO: read from synth
        self.tone.base_tone = instrument
        print("Instrument id: " + str(instrument_id) + " " + self.tone.base_tone.name)
        try:
            self.midi_service.send_change_tone_msg(self.tone.base_tone)
        except Exception as e:
            self.main_window.show_error_msg(str(e))

    def update_tone_dsp_modules(self, response):
        print("update_tone_dsp_modules........... find block id & dsp id")

    def request_dsp_module_by_block_id(self, block_id):
        try:
            self.midi_service.request_dsp_module(block_id)
        except Exception as e:
            self.main_window.show_error_msg(str(e))

    def process_dsp_module_by_block_id_response(self, response):
        if response is not None and len(response) > 0:
            block_id = 0  # FIXME
            dsp_module_id = response[0]
            # self.update_dsp_module(block_id, dsp_module_id) # FIXME

    def update_dsp_module(self, block_id, dsp_module_id):
        if block_id == 0:
            self.tone.dsp_module_1 = copy.deepcopy(Tone.get_dsp_module_by_id(dsp_module_id))
            self.main_window.central_widget.dsp_page_1.dsp_module = self.tone.dsp_module_1
        elif block_id == 1:
            self.tone.dsp_module_2 = copy.deepcopy(Tone.get_dsp_module_by_id(dsp_module_id))
            self.main_window.central_widget.dsp_page_2.dsp_module = self.tone.dsp_module_2
        elif block_id == 2:
            self.tone.dsp_module_3 = copy.deepcopy(Tone.get_dsp_module_by_id(dsp_module_id))
            self.main_window.central_widget.dsp_page_1.dsp_module = self.tone.dsp_module_3
        elif block_id == 3:
            self.tone.dsp_module_4 = copy.deepcopy(Tone.get_dsp_module_by_id(dsp_module_id))
            self.main_window.central_widget.dsp_page_1.dsp_module = self.tone.dsp_module_4

        if dsp_module_id is None:
            # TODO: turn DSP off
            self.main_window.show_status_msg("Not implemented!!", 1000)
        else:
            try:
                self.midi_service.send_dsp_module_change_sysex(dsp_module_id, block_id)
            except Exception as e:
                self.main_window.show_error_msg(str(e))

        self.midi_get_synth_dsp_params(block_id)
        self.main_window.central_widget.current_dsp_page.redraw_dsp_params_panel()  # TODO: current or by block name?
        self.main_window.central_widget.update_help_text_panel()

    @staticmethod
    def decode_param_value(value: int, dsp_param: DspParameter):
        if dsp_param.type == ParameterType.KNOB:
            if dsp_param.choices[0] == 0:
                return value
            elif dsp_param.choices[0] == -64:
                return value - 64
        # TODO
        # elif parameter.type == ParameterType.KNOB_2BYTES:
        #     return value
        return value

    def midi_get_synth_dsp_params(self, block_id):
        pass
        # if self.dsp_module is not None:
        #     try:
        #         synth_dsp_params = self.midi_service.request_dsp_params(block_id)
        #         for idx, dsp_param in enumerate(self.dsp_module.dsp_parameter_list):
        #             print("Param before: " + str(synth_dsp_params[idx]) + ", after: " + str(
        #                 self.decode_param_value(synth_dsp_params[idx], dsp_param)))
        #             dsp_param.value = self.decode_param_value(synth_dsp_params[idx], dsp_param)
        #     except Exception as e:
        #         self.main_window.show_error_msg(str(e))
        #
        #     current_row = self.get_list_item_by_dsp_id(self.dsp_module.id)
        #     self.list_widget.setCurrentItem(current_row)

    def midi_set_synth_dsp_params(self):
        try:
            dsp_page = self.main_window.central_widget.current_dsp_page
            self.midi_service.send_dsp_params_change_sysex(dsp_page.get_dsp_params_as_list(), dsp_page.block_id)
        except Exception as e:
            self.main_window.show_error_msg(str(e))

    def close_midi_ports(self):
        self.midi_service.close_midi_ports()
