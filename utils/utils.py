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
