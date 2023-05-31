from enum import Enum


class ParameterType(Enum):
    COMBO = 1
    SPECIAL_VIBRATO_COMBO = 2
    KNOB = 3
    KNOB_255 = 4
    SPECIAL_DELAY_KNOB = 5


class SysexType(Enum):
    TONE_NAME = 0
    DSP_MODULE = 85
    DSP_PARAMS = 87


class TabName(Enum):
    MAIN_PARAMETERS = "Main parameters"
    DSP_1 = "DSP 1"
    DSP_2 = "DSP 2"
    DSP_3 = "DSP 3"
    DSP_4 = "DSP 4"
    JSON = "View JSON"
