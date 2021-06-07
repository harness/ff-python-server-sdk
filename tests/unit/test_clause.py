import pytest

from featureflags.evaluation.constants import SEGMENT_MATCH_OPERATOR, \
    IN_OPERATOR, EQUAL_OPERATOR, GT_OPERATOR, STARTS_WITH_OPERATOR, \
    ENDS_WITH_OPERATOR, CONTAINS_OPERATOR, EQUAL_SENSITIVE_OPERATOR
from featureflags.evaluation.clause import Clause
from featureflags.ftypes import String


@pytest.mark.parametrize('op', [
    None,
    'NOT_FOUND',
])
def test_evaluate_op(op):
    clause = Clause(attribute='email', id='', negate=False, op=op,
                    value=['john@doe.com'])
    
    got = clause.evaluate(None, None, String('john@doe.com'))

    assert got == False


@pytest.mark.parametrize('op,method,expected', [
    (IN_OPERATOR, 'in_list', True),
    (EQUAL_OPERATOR, 'equal', True),
    (GT_OPERATOR, 'greater_than', False),
    (STARTS_WITH_OPERATOR, 'starts_with', True),
    (ENDS_WITH_OPERATOR, 'ends_with', True),
    (CONTAINS_OPERATOR, 'contains', True),
    (EQUAL_SENSITIVE_OPERATOR, 'equal_sensitive', True)
])
def test_evaluate_string(mocker, op, method, expected):
    clause = Clause(attribute='email', id='', negate=False, op=op,
                    value=['john@doe.com'])

    m = mocker.patch.object(String, method, return_value=expected)
    _string = String('john@doe.com')
    
    got = clause.evaluate(None, None, _string)

    assert got == expected
    assert m.call_count == 1
