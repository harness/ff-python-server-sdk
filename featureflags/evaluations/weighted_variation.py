from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="WeightedVariation")


@attr.s(auto_attribs=True)
class WeightedVariation(object):
    variation: str
    weight: int

    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        variation = self.variation
        weight = self.weight

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "variation": variation,
                "weight": weight,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        variation = d.pop("variation")

        weight = d.pop("weight")

        weighted_variation = cls(
            variation=variation,
            weight=weight,
        )

        weighted_variation.additional_properties = d
        return weighted_variation

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
