from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Prerequisite")


@_attrs_define
class Prerequisite:
    """Feature Flag pre-requisites

    Attributes:
        feature (str): The feature identifier that is the prerequisite
        variations (List[str]): A list of variations that must be met
    """

    feature: str
    variations: List[str]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        feature = self.feature

        variations = self.variations

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "feature": feature,
                "variations": variations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        feature = d.pop("feature")

        variations = cast(List[str], d.pop("variations"))

        prerequisite = cls(
            feature=feature,
            variations=variations,
        )

        prerequisite.additional_properties = d
        return prerequisite

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
