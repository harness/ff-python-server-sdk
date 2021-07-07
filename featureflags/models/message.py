import json
from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="Message")


@attr.s(auto_attribs=True)
class Message(object):
    event: str
    domain: str
    identifier: str
    version: int

    def to_dict(self) -> Dict[str, Any]:
        event = self.event
        domain = self.domain
        identifier = self.identifier
        version = self.version

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "event": event,
                "domain": domain,
                "identifier": identifier,
                "version": version
            }
        )
        return field_dict

    @classmethod
    def from_str(cls: Type[T], src: str) -> T:
        if src is None or src == '':
            raise ValueError('source cannot be empty or None')
        d = json.loads(src)
        return cls.from_dict(d)

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        event = d.pop("event")
        domain = d.pop("domain")
        identifier = d.pop("identifier")
        version = d.pop("version")

        message = cls(
            event=event,
            domain=domain,
            identifier=identifier,
            version=version
        )

        return message
