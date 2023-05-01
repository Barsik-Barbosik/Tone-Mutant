from typing import List

from model.DspParameter import DspParameter


class DspEffect:
    def __init__(self, id: int, name: str, description: str, dsp_parameter_list: List[DspParameter]):
        self.id = id
        self.name = name
        self.description = description
        self.dsp_parameter_list = dsp_parameter_list
