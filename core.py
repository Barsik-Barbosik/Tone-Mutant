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

    # Synchronize all Tone data: name, main params, DSP modules and their params
    def synchronize_tone_with_synth(self):
        print("Synchronizing tone!")
        self.tone = Tone()  # TODO: fix -> tone is initialized twice during the application startup

        self.request_tone_name()
        self.request_dsp_module_by_block_id(0)
        self.request_dsp_module_by_block_id(1)
        self.request_dsp_module_by_block_id(2)
        self.request_dsp_module_by_block_id(3)

        self.main_window.central_widget.on_tab_changed(0)

    # Request tone name from synth
    def request_tone_name(self):
        try:
            self.midi_service.request_tone_name()
        except Exception as e:
            self.main_window.show_error_msg(str(e))

    # Process tone name from synth response
    def process_tone_name_response(self, response):
        tone_name = ''.join(chr(i) for i in response if chr(i).isprintable())
        print("Synth tone name: " + tone_name)
        if tone_name is not None and len(tone_name.strip()) > 0:
            self.tone.name = tone_name
        else:
            self.tone.name = "Unknown Tone"
        self.main_window.top_widget.tone_name_label.setText(self.tone.name)

    # Request DSP module from synth
    def request_dsp_module_by_block_id(self, block_id):
        try:
            self.midi_service.request_dsp_module(block_id)
        except Exception as e:
            self.main_window.show_error_msg(str(e))

    # Process DSP module from synth response
    def process_dsp_module_by_block_id_response(self, response):
        if response is not None and len(response) > 0:
            block_id = 0  # FIXME
            dsp_module_id = response[0]
            # self.update_dsp_module(block_id, dsp_module_id)

    def update_dsp_module_from_list(self, block_id, dsp_module_id):
        if block_id == 0:
            self.tone.dsp_module_1 = copy.deepcopy(Tone.get_dsp_module_by_id(dsp_module_id))
            dsp_page = self.main_window.central_widget.dsp_page_1
            dsp_page.dsp_module = self.tone.dsp_module_1
            dsp_page.list_widget.setCurrentItem(dsp_page.get_list_item_by_dsp_id(dsp_module_id))
        elif block_id == 1:
            self.tone.dsp_module_2 = copy.deepcopy(Tone.get_dsp_module_by_id(dsp_module_id))
            dsp_page = self.main_window.central_widget.dsp_page_2
            dsp_page.dsp_module = self.tone.dsp_module_2
            dsp_page.list_widget.setCurrentItem(dsp_page.get_list_item_by_dsp_id(dsp_module_id))
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
                self.midi_service.send_dsp_module_change_sysex(block_id, dsp_module_id)
            except Exception as e:
                self.main_window.show_error_msg(str(e))

        # Update DSP module parameters
        self.request_dsp_module_parameters(block_id)
        self.main_window.central_widget.current_dsp_page.redraw_dsp_params_panel()  # TODO: by block_id
        self.main_window.central_widget.update_help_text_panel()

    # Request DSP module parameters from synth
    def request_dsp_module_parameters(self, block_id):
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

    # Process DSP module parameters from synth response
    def request_dsp_module_parameters_response(self, response):
        pass

    # TODO: move to DspParameter class
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

    # Send message to update synth's DSP parameters
    def set_synth_dsp_params(self):
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

    def close_midi_ports(self):
        self.midi_service.close_midi_ports()
