import re
import typing

import attr

from featureflags.ftypes.interface import Interface

from .utils import get_str_value


@attr.s(auto_attribs=True)
class String(Interface):

    value: str

    def starts_with(self, value: typing.Any) -> bool:
        _value = get_str_value(value)
        return self.value.startswith(_value)

    def ends_with(self, value: typing.Any) -> bool:
        _value = get_str_value(value)
        return self.value.endswith(_value)

    def match(self, value: typing.Any) -> bool:
        _value = get_str_value(value)
        return re.match(self.value, _value) is not None

    def contains(self, value: typing.Any) -> bool:
        _value = get_str_value(value)
        return _value in self.value

    def equal_sensitive(self, value: typing.Any) -> bool:
        _value = get_str_value(value)
        return self.value == _value

    def equal(self, value: typing.Any) -> bool:
        _value = get_str_value(value)
        return self.value.lower() == _value.lower()

    def greater_than(self, value: typing.Any) -> bool:
        _value = get_str_value(value)
        return self.value.lower() > _value.lower()

    def greater_than_equal(self, value: typing.Any) -> bool:
        _value = get_str_value(value)
        return self.value.lower() >= _value.lower()

    def less_than(self, value: typing.Any) -> bool:
        _value = get_str_value(value)
        return self.value.lower() < _value.lower()

    def less_than_equal(self, value: typing.Any) -> bool:
        _value = get_str_value(value)
        return self.value.lower() <= _value.lower()

    def in_list(self, value: typing.List[typing.Any]) -> bool:
        return self.value.lower() in (val.lower() for val in value)
