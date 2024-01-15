import json
from typing import Any, Dict, List, Type, TypeVar, Union
from xmlrpc.client import boolean

import attr

from featureflags.evaluations.auth_target import Target
from featureflags.models import UNSET, Unset
from featureflags.util import log

T = TypeVar("T", bound="Variation")


@attr.s(auto_attribs=True)
class Variation(object):
    identifier: str
    value: Union[str, None]
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def bool(self, target: Target, flag_identifier: str,
             default: bool = False) -> bool:
        if self.value:
            result = self.value.lower() == "true"
            log.debug(
                "SDKCODE:6000: Evaluated bool variation successfully:"
                "%s", {"result": result, "flag identifier": flag_identifier,
                       "target": target})
            return result
        log.error(
            "SDKCODE:6001: Failed to evaluate bool variation for %s and the "
            "default variation '%s' is being returned",
            {"target": target, "flag": flag_identifier}, default)
        return default

    def string(self, target: Target, flag_identifier: str,
               default: str) -> str:
        if self.value:
            result = self.value
            log.debug(
                "SDKCODE:6000: Evaluated string variation successfully:"
                "%s", {"result": result, "flag identifier": flag_identifier,
                       "target": target})
            return result
        log.error(
            "SDKCODE:6001: Failed to evaluate string variation for %s and the"
            " default variation '%s' is being returned",
            {"target": target, "flag": flag_identifier}, default)
        return default

    def number(self, target: Target, flag_identifier: str,
               default: float) -> float:
        if self.value:
            result = float(self.value)
            log.debug(
                "SDKCODE:6000: Evaluated number variation successfully:"
                "%s", {"result": result, "flag identifier": flag_identifier,
                       "target": target})
            return result
        log.error(
            "SDKCODE:6001: Failed to evaluate number variation for %s and the"
            " default variation '%s' is being returned",
            {"target": target, "flag": flag_identifier}, default)
        return default

    def int(self, target: Target, flag_identifier: str,
            default: int) -> int:
        if self.value:
            result = int(self.value)
            log.debug(
                "SDKCODE:6000: Evaluated number variation successfully:"
                "%s", {"result": result, "flag identifier": flag_identifier,
                       "target": target})
            return result
        log.error(
            "SDKCODE:6001: Failed to evaluate int variation for %s and the "
            "default variation '%s' is being returned",
            {"target": target, "flag": flag_identifier}, default)
        return default

    def int_or_float(self, target: Target, flag_identifier: str,
                     default: Union[int, float]) -> Union[int, float]:
        if self.value:
            try:
                result = int(self.value)
            except ValueError:
                try:
                    # If int conversion fails, try converting to float
                    result = float(self.value)
                except ValueError:
                    # If both conversions fail, log an error and return the
                    # default
                    log.error(
                        "SDKCODE:6001: Invalid number format for %s. "
                        "Expected a number but got '%s'",
                        {"flag": flag_identifier, "value": self.value}
                    )
                    return default

            log.debug(
                "SDKCODE:6000: Evaluated number variation successfully: %s",
                {"result": result, "flag identifier": flag_identifier,
                 "target": target}
            )
            return result

        log.error(
            "SDKCODE:6001: Failed to evaluate int_or_float variation for %s "
            "and the "
            "default variation '%s' is being returned",
            {"target": target, "flag": flag_identifier}, default)
        return default

    def json(self, target: Target, flag_identifier: str,
             default: dict) -> dict:
        if self.value:
            result = json.loads(self.value)
            log.debug(
                "SDKCODE:6000: Evaluated json variation successfully:"
                "%s", {"result": result, "flag identifier": flag_identifier,
                       "target": target})
            return result
        log.error(
            "SDKCODE:6001: Failed to evaluate json variation for %s and the "
            "default variation '%s' is being returned",
            {"target": target, "flag": flag_identifier}, default)
        return default

    def to_dict(self) -> Dict[str, Any]:
        identifier = self.identifier
        value = self.value
        name = self.name
        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identifier": identifier,
                "value": value,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        identifier = d.pop("identifier")

        value = d.pop("value")

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        variation = cls(
            identifier=identifier,
            value=value,
            name=name,
            description=description,
        )

        variation.additional_properties = d
        return variation

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> boolean:
        return key in self.additional_properties
