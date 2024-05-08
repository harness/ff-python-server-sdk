from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.proxy_config_environments_item import ProxyConfigEnvironmentsItem


T = TypeVar("T", bound="ProxyConfig")


@_attrs_define
class ProxyConfig:
    """TBD

    Attributes:
        page_count (int): The total number of pages Example: 100.
        item_count (int): The total number of items Example: 1.
        page_size (int): The number of items per page Example: 1.
        page_index (int): The current page
        version (Union[Unset, int]): The version of this object.  The version will be incremented each time the object
            is modified Example: 5.
        environments (Union[Unset, List['ProxyConfigEnvironmentsItem']]):
    """

    page_count: int
    item_count: int
    page_size: int
    page_index: int
    version: Union[Unset, int] = UNSET
    environments: Union[Unset, List["ProxyConfigEnvironmentsItem"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        page_count = self.page_count

        item_count = self.item_count

        page_size = self.page_size

        page_index = self.page_index

        version = self.version

        environments: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.environments, Unset):
            environments = []
            for environments_item_data in self.environments:
                environments_item = environments_item_data.to_dict()
                environments.append(environments_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pageCount": page_count,
                "itemCount": item_count,
                "pageSize": page_size,
                "pageIndex": page_index,
            }
        )
        if version is not UNSET:
            field_dict["version"] = version
        if environments is not UNSET:
            field_dict["environments"] = environments

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.proxy_config_environments_item import ProxyConfigEnvironmentsItem

        d = src_dict.copy()
        page_count = d.pop("pageCount")

        item_count = d.pop("itemCount")

        page_size = d.pop("pageSize")

        page_index = d.pop("pageIndex")

        version = d.pop("version", UNSET)

        environments = []
        _environments = d.pop("environments", UNSET)
        for environments_item_data in _environments or []:
            environments_item = ProxyConfigEnvironmentsItem.from_dict(
                environments_item_data
            )

            environments.append(environments_item)

        proxy_config = cls(
            page_count=page_count,
            item_count=item_count,
            page_size=page_size,
            page_index=page_index,
            version=version,
            environments=environments,
        )

        proxy_config.additional_properties = d
        return proxy_config

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
