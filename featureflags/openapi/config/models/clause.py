from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Clause")


@_attrs_define
class Clause:
    """A clause describes what conditions are used to evaluate a flag

    Attributes:
        attribute (str): The attribute to use in the clause.  This can be any target attribute Example: identifier.
        op (str): The type of operation such as equals, starts_with, contains Example: starts_with.
        values (List[str]): The values that are compared against the operator
        negate (bool): Is the operation negated?
        id (Union[Unset, str]): The unique ID for the clause Example: 32434243.
    """

    attribute: str
    op: str
    values: List[str]
    negate: bool
    id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        attribute = self.attribute

        op = self.op

        values = self.values

        negate = self.negate

        id = self.id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "attribute": attribute,
                "op": op,
                "values": values,
                "negate": negate,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        attribute = d.pop("attribute")

        op = d.pop("op")

        values = cast(List[str], d.pop("values"))

        negate = d.pop("negate")

        id = d.pop("id", UNSET)

        clause = cls(
            attribute=attribute,
            op=op,
            values=values,
            negate=negate,
            id=id,
        )

        clause.additional_properties = d
        return clause

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
