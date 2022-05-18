from typing import Any, Dict, List, Type, TypeVar

import attr

from .auth_target import Target
from .constants import ONE_HUNDRED
from .strategy import get_normalized_number
from .weighted_variation import WeightedVariation

T = TypeVar("T", bound="Distribution")


@attr.s(auto_attribs=True)
class Distribution(object):
    bucket_by: str
    variations: List[WeightedVariation]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def get_key_name(self, target: Target) -> str:
        variation: str = ""
        for _variation in self.variations:
            variation = _variation.variation
            if self.is_enabled(target, _variation.weight):
                return variation
        if self.is_enabled(target, ONE_HUNDRED):
            return variation
        return ""

    def is_enabled(self, target: Target, percentage: int) -> bool:
        identifier = target.get_attr_value(self.bucket_by)
        if not identifier or identifier == "":
            return False
        bucket_id = get_normalized_number(identifier, self.bucket_by)
        return percentage > 0 and bucket_id <= percentage

    def to_dict(self) -> Dict[str, Any]:
        bucket_by = self.bucket_by
        variations = []
        for variations_item_data in self.variations:
            variations_item = variations_item_data.to_dict()

            variations.append(variations_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bucketBy": bucket_by,
                "variations": variations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        if src_dict is None:
            return None
        d = src_dict.copy()
        bucket_by = d.pop("bucketBy")

        variations = []
        _variations = d.pop("variations")
        for variations_item_data in _variations:
            variations_item = WeightedVariation.from_dict(variations_item_data)

            variations.append(variations_item)

        distribution = cls(
            bucket_by=bucket_by,
            variations=variations,
        )

        distribution.additional_properties = d
        return distribution

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
