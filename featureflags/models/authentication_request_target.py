from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.authentication_request_target_attributes import \
    AuthenticationRequestTargetAttributes
from .unset import UNSET, Unset

T = TypeVar("T", bound="AuthenticationRequestTarget")


@attr.s(auto_attribs=True)
class AuthenticationRequestTarget:
    """ """

    identifier: str
    name: Union[Unset, str] = UNSET
    anonymous: Union[Unset, bool] = UNSET
    attributes: Union[Unset, AuthenticationRequestTargetAttributes] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        identifier = self.identifier
        name = self.name
        anonymous = self.anonymous
        attributes: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
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
        attributes: Union[Unset, AuthenticationRequestTargetAttributes]
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = AuthenticationRequestTargetAttributes.from_dict(
                _attributes
            )

        authentication_request_target = cls(
            identifier=identifier,
            name=name,
            anonymous=anonymous,
            attributes=attributes,
        )

        authentication_request_target.additional_properties = d
        return authentication_request_target

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
