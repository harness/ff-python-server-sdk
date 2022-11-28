from typing import (TYPE_CHECKING, Any, Dict, List, Optional, Type, TypeVar,
                    cast)

import attr

from featureflags.ftypes.interface import Interface

from .auth_target import Target
from .constants import (CONTAINS_OPERATOR, ENDS_WITH_OPERATOR, EQUAL_OPERATOR,
                        EQUAL_SENSITIVE_OPERATOR, GT_OPERATOR, IN_OPERATOR,
                        SEGMENT_MATCH_OPERATOR, STARTS_WITH_OPERATOR)

if TYPE_CHECKING:
    from .segment import Segments  # noqa

T = TypeVar("T", bound="Clause")


@attr.s(auto_attribs=True)
class Clause(object):
    attribute: str
    id: str
    op: str
    negate: bool = False
    values: List[str] = attr.Factory(list)
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def evaluate(self, target: Target, segments: Optional['Segments'],
                 operator: Optional[Interface]) -> bool:
        if self.op is None or self.op == "":
            return False
        _op = self.op.lower()
        if _op == SEGMENT_MATCH_OPERATOR.lower():
            if segments:
                return segments.evaluate(target)
            return False
        if operator:
            if _op == IN_OPERATOR.lower():
                return operator.in_list(self.values)
            if _op == EQUAL_OPERATOR.lower():
                return operator.equal(self.values)
            if _op == GT_OPERATOR.lower():
                return operator.greater_than(self.values)
            if _op == STARTS_WITH_OPERATOR.lower():
                return operator.starts_with(self.values)
            if _op == ENDS_WITH_OPERATOR.lower():
                return operator.ends_with(self.values)
            if _op == CONTAINS_OPERATOR.lower():
                return operator.contains(self.values)
            if _op == EQUAL_SENSITIVE_OPERATOR.lower():
                return operator.equal_sensitive(self.values)
        # unknown operation
        return False

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        attribute = self.attribute
        op = self.op
        values = self.values

        negate = self.negate

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "attribute": attribute,
                "op": op,
                "values": values,
                "negate": negate,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        # If clause ID is missing, then default to empty
        id = d.pop("id", "")

        attribute = d.pop("attribute")

        op = d.pop("op")

        values = cast(List[str], d.pop("values"))

        negate = False
        if "negate" in d:
            negate = d.pop("negate")

        clause = cls(
            id=id,
            attribute=attribute,
            op=op,
            values=values,
            negate=negate,
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


class Clauses(List[Clause]):
    def evaluate(self, target: Target, segments: Optional['Segments']) -> bool:
        for clause in self:
            operator = target.get_type(clause.attribute)
            if not clause.evaluate(target, segments, operator):
                return False
        return True
