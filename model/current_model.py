import json

from enums.enums import ParameterType, TabName
from external.object_encoder.object_encoder import ObjectEncoder
from model.dsp_module import DspModule
from model.tone import Tone

EMPTY_DSP_NAME = "OFF"


class CurrentModel:
    def __init__(self):
        self.tone: Tone = Tone()

        self.current_block_id: int = None
        self.current_dsp_module: DspModule = None
        self.current_dsp_name: str = None

        self.update_current_model(None, TabName.MAIN_PARAMETERS)

    def update_current_block_id(self, current_tab_name: TabName):
        if current_tab_name == TabName.DSP_1:
            self.current_block_id = 0
        elif current_tab_name == TabName.DSP_2:
            self.current_block_id = 1
        elif current_tab_name == TabName.DSP_3:
            self.current_block_id = 2
        elif current_tab_name == TabName.DSP_4:
            self.current_block_id = 3

    def update_current_model(self, dsp_id: int, current_tab_name: TabName):
        self.current_dsp_module = DspModule.get_dsp_module_by_id(dsp_id)
        self.current_dsp_name = self.current_dsp_module.name if self.current_dsp_module is not None else EMPTY_DSP_NAME

        if current_tab_name == TabName.DSP_1:
            self.current_block_id = 0
            self.tone.dsp_module_1 = self.current_dsp_module
        elif current_tab_name == TabName.DSP_2:
            self.current_block_id = 1
            self.tone.dsp_module_2 = self.current_dsp_module
        elif current_tab_name == TabName.DSP_3:
            self.current_block_id = 2
            self.tone.dsp_module_3 = self.current_dsp_module
        elif current_tab_name == TabName.DSP_4:
            self.current_block_id = 3
            self.tone.dsp_module_4 = self.current_dsp_module

    def get_current_tone_as_json(self) -> str:
        return json.dumps(self.tone, cls=ObjectEncoder, indent=4)

    def get_current_dsp_params_as_list(self) -> list:
        output = [0] * 14
        if self.current_dsp_module is not None:
            for idx, parameter in enumerate(self.current_dsp_module.dsp_parameter_list):
                if parameter.type == ParameterType.COMBO:
                    output[idx] = parameter.value
                elif parameter.type == ParameterType.KNOB:
                    output[idx] = parameter.value if parameter.choices[0] == 0 else parameter.value + 64
                elif parameter.type == ParameterType.KNOB_2BYTES:
                    # special case, only for the "delay" DSP module
                    output[12] = int(str(parameter.value).zfill(4)[:2])  # first 2 digits
                    output[13] = int(str(parameter.value).zfill(4)[2:])  # last 2 digits
        return output
