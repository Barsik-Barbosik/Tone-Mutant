import json
from enum import Enum

from enums.enums import ParameterType, TabName
from external.object_encoder.object_encoder import ObjectEncoder
from model.dsp_module import DspModule
from model.instrument import Instrument

EMPTY_DSP_NAME = "OFF"


class MainModel:
    def __init__(self):
        self.currentTabName: Enum = TabName.MAIN_PARAMETERS

        # TODO: make new class "CurrentTone"

        self.selectedInstrument: Instrument = None
        self.selectedDsp1: DspModule = None
        self.selectedDsp2: DspModule = None
        self.selectedDsp3: DspModule = None
        self.selectedDsp4: DspModule = None

    @staticmethod
    def get_dsp_module_by_id(dsp_id: int) -> DspModule:
        for dsp_module in DspModule.get_all_dsp_modules():
            if dsp_module.id == dsp_id:
                return dsp_module
        return None

    def get_current_dsp_module(self) -> DspModule:
        if self.currentTabName == TabName.DSP_1:
            return self.selectedDsp1
        elif self.currentTabName == TabName.DSP_2:
            return self.selectedDsp2
        elif self.currentTabName == TabName.DSP_3:
            return self.selectedDsp3
        elif self.currentTabName == TabName.DSP_4:
            return self.selectedDsp4
        else:
            return None

    def get_current_block_id(self) -> int:
        if self.currentTabName == TabName.DSP_1:
            return 0
        elif self.currentTabName == TabName.DSP_2:
            return 1
        elif self.currentTabName == TabName.DSP_3:
            return 2
        elif self.currentTabName == TabName.DSP_4:
            return 3
        else:
            return None

    def get_current_dsp_name(self) -> str:
        return self.get_current_dsp_module().name if self.get_current_dsp_module() is not None else EMPTY_DSP_NAME

    def set_current_dsp_module(self, dsp_id: int):
        current_dsp_module: DspModule = self.get_dsp_module_by_id(dsp_id)
        if self.currentTabName == TabName.DSP_1:
            self.selectedDsp1 = current_dsp_module
        elif self.currentTabName == TabName.DSP_2:
            self.selectedDsp2 = current_dsp_module
        elif self.currentTabName == TabName.DSP_3:
            self.selectedDsp3 = current_dsp_module
        elif self.currentTabName == TabName.DSP_4:
            self.selectedDsp4 = current_dsp_module

    def get_current_tone_as_json(self) -> str:
        obj = {"DSP": [
            {"DSP_1": self.selectedDsp1,
             "DSP_2": self.selectedDsp2,
             "DSP_3": self.selectedDsp3,
             "DSP_4": self.selectedDsp4
             }
        ]}
        output = json.dumps(obj, cls=ObjectEncoder, indent=4)
        return output

    @staticmethod
    def get_params_info(dsp_module: DspModule) -> str:
        output: str = ""
        if dsp_module is not None:
            for param in dsp_module.dsp_parameter_list:
                param_value = param.choices[param.value] if param.type == ParameterType.COMBO else str(param.value)
                output = output + "\n\t" + param.name + ": " + param_value
        return output

    def get_current_dsp_params_as_list(self) -> list:
        output = [0] * 14
        dsp_module = self.get_current_dsp_module()
        if dsp_module is not None:
            for idx, parameter in enumerate(dsp_module.dsp_parameter_list):
                if parameter.type == ParameterType.COMBO:
                    output[idx] = parameter.value
                elif parameter.type == ParameterType.KNOB:
                    output[idx] = parameter.value if parameter.choices[0] == 0 else parameter.value + 64
                elif parameter.type == ParameterType.KNOB_2BYTES:
                    # special case, only for the "delay" DSP module
                    output[12] = int(str(parameter.value).zfill(4)[:2])  # first 2 digits
                    output[13] = int(str(parameter.value).zfill(4)[2:])  # last 2 digits
        return output
