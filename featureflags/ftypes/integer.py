import typing

import attr

from featureflags.ftypes.interface import Interface

from .utils import get_int_value


@attr.s(auto_attribs=True)
class Integer(Interface):

    value: int

    def starts_with(self, value: typing.Any) -> bool:
        return False

    def ends_with(self, value: typing.Any) -> bool:
        return False

    def match(self, value: typing.Any) -> bool:
        return False

    def contains(self, value: typing.Any) -> bool:
        return False

    def equal_sensitive(self, value: typing.Any) -> bool:
        return False

    def equal(self, value: typing.Any) -> bool:
        _value = get_int_value(value)
        return self.value == _value

    def greater_than(self, value: typing.Any) -> bool:
        _value = get_int_value(value)
        return self.value > _value

    def greater_than_equal(self, value: typing.Any) -> bool:
        _value = get_int_value(value)
        return self.value >= _value

    def less_than(self, value: typing.Any) -> bool:
        _value = get_int_value(value)
        return self.value < _value

    def less_than_equal(self, value: typing.Any) -> bool:
        _value = get_int_value(value)
        return self.value <= _value

    def in_list(self, value: typing.List[typing.Any]) -> bool:
        return self.value in value
