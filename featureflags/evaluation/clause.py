import typing

import attr

from .target import Target
from .segment import Segments
from featureflags.ftypes.interface import Interface
from .constants import SEGMENT_MATCH_OPERATOR, IN_OPERATOR, EQUAL_OPERATOR, \
    GT_OPERATOR, STARTS_WITH_OPERATOR, ENDS_WITH_OPERATOR, CONTAINS_OPERATOR, \
    EQUAL_SENSITIVE_OPERATOR


@attr.s(auto_attribs=True)
class Clause(object):
    attribute: str
    id: str
    op: str
    negate: bool = False
    value: typing.List[str] = attr.Factory(list)

    def evaluate(self, target: Target, segments: typing.Optional[Segments], operator: Interface) -> bool:
        if self.op is None or self.op == '':
            return False
        _op = self.op.lower()
        if _op == SEGMENT_MATCH_OPERATOR:
            return False
        if _op == IN_OPERATOR:
            return operator.in_list(self.value)
        if _op == EQUAL_OPERATOR:
            return operator.equal(self.value)
        if _op == GT_OPERATOR:
            return operator.greater_than(self.value)
        if _op == STARTS_WITH_OPERATOR:
            return operator.starts_with(self.value)
        if _op == ENDS_WITH_OPERATOR:
            return operator.ends_with(self.value)
        if _op == CONTAINS_OPERATOR:
            return operator.contains(self.value)
        if _op == EQUAL_SENSITIVE_OPERATOR:
            return operator.equal_sensitive(self.value)

        # unknown operation
        return False


class Clauses(typing.List[Clause]):
    
    def evaluate(self, target: Target, segments: typing.Optional[Segments]) -> bool:
        for clause in self:
            operator = target.get_operator(clause.attribute)
            if operator is None:
                return False
            if not clause.evaluate(target, segments, operator):
                return False
        return True
