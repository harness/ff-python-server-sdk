from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Variation")


@_attrs_define
class Variation:
    """A variation of a flag that can be returned to a target

    Attributes:
        identifier (str): The unique identifier for the variation Example: off-variation.
        value (str): The variation value to serve such as true or false for a boolean flag Example: true.
        name (Union[Unset, str]): The user friendly name of the variation Example: Off VAriation.
        description (Union[Unset, str]): A description of the variation
    """

    identifier: str
    value: str
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        identifier = self.identifier

        value = self.value

        name = self.name

        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identifier": identifier,
                "value": value,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        identifier = d.pop("identifier")

        value = d.pop("value")

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        variation = cls(
            identifier=identifier,
            value=value,
            name=name,
            description=description,
        )

        variation.additional_properties = d
        return variation

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
