from typing import List

from enums.enums import ParameterType


class DspParameter:
    def __init__(self, id: int, name: str, description: str, type: ParameterType, settings: List[int], default_value: int):
        self.id = id
        self.name = name
        self.description = description
        self.type = type
        self.settings = settings
        self.defaultValue = default_value
