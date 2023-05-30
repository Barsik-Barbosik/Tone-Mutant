from typing import List

from constants.enums import ParameterType
from model.parameter import DspParameter


class DspModule:
    def __init__(self, id: int, name: str, description: str, dsp_parameter_list: List[DspParameter]):
        self.id = id
        self.name = name
        self.description = description
        self.dsp_parameter_list = dsp_parameter_list

    def to_json(self):
        return {"name": self.name, "parameters": self.dsp_parameter_list}

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
