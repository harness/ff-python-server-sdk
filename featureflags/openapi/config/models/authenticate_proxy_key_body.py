from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AuthenticateProxyKeyBody")


@_attrs_define
class AuthenticateProxyKeyBody:
    """
    Attributes:
        proxy_key (str):  Example: 896045f3-42ee-4e73-9154-086644768b96.
    """

    proxy_key: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        proxy_key = self.proxy_key

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "proxyKey": proxy_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        proxy_key = d.pop("proxyKey")

        authenticate_proxy_key_body = cls(
            proxy_key=proxy_key,
        )

        authenticate_proxy_key_body.additional_properties = d
        return authenticate_proxy_key_body

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
