from enum import Enum, IntEnum


class TabName(Enum):
    MAIN_PARAMETERS = "Main parameters"
    DSP_1 = "DSP 1"
    DSP_2 = "DSP 2"
    DSP_3 = "DSP 3"
    DSP_4 = "DSP 4"
    JSON = "View JSON"


class ParameterType(Enum):
    COMBO = 1
    KNOB = 2
    KNOB_X2 = 3
    SPECIAL_ATK_REL_KNOB = 4
    SPECIAL_DELAY_KNOB = 5


class SysexId(IntEnum):
    CASIO = 0x44
    NON_REAL_TIME = 0x7E
    REAL_TIME = 0x7F


class SysexType(Enum):
    TONE_NAME = 0
    DSP_MODULE = 85
    DSP_PARAMS = 87
