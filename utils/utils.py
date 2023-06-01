from constants.enums import ParameterType
from model.parameter import Parameter


def decimal_to_hex(decimal_num: int) -> str:
    return "{:02X}".format(decimal_num)


def decimal_to_hex_hex(decimal_num: int) -> str:
    if decimal_num > 32267:
        raise ValueError("Number is too big: {}".format(decimal_num))

    return "{:02X}".format(decimal_num % 128) + " {:02X}".format(decimal_num // 128)


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
        if parameter.choices[0] == 0:
            return parameter.value
        if parameter.choices[1] in [12, 24, 50]:
            return parameter.value + 64
        else:
            return parameter.value + parameter.choices[1] + 1
    elif parameter.type == ParameterType.KNOB_255:
        return parameter.value * 2
    else:
        return parameter.value


def decode_param_value(value: int, parameter: Parameter):
    if parameter.type == ParameterType.KNOB:
        if parameter.choices[0] == 0:
            return value
        if parameter.choices[1] in [12, 24, 50]:
            return value - 64
        else:
            return value - parameter.choices[1] - 1
    elif parameter.type == ParameterType.KNOB_255:
        return round(value / 2)
    # elif parameter.type == ParameterType.SPECIAL_DELAY_KNOB:
    #     return value
    return value
