import pytest

from featureflags.evaluations.clause import Clause
from featureflags.evaluations.constants import (CONTAINS_OPERATOR,
                                                ENDS_WITH_OPERATOR,
                                                EQUAL_OPERATOR,
                                                EQUAL_SENSITIVE_OPERATOR,
                                                GT_OPERATOR, IN_OPERATOR,
                                                STARTS_WITH_OPERATOR)
from featureflags.ftypes import String


@pytest.mark.parametrize(
    "op",
    [
        None,
        "NOT_FOUND",
    ],
)
def test_evaluate_op(op):
    clause = Clause(
        attribute="email", id="", negate=False, op=op, values=["john@doe.com"]
    )

    got = clause.evaluate(None, None, String("john@doe.com"))

    assert got is False


@pytest.mark.parametrize(
    "op,method,expected",
    [
        (IN_OPERATOR, "in_list", True),
        (EQUAL_OPERATOR, "equal", True),
        (GT_OPERATOR, "greater_than", False),
        (STARTS_WITH_OPERATOR, "starts_with", True),
        (ENDS_WITH_OPERATOR, "ends_with", True),
        (CONTAINS_OPERATOR, "contains", True),
        (EQUAL_SENSITIVE_OPERATOR, "equal_sensitive", True),
    ],
)
def test_evaluate_string(mocker, op, method, expected):
    clause = Clause(
        attribute="email", id="", negate=False, op=op, values=["john@doe.com"]
    )

    m = mocker.patch.object(String, method, return_value=expected)
    _string = String("john@doe.com")

    got = clause.evaluate(None, None, _string)

    assert got == expected
    assert m.call_count == 1
