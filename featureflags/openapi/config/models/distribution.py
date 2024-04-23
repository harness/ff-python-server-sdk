from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.weighted_variation import WeightedVariation


T = TypeVar("T", bound="Distribution")


@_attrs_define
class Distribution:
    """Describes a distribution rule

    Attributes:
        bucket_by (str): The attribute to use when distributing targets across buckets
        variations (List['WeightedVariation']): A list of variations and the weight that should be given to each
    """

    bucket_by: str
    variations: List["WeightedVariation"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

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
        from ..models.weighted_variation import WeightedVariation

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
