from typing import List

from constants.enums import ParameterType


class Parameter:
    def __init__(self, id: int, name: str, description: str, type: ParameterType, choices: List, value: int):
        self.id = id
        self.name = name
        self.description = description
        self.type = type
        self.choices = choices
        self.value = value

    def to_json(self):
        obj = {"name": self.name}
        if self.type == ParameterType.COMBO:
            obj["value"] = self.value + 1
            obj["text"] = self.choices[self.value].replace("\t", " ")
        else:
            obj["value"] = self.value
        return obj


class MainParameter(Parameter):
    def __init__(self, id: int, action_number: int, block_id: int, name: str, description: str, type: ParameterType,
                 choices: List, value: int):
        super().__init__(id, name, description, type, choices, value)
        self.action_number: int = action_number  # TODO: rename to param_number
        self.block_id: int = block_id


class DspParameter(Parameter):
    def __init__(self, id: int, name: str, description: str, type: ParameterType, choices: List, value: int):
        super().__init__(id, name, description, type, choices, value)
