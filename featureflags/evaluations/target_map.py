from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from featureflags.models import UNSET, Unset

T = TypeVar("T", bound="TargetMap")


@attr.s(auto_attribs=True)
class TargetMap:
    """ """

    name: str
    identifier: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        identifier = self.identifier

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if identifier is not UNSET:
            field_dict["identifier"] = identifier

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        identifier = d.pop("identifier", UNSET)

        target_map = cls(
            name=name,
            identifier=identifier,
        )

        target_map.additional_properties = d
        return target_map

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
