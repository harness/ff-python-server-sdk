from typing import Any, Dict, List, Type, TypeVar, cast

import attr

T = TypeVar("T", bound="Prerequisite")


@attr.s(auto_attribs=True)
class Prerequisite:
    """ """

    feature: str
    variations: List[str]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

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
