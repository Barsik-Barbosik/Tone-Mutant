from typing import List

from constants.enums import ParameterType
from model.parameter import DspParameter, Parameter


class DspModule:
    def __init__(self, id: int, name: str, description: str, dsp_parameter_list: List[DspParameter]):
        self.id = id
        self.name = name
        self.description = description
        self.dsp_parameter_list = dsp_parameter_list
        self.bypass = Parameter(1, "Bypass", "DSP Bypass", ParameterType.COMBO, ["OFF", "ON"], 0)

    def to_json(self):
        bypass = True if self.bypass.value == 1 else False
        return {"name": self.name, "parameters": self.dsp_parameter_list, "bypass": bypass}
