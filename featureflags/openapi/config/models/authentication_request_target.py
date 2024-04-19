from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authentication_request_target_attributes import (
        AuthenticationRequestTargetAttributes,
    )


T = TypeVar("T", bound="AuthenticationRequestTarget")


@_attrs_define
class AuthenticationRequestTarget:
    """
    Attributes:
        identifier (str):
        name (Union[Unset, str]):
        anonymous (Union[Unset, bool]):
        attributes (Union[Unset, AuthenticationRequestTargetAttributes]):
    """

    identifier: str
    name: Union[Unset, str] = UNSET
    anonymous: Union[Unset, bool] = UNSET
    attributes: Union[Unset, "AuthenticationRequestTargetAttributes"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

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
        from ..models.authentication_request_target_attributes import (
            AuthenticationRequestTargetAttributes,
        )

        d = src_dict.copy()
        identifier = d.pop("identifier")

        name = d.pop("name", UNSET)

        anonymous = d.pop("anonymous", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, AuthenticationRequestTargetAttributes]
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = AuthenticationRequestTargetAttributes.from_dict(_attributes)

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
