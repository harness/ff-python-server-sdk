from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="WeightedVariation")


@_attrs_define
class WeightedVariation:
    """A variation and the weighting it should receive as part of a percentage rollout

    Attributes:
        variation (str): The variation identifier Example: off-variation.
        weight (int): The weight to be given to the variation in percent Example: 50.
    """

    variation: str
    weight: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

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
