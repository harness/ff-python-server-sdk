from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.feature_config import FeatureConfig
    from ..models.segment import Segment


T = TypeVar("T", bound="ProxyConfigEnvironmentsItem")


@_attrs_define
class ProxyConfigEnvironmentsItem:
    """
    Attributes:
        id (Union[Unset, str]):
        api_keys (Union[Unset, List[str]]):
        feature_configs (Union[Unset, List['FeatureConfig']]):
        segments (Union[Unset, List['Segment']]):
    """

    id: Union[Unset, str] = UNSET
    api_keys: Union[Unset, List[str]] = UNSET
    feature_configs: Union[Unset, List["FeatureConfig"]] = UNSET
    segments: Union[Unset, List["Segment"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        api_keys: Union[Unset, List[str]] = UNSET
        if not isinstance(self.api_keys, Unset):
            api_keys = self.api_keys

        feature_configs: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.feature_configs, Unset):
            feature_configs = []
            for feature_configs_item_data in self.feature_configs:
                feature_configs_item = feature_configs_item_data.to_dict()
                feature_configs.append(feature_configs_item)

        segments: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.segments, Unset):
            segments = []
            for segments_item_data in self.segments:
                segments_item = segments_item_data.to_dict()
                segments.append(segments_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if api_keys is not UNSET:
            field_dict["apiKeys"] = api_keys
        if feature_configs is not UNSET:
            field_dict["featureConfigs"] = feature_configs
        if segments is not UNSET:
            field_dict["segments"] = segments

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.feature_config import FeatureConfig
        from ..models.segment import Segment

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        api_keys = cast(List[str], d.pop("apiKeys", UNSET))

        feature_configs = []
        _feature_configs = d.pop("featureConfigs", UNSET)
        for feature_configs_item_data in _feature_configs or []:
            feature_configs_item = FeatureConfig.from_dict(feature_configs_item_data)

            feature_configs.append(feature_configs_item)

        segments = []
        _segments = d.pop("segments", UNSET)
        for segments_item_data in _segments or []:
            segments_item = Segment.from_dict(segments_item_data)

            segments.append(segments_item)

        proxy_config_environments_item = cls(
            id=id,
            api_keys=api_keys,
            feature_configs=feature_configs,
            segments=segments,
        )

        proxy_config_environments_item.additional_properties = d
        return proxy_config_environments_item

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
