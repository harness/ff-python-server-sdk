from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.metrics_data import MetricsData
from ..models.target_data import TargetData
from ..models.unset import UNSET, Unset

T = TypeVar("T", bound="Metrics")


@attr.s(auto_attribs=True)
class Metrics:
    """ """

    target_data: Union[Unset, List[TargetData]] = UNSET
    metrics_data: Union[Unset, List[MetricsData]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        target_data: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.target_data, Unset):
            target_data = []
            for target_data_item_data in self.target_data:
                target_data_item = target_data_item_data.to_dict()

                target_data.append(target_data_item)

        metrics_data: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.metrics_data, Unset):
            metrics_data = []
            for metrics_data_item_data in self.metrics_data:
                metrics_data_item = metrics_data_item_data.to_dict()

                metrics_data.append(metrics_data_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if target_data is not UNSET:
            field_dict["targetData"] = target_data
        if metrics_data is not UNSET:
            field_dict["metricsData"] = metrics_data

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        target_data = []
        _target_data = d.pop("targetData", UNSET)
        for target_data_item_data in _target_data or []:
            target_data_item = TargetData.from_dict(target_data_item_data)

            target_data.append(target_data_item)

        metrics_data = []
        _metrics_data = d.pop("metricsData", UNSET)
        for metrics_data_item_data in _metrics_data or []:
            metrics_data_item = MetricsData.from_dict(metrics_data_item_data)

            metrics_data.append(metrics_data_item)

        metrics = cls(
            target_data=target_data,
            metrics_data=metrics_data,
        )

        metrics.additional_properties = d
        return metrics

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
