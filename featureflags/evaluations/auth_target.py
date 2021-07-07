from typing import Any, Dict, Optional, Type, TypeVar, Union

import attr

from featureflags.ftypes import OPERATORS
from featureflags.ftypes.interface import Interface
from featureflags.models import UNSET, Unset

T = TypeVar("T", bound="Target")


@attr.s(auto_attribs=True)
class Target():

    identifier: str
    name: Union[Unset, str] = UNSET
    anonymous: Union[Unset, bool] = UNSET
    attributes: Union[Unset, Dict[str, Any]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        identifier = self.identifier
        name = self.name
        anonymous = self.anonymous

        attributes: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "identifier": identifier,
            }
        )

        if name is not UNSET:
            field_dict["name"] = name
        if anonymous is not UNSET:
            field_dict["anonymous"] = anonymous
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        identifier = d.pop("identifier")
        name = d.pop("name", UNSET)
        anonymous = d.pop("anonymous", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, Dict[str, Any]]
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = _attributes

        target = cls(
            identifier=identifier,
            name=name,
            anonymous=anonymous,
            attributes=attributes,
        )

        return target

    def get_attr_value(self, attribute: str) -> Optional[str]:
        result: Any = getattr(self, attribute, None)
        if result is None and not isinstance(self.attributes, Unset):
            result = self.attributes.get(attribute, None)
        return result

    def get_operator(self, attribute: str) -> Optional[Interface]:
        value: Optional[str] = self.get_attr_value(attribute)
        for _type, klass in OPERATORS.items():
            if isinstance(value, _type):
                operator = OPERATORS.get(_type, None)
                if operator:
                    return klass(value)
        return None
