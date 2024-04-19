from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.distribution import Distribution


T = TypeVar("T", bound="Serve")


@_attrs_define
class Serve:
    """Describe the distribution rule and the variation that should be served to the target

    Attributes:
        distribution (Union[Unset, Distribution]): Describes a distribution rule
        variation (Union[Unset, str]):
    """

    distribution: Union[Unset, "Distribution"] = UNSET
    variation: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        distribution: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.distribution, Unset):
            distribution = self.distribution.to_dict()

        variation = self.variation

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if distribution is not UNSET:
            field_dict["distribution"] = distribution
        if variation is not UNSET:
            field_dict["variation"] = variation

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.distribution import Distribution

        d = src_dict.copy()
        _distribution = d.pop("distribution", UNSET)
        distribution: Union[Unset, Distribution]
        if isinstance(_distribution, Unset):
            distribution = UNSET
        else:
            distribution = Distribution.from_dict(_distribution)

        variation = d.pop("variation", UNSET)

        serve = cls(
            distribution=distribution,
            variation=variation,
        )

        serve.additional_properties = d
        return serve

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
