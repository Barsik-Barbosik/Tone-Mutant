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

        self.value = self.choices[self.default_value] if type == ParameterType.COMBO else self.default_value
