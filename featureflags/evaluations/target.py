from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr

from featureflags.ftypes import OPERATORS
from featureflags.ftypes.interface import Interface
from featureflags.models import UNSET, Unset

from .target_attributes import TargetAttributes

T = TypeVar("T", bound="Target")


@attr.s(auto_attribs=True)
class Target(object):

    identifier: str
    account: str
    org: str
    environment: str
    project: str
    name: str
    anonymous: Union[Unset, bool] = UNSET
    attributes: Union[Unset, TargetAttributes] = UNSET
    created_at: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        identifier = self.identifier
        account = self.account
        org = self.org
        environment = self.environment
        project = self.project
        name = self.name
        anonymous = self.anonymous
        attributes: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.attributes, Unset):
            attributes = self.attributes.to_dict()

        created_at = self.created_at

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identifier": identifier,
                "account": account,
                "org": org,
                "environment": environment,
                "project": project,
                "name": name,
            }
        )
        if anonymous is not UNSET:
            field_dict["anonymous"] = anonymous
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        identifier = d.pop("identifier")

        account = d.pop("account")

        org = d.pop("org")

        environment = d.pop("environment")

        project = d.pop("project")

        name = d.pop("name")

        anonymous = d.pop("anonymous", UNSET)

        _attributes = d.pop("attributes", UNSET)
        attributes: Union[Unset, TargetAttributes]
        if isinstance(_attributes, Unset):
            attributes = UNSET
        else:
            attributes = TargetAttributes.from_dict(_attributes)

        created_at = d.pop("createdAt", UNSET)

        target = cls(
            identifier=identifier,
            account=account,
            org=org,
            environment=environment,
            project=project,
            name=name,
            anonymous=anonymous,
            attributes=attributes,
            created_at=created_at,
        )

        target.additional_properties = d
        return target

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

    def get_attr_value(self, attribute: str) -> Optional[str]:
        result: Any = getattr(self, attribute, None)
        if isinstance(result, Unset) and not isinstance(self.attributes,
                                                        Unset):
            result = self.attributes.get(attribute, None)
        return result

    def get_operator(self, attribute: str) -> Optional[Interface]:
        value: Optional[str] = self.get_attr_value(attribute)
        for _type, klass in OPERATORS.items():
            if isinstance(value, _type):
                operator = OPERATORS.get(_type, None)
                if operator:
                    return klass(value)
        return None
