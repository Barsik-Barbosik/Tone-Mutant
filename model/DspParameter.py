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
        obj = {"name": self.name, "value": self.value}
        if self.type == ParameterType.COMBO:
            obj["value_on_display"] = str(self.value + 1) + " (" + self.choices[self.value] + ")"
        elif self.type in [ParameterType.KNOB, ParameterType.KNOB_2BYTES]:
            obj["value_on_display"] = self.value

        return obj
