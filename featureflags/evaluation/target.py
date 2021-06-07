import typing

import attr

from featureflags.ftypes.interface import Interface
from featureflags.ftypes import OPERATORS

@attr.s(auto_attribs=True)
class Target(object):
    identifier: str
    name: typing.Optional[str] = None
    anonymous: bool = False
    attributes: typing.Dict[str, typing.Any] = {}

    def get_attr_value(self, attribute: str) -> typing.Optional[str]:
        result: typing.Any = getattr(self, attribute, None)
        if result is None:
            result = self.attributes.get(attribute, None)
        return result

    def get_operator(self, attribute: str) -> typing.Optional[Interface]:
        value: typing.Optional[str] = self.get_attr_value(attribute)
        for _type, klass in OPERATORS.items():
            if isinstance(value, _type):
                operator = OPERATORS.get(_type, None)
                if operator:
                    return klass(value)
        return None
