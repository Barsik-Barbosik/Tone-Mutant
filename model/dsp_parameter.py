from typing import List

from enums.enums import ParameterType


class DspParameter:
    def __init__(self, id: int, name: str, description: str, type: ParameterType, choices: List, default_value: int):
        self.id = id
        self.name = name
        self.description = description
        self.type = type
        self.choices = choices
        self.default_value = default_value

        self.value = self.default_value

    def to_json(self):
        obj = {"name": self.name}
        if self.type == ParameterType.COMBO:
            obj["value"] = self.value + 1
            obj["text"] = self.choices[self.value]
        elif self.type in [ParameterType.KNOB, ParameterType.KNOB_2BYTES]:
            obj["value"] = self.value

        return obj
