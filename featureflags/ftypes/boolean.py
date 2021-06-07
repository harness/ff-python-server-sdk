import typing

import attr

from .interface import Interface
from .utils import get_value


@attr.s(auto_attribs=True)
class Boolean(Interface):

    value: bool

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
        _value = get_value(value)
        return self.value is _value

    def greater_than(self, value: typing.Any) -> bool:
        return False

    def greater_than_equal(self, value: typing.Any) -> bool:
        return False

    def less_than(self, value: typing.Any) -> bool:
        return False

    def less_than_equal(self, value: typing.Any) -> bool:
        return False

    def in_list(self, value: typing.List[typing.Any]) -> bool:
        return False
