from typing import Any, Dict, Type, TypeVar, Union

import attr

from featureflags.models import Unset, UNSET

T = TypeVar("T", bound="Target")

@attr.s(auto_attribs=True)
class Target():
    
    identifier: str
    anonymous: Union[Unset, bool] = UNSET
    attributes: Union[Unset, Dict[str, Any]] = UNSET
    
    def to_dict(self) -> Dict[str, Any]:
        identifier = self.identifier
        anonymous = self.anonymous
        attributes: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "identifier": identifier
            }
        )
        if anonymous is not UNSET:
            field_dict["anonymous"] = anonymous
        if attributes is not UNSET:
            field_dict["attributes"] = attributes

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        identifier = d.pop("identifier")

        anonymous = d.pop("anonymous", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, Dict[str, Any]]
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = _attributes

        target = cls(
            identifier=identifier,
            anonymous=anonymous,
            attributes=attributes,
        )

        return target
