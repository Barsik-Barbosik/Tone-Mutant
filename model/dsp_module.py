from typing import List

from model.parameter import DspParameter


class DspModule:
    def __init__(self, id: int, name: str, description: str, dsp_parameter_list: List[DspParameter]):
        self.id = id
        self.name = name
        self.description = description
        self.dsp_parameter_list = dsp_parameter_list

    def to_json(self):
        return {"name": self.name, "parameters": self.dsp_parameter_list}
