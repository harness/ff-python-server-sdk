from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.metrics_data_metrics_type import MetricsDataMetricsType

if TYPE_CHECKING:
    from ..models.key_value import KeyValue


T = TypeVar("T", bound="MetricsData")


@_attrs_define
class MetricsData:
    """
    Attributes:
        timestamp (int): time at when this data was recorded Example: 1608175465.
        count (int):
        metrics_type (MetricsDataMetricsType): This can be of type FeatureMetrics
        attributes (List['KeyValue']):
    """

    timestamp: int
    count: int
    metrics_type: MetricsDataMetricsType
    attributes: List["KeyValue"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

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
        from ..models.key_value import KeyValue

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
