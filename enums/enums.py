from enum import Enum


class ParameterType(Enum):
    COMBO = 1
    KNOB = 2
    KNOB_WITH_MIDDLE = 3


class SysexType(Enum):
    SET_DSP_MODULE = 85
