from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from featureflags.models import UNSET, Unset

from .target_map import TargetMap

T = TypeVar("T", bound="VariationMap")


@attr.s(auto_attribs=True)
class VariationMap:
    """ """

    variation: str
    targets: Union[Unset, List[TargetMap]] = UNSET
    target_segments: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        variation = self.variation
        targets: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.targets, Unset):
            targets = []
            for targets_item_data in self.targets:
                targets_item = targets_item_data.to_dict()

                targets.append(targets_item)

        target_segments: Union[Unset, List[str]] = UNSET
        if not isinstance(self.target_segments, Unset):
            target_segments = self.target_segments

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "variation": variation,
            }
        )
        if targets is not UNSET:
            field_dict["targets"] = targets
        if target_segments is not UNSET:
            field_dict["targetSegments"] = target_segments

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        variation = d.pop("variation")

        targets = []
        _targets = d.pop("targets", UNSET)
        for targets_item_data in _targets or []:
            targets_item = TargetMap.from_dict(targets_item_data)

            targets.append(targets_item)

        target_segments = cast(List[str], d.pop("targetSegments", UNSET))

        variation_map = cls(
            variation=variation,
            targets=targets,
            target_segments=target_segments,
        )

        variation_map.additional_properties = d
        return variation_map

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
