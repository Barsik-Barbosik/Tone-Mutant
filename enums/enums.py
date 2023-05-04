from enum import Enum


class ParameterType(Enum):
    COMBO = 1
    KNOB = 2


class SysexType(Enum):
    SET_DSP_MODULE = 85


class TabName(Enum):
    MAIN_PARAMETERS = "Main parameters"
    DSP_1 = "DSP 1"
    DSP_2 = "DSP 2"
    DSP_3 = "DSP 3"
    DSP_4 = "DSP 4"
    OUTPUT = "Output"
