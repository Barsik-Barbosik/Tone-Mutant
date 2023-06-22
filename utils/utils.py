from constants import constants
from constants.enums import ParameterType
from model.parameter import Parameter


# Converts int to 1-byte hex string
# Example: 111 -> "6F"
def int_to_hex(number: int) -> str:
    if number > 255:
        raise ValueError("Number is too big: {}".format(number))
    return "{:02X}".format(number)


# Converts int to 2-byte hex string (7-bit LSB + 7-bit MSB): default for all parameters
# Example: 222 -> "5E 01"
def int_to_lsb_msb(number: int) -> str:
    if number > 32267:
        raise ValueError("Number is too big: {}".format(number))
    return "{:02X}".format(number % 128) + " {:02X}".format(number // 128)


# Converts int to 2-byte hex string (8-bit LSB + 8-bit MSB): for attack/release time
# Example: 222 -> "DE 00"
def int_to_lsb_msb_8bit(number: int) -> str:
    if number > 32267:
        raise ValueError("Number is too big: {}".format(number))
    return "{:02X}".format(number % 256) + " {:02X}".format(number // 256)


def size_to_lsb_msb(size):
    return int_to_lsb_msb(size - 1)


# Converts 2-byte hex string (7-bit LSB + 7-bit MSB) to int
# Example: "5E 01" -> 222
def lsb_msb_to_int(lsb: int, msb: int):
    return msb * 128 + lsb


# Converts each int in the list into a 1-byte hex string and returns the concatenated string
def list_to_hex_str(int_list: list) -> str:
    hex_str = ""
    for int_value in int_list:
        hex_str = hex_str + " " + int_to_hex(int_value)
    return hex_str


# Example: "1122AABB" -> "11 22 AA BB"
def format_as_nice_hex(input_str: str) -> str:
    string_without_spaces = input_str.replace(" ", "")
    return " ".join(string_without_spaces[i:i + 2] for i in range(0, len(string_without_spaces), 2))


# UI value -> synth value
def encode_value_by_type(parameter):
    if parameter.type == ParameterType.SPECIAL_DELAY_KNOB:
        raise ValueError("Wrong parameter type! Process SPECIAL_DELAY_KNOB separately!")
    elif parameter.type == ParameterType.KNOB:
        if parameter.choices[1] == 127:  # 0...127
            return parameter.value
        elif parameter.choices[1] == 3:  # -3...3
            return parameter.value + parameter.choices[1] + 1
        else:  # -12...12, -24...24, -50...50, -64...63
            return parameter.value + 64
    elif parameter.type == ParameterType.KNOB_X2:
        return parameter.value * 2
    elif parameter.type == ParameterType.SPECIAL_ATK_REL_KNOB:
        for idx in range(len(constants.ATTACK_AND_RELEASE_TIME)):
            item = constants.ATTACK_AND_RELEASE_TIME[idx]
            if item[0] == parameter.value:
                return item[2]
        return 0
    else:
        return parameter.value


# Synth value -> UI value
def decode_param_value(value: int, parameter: Parameter):
    # DO NOT USE parameter.value here!
    if parameter.type == ParameterType.SPECIAL_DELAY_KNOB:
        raise ValueError("Wrong parameter type! Process SPECIAL_DELAY_KNOB separately!")
    elif parameter.type == ParameterType.KNOB:
        if parameter.choices[1] == 127:  # 0...127
            return value
        elif parameter.choices[1] == 3:  # -3...3
            return value - parameter.choices[1] - 1
        else:  # -12...12, -24...24, -50...50, -64...63
            return value - 64
    elif parameter.type == ParameterType.KNOB_X2:
        return round(value / 2)
    elif parameter.type == ParameterType.SPECIAL_ATK_REL_KNOB:
        for idx in range(len(constants.ATTACK_AND_RELEASE_TIME)):
            item = constants.ATTACK_AND_RELEASE_TIME[idx]
            if value == item[2]:
                return item[0]
            if value > item[2]:
                return item[0] - 1
        return 0
    elif parameter.name == "Vibrato Type" and value == 0x0F:
        return 0  # Why synth returns "0F" instead of "00"?
    return value
