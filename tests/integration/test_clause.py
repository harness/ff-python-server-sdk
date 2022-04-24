from featureflags.evaluations.auth_target import Target
from featureflags.evaluations.clause import Clause, Clauses
from featureflags.evaluations.constants import EQUAL_OPERATOR


def test_evaluate_clauses():
    target = Target(
        identifier="john",
        anonymous=False,
        attributes={"email": "john@doe.com"}
    )
    clause_1 = Clause(
        attribute="email",
        id="",
        negate=False,
        op=EQUAL_OPERATOR,
        values=["john@doe.com"],
    )
    clause_2 = Clause(
        attribute="anonymous", id="",
        negate=False,
        op=EQUAL_OPERATOR,
        values=[False]
    )
    clauses = Clauses([clause_1, clause_2])

    got = clauses.evaluate(target, [])

    assert got is False
