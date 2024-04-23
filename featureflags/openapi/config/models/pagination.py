from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Pagination")


@_attrs_define
class Pagination:
    """
    Attributes:
        page_count (int): The total number of pages Example: 100.
        item_count (int): The total number of items Example: 1.
        page_size (int): The number of items per page Example: 1.
        page_index (int): The current page
        version (Union[Unset, int]): The version of this object.  The version will be incremented each time the object
            is modified Example: 5.
    """

    page_count: int
    item_count: int
    page_size: int
    page_index: int
    version: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        page_count = self.page_count

        item_count = self.item_count

        page_size = self.page_size

        page_index = self.page_index

        version = self.version

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

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        page_count = d.pop("pageCount")

        item_count = d.pop("itemCount")

        page_size = d.pop("pageSize")

        page_index = d.pop("pageIndex")

        version = d.pop("version", UNSET)

        pagination = cls(
            page_count=page_count,
            item_count=item_count,
            page_size=page_size,
            page_index=page_index,
            version=version,
        )

        pagination.additional_properties = d
        return pagination

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
