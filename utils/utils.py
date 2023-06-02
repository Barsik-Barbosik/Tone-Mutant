from constants import constants
from constants.enums import ParameterType
from model.parameter import Parameter


def decimal_to_hex(decimal_num: int) -> str:
    return "{:02X}".format(decimal_num)


def decimal_to_hex_hex(decimal_num: int) -> str:
    if decimal_num > 32267:
        raise ValueError("Number is too big: {}".format(decimal_num))

    return "{:02X}".format(decimal_num % 256) + " {:02X}".format(decimal_num // 256)


def list_to_hex_str(int_list: list) -> str:
    hex_str = ""
    for int_value in int_list:
        hex_str = hex_str + " " + decimal_to_hex(int_value)
    return hex_str


def format_as_nice_hex(input_str: str) -> str:
    string_without_spaces = input_str.replace(" ", "")
    return " ".join(string_without_spaces[i:i + 2] for i in range(0, len(string_without_spaces), 2))


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


def decode_param_value(value: int, parameter: Parameter):
    if parameter.type == ParameterType.KNOB:
        if parameter.choices[1] == 127:  # 0...127
            return value
        elif parameter.choices[1] == 3:  # -3...3
            return value - parameter.choices[1] - 1
        else:  # -12...12, -24...24, -50...50, -64...63
            return value - 64
    elif parameter.type == ParameterType.KNOB_X2:
        return round(value / 2)
    # elif parameter.type == ParameterType.KNOB_X4:
    #     return 1023 - round(value / 4)  # FIXME
    # elif parameter.type == ParameterType.SPECIAL_DELAY_KNOB:
    #     return value
    return value
