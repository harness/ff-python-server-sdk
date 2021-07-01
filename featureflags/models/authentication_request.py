from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from .authentication_request_target import AuthenticationRequestTarget
from .unset import UNSET, Unset

T = TypeVar("T", bound="AuthenticationRequest")


@attr.s(auto_attribs=True)
class AuthenticationRequest:
    """ """

    api_key: str
    target: Union[Unset, AuthenticationRequestTarget] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        api_key = self.api_key
        target: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.target, Unset):
            target = self.target.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "apiKey": api_key,
            }
        )
        if target is not UNSET:
            field_dict["target"] = target

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        api_key = d.pop("apiKey")

        _target = d.pop("target", UNSET)
        target: Union[Unset, AuthenticationRequestTarget]
        if isinstance(_target, Unset):
            target = UNSET
        else:
            target = AuthenticationRequestTarget.from_dict(_target)

        authentication_request = cls(
            api_key=api_key,
            target=target,
        )

        authentication_request.additional_properties = d
        return authentication_request

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
