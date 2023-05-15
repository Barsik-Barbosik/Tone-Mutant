from enum import Enum

from enums.enums import ParameterType, TabName
from model.DspEffect import DspEffect

EMPTY_DSP_NAME = "OFF"


class MainModel:
    def __init__(self):
        self.currentTabName: Enum = TabName.MAIN_PARAMETERS
        self.selectedDsp1: DspEffect = None
        self.selectedDsp2: DspEffect = None
        self.selectedDsp3: DspEffect = None
        self.selectedDsp4: DspEffect = None

    @staticmethod
    def get_dsp_effect_by_id(dsp_id: int) -> DspEffect:
        for dspEffect in DspEffect.get_dsp_effects_tuple():
            if dspEffect.id == dsp_id:
                return dspEffect
        return None

    def get_current_dsp(self) -> DspEffect:
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
        return self.get_current_dsp().name if self.get_current_dsp() is not None else EMPTY_DSP_NAME

    def set_current_dsp(self, dsp_id: int):
        new_dsp_effect: DspEffect = self.get_dsp_effect_by_id(dsp_id)
        if self.currentTabName == TabName.DSP_1:
            self.selectedDsp1 = new_dsp_effect
        elif self.currentTabName == TabName.DSP_2:
            self.selectedDsp2 = new_dsp_effect
        elif self.currentTabName == TabName.DSP_3:
            self.selectedDsp3 = new_dsp_effect
        elif self.currentTabName == TabName.DSP_4:
            self.selectedDsp4 = new_dsp_effect

    def get_output_text(self) -> str:
        output: str = "Current settings: \n" \
                      + "\nDSP 1: " + str(self.selectedDsp1.name if self.selectedDsp1 is not None else EMPTY_DSP_NAME) \
                      + self.get_params_info(self.selectedDsp1) \
                      + "\nDSP 2: " + str(self.selectedDsp2.name if self.selectedDsp2 is not None else EMPTY_DSP_NAME) \
                      + self.get_params_info(self.selectedDsp2) \
                      + "\nDSP 3: " + str(self.selectedDsp3.name if self.selectedDsp3 is not None else EMPTY_DSP_NAME) \
                      + self.get_params_info(self.selectedDsp3) \
                      + "\nDSP 4: " + str(self.selectedDsp4.name if self.selectedDsp4 is not None else EMPTY_DSP_NAME) \
                      + self.get_params_info(self.selectedDsp4)
        return output

    @staticmethod
    def get_params_info(dsp_effect: DspEffect) -> str:
        output: str = ""
        if dsp_effect is not None:
            for param in dsp_effect.dsp_parameter_list:
                param_value = param.choices[param.value] if param.type == ParameterType.COMBO else str(param.value)
                output = output + "\n\t" + param.name + ": " + param_value
        return output

    def get_current_dsp_params_as_list(self) -> list:
        output = [0] * 14
        dsp_effect = self.get_current_dsp()
        if dsp_effect is not None:
            for idx, parameter in enumerate(dsp_effect.dsp_parameter_list):
                if parameter.type == ParameterType.COMBO:
                    output[idx] = parameter.value
                elif parameter.type == ParameterType.KNOB:
                    output[idx] = parameter.value - parameter.choices[0]
                elif parameter.type == ParameterType.KNOB_2BYTES:
                    # special case, only for the "delay" DSP effect
                    output[12] = int(str(parameter.value).zfill(4)[:2])  # first 2 digits
                    output[13] = int(str(parameter.value).zfill(4)[2:])  # last 2 digits
        return output
