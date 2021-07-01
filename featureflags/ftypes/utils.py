"""Type utilities"""

import typing


def get_value(value: typing.Union[typing.Any,
              typing.List[typing.Any]]) -> typing.Any:
    if isinstance(value, list):
        return value[0]
    return value


def get_str_value(value: typing.List[typing.Any]) -> str:
    return str(get_value(value))


def get_int_value(value: typing.List[typing.Any]) -> int:
    return int(get_value(value))


def get_float_value(value: typing.List[typing.Any]) -> float:
    return float(get_value(value))
