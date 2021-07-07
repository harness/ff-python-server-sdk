from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.key_value import KeyValue

T = TypeVar("T", bound="TargetData")


@attr.s(auto_attribs=True)
class TargetData:
    """ """

    identifier: str
    name: str
    attributes: List[KeyValue]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        identifier = self.identifier
        name = self.name
        attributes = []
        for attributes_item_data in self.attributes:
            attributes_item = attributes_item_data.to_dict()

            attributes.append(attributes_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identifier": identifier,
                "name": name,
                "attributes": attributes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        identifier = d.pop("identifier")

        name = d.pop("name")

        attributes = []
        _attributes = d.pop("attributes")
        for attributes_item_data in _attributes:
            attributes_item = KeyValue.from_dict(attributes_item_data)

            attributes.append(attributes_item)

        target_data = cls(
            identifier=identifier,
            name=name,
            attributes=attributes,
        )

        target_data.additional_properties = d
        return target_data

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
