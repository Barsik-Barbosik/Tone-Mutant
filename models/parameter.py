from typing import List

from constants.enums import ParameterType


class Parameter:
    def __init__(self, id: int, name: str, description: str, type: ParameterType, choices: List):
        self.id = id
        self.name = name
        self.description = description
        self.type = type
        self.choices = choices
        self.value = 1 if self.type == ParameterType.SPECIAL_DELAY_KNOB else 0

    def to_json(self):
        obj = {"name": self.name}
        if self.type == ParameterType.COMBO:
            obj["value"] = self.value + 1
            obj["text"] = self.choices[self.value].replace("\t", " ")
        else:
            obj["value"] = self.value
        return obj


class MainParameter(Parameter):
    def __init__(self, id: int, param_number: int, block_id: int, name: str, description: str, type: ParameterType,
                 choices: List):
        super().__init__(id, name, description, type, choices)
        self.param_number: int = param_number
        self.block_id: int = block_id


class AdvancedParameter(Parameter):
    def __init__(self, id: int, param_number: int, block_id: int, name: str, description: str, type: ParameterType,
                 choices: List):
        super().__init__(id, name, description, type, choices)
        self.param_number: int = param_number
        self.block_id: int = block_id


class DspParameter(Parameter):
    def __init__(self, id: int, name: str, description: str, type: ParameterType, choices: List):
        super().__init__(id, name, description, type, choices)
