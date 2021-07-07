from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.key_value import KeyValue
from ..models.metrics_data_metrics_type import MetricsDataMetricsType

T = TypeVar("T", bound="MetricsData")


@attr.s(auto_attribs=True)
class MetricsData:
    """ """

    timestamp: int
    count: int
    metrics_type: MetricsDataMetricsType
    attributes: List[KeyValue]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        timestamp = self.timestamp
        count = self.count
        metrics_type = self.metrics_type.value

        attributes = []
        for attributes_item_data in self.attributes:
            attributes_item = attributes_item_data.to_dict()

            attributes.append(attributes_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "timestamp": timestamp,
                "count": count,
                "metricsType": metrics_type,
                "attributes": attributes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        timestamp = d.pop("timestamp")

        count = d.pop("count")

        metrics_type = MetricsDataMetricsType(d.pop("metricsType"))

        attributes = []
        _attributes = d.pop("attributes")
        for attributes_item_data in _attributes:
            attributes_item = KeyValue.from_dict(attributes_item_data)

            attributes.append(attributes_item)

        metrics_data = cls(
            timestamp=timestamp,
            count=count,
            metrics_type=metrics_type,
            attributes=attributes,
        )

        metrics_data.additional_properties = d
        return metrics_data

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
