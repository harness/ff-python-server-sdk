import pytest

from featureflags.evaluations.auth_target import Target
from featureflags.openapi.config.models.clause import Clause
from featureflags.evaluations.constants import EQUAL_OPERATOR, \
    STARTS_WITH_OPERATOR
from featureflags.openapi.config.models.distribution import Distribution
from featureflags.evaluations.enum import FeatureState
from featureflags.evaluations.evaluator import Evaluator
from featureflags.openapi.config.models.feature_config import FeatureConfig, FeatureConfigKind
from featureflags.openapi.config.models.segment import Segment
from featureflags.openapi.config.models.serve import Serve
from featureflags.openapi.config.models.serving_rule import ServingRule
from featureflags.openapi.config.models.target_map import TargetMap
from featureflags.openapi.config.models.variation import Variation
from featureflags.openapi.config.models.variation_map import VariationMap
from featureflags.openapi.config.models.weighted_variation import WeightedVariation
from featureflags.lru_cache import LRUCache
from featureflags.repository import Repository

TRUE = "true"
FALSE = "false"


@pytest.fixture
def target():
    return Target(identifier="john", name="John",
                  attributes={"email": "john@doe.com"})


@pytest.fixture
def true_variation():
    return Variation(identifier=TRUE, value=TRUE)


@pytest.fixture
def false_variation():
    return Variation(identifier=FALSE, value=FALSE)


@pytest.fixture
def empty_variation():
    return Variation(identifier="", value=None)


@pytest.fixture
def variations(true_variation, false_variation):
    return [true_variation, false_variation]


@pytest.fixture
def distribution_by_email():
    variations = [
        WeightedVariation(TRUE, 50),
        WeightedVariation(FALSE, 50)
    ]
    return Distribution("email", variations)


@pytest.fixture
def feature(variations):
    default_serve = Serve(variation=TRUE)

    return FeatureConfig(
        feature="bool-flag",
        environment="test",
        default_serve=default_serve,
        kind=FeatureConfigKind.BOOLEAN,
        off_variation=FALSE,
        project="default",
        state=FeatureState.ON,
        variations=variations
    )


@pytest.fixture
def segment(target):
    return Segment(
        identifier="beta",
        name="Beta users",
        environment="test",
        included=[Target(identifier=target.identifier, name=target.name)],
        version=1
    )


@pytest.fixture
def data_provider(feature, segment):
    cache = LRUCache()

    repository = Repository(cache)
    repository.set_flag(feature)
    repository.set_segment(segment)

    return repository


@pytest.mark.parametrize('identifier,expected', [
    (TRUE, 'true_variation'),
    (FALSE, 'false_variation'),
    ("unknown", 'empty_variation')
])
def test_find_variation(request, data_provider, variations, identifier,
                        expected):
    evaluator = Evaluator(data_provider)

    expected = request.getfixturevalue(expected)

    got = evaluator._find_variation(variations, identifier)

    assert got == expected


@pytest.mark.parametrize('bucket_by,value,expected', [
    ("email", 'john@doe.com', 18),
    ("email", 'enver.bisevac@harness', 61),
    ("identifier", 'harness', 6)
])
def test_get_normalized_number(bucket_by, value, expected):
    evaluator = Evaluator(data_provider)

    got = evaluator._get_normalized_number(bucket_by, value)

    assert got == expected


def test_is_enabled(data_provider, target):
    evaluator = Evaluator(data_provider)

    got = evaluator._is_enabled(target, "email", 10)

    assert got is False


def test_evaluate_distribution(data_provider, distribution_by_email, target):
    evaluator = Evaluator(data_provider)

    got = evaluator._evaluate_distribution(distribution_by_email, target)

    assert got == 'true'


def test_check_target_in_segment(data_provider, target):
    evaluator = Evaluator(data_provider)

    got = evaluator._check_target_in_segment(["beta"], target)

    assert got is True


def test_evaluate_clause(data_provider, target):
    evaluator = Evaluator(data_provider)

    clause = Clause(
        id="",
        attribute="identifier",
        op=EQUAL_OPERATOR,
        values=[target.identifier]
    )

    got = evaluator._evaluate_clause(clause, target)

    assert got is True


def test_evaluate_clauses(data_provider, target):
    evaluator = Evaluator(data_provider)
    clause1 = Clause(
        id="",
        attribute="identifier",
        op=EQUAL_OPERATOR,
        values=[target.identifier]
    )

    clause2 = Clause(
        id="",
        attribute="name",
        op=EQUAL_OPERATOR,
        values=[target.name]
    )

    clause3 = Clause(
        id="",
        attribute="name",
        op=EQUAL_OPERATOR,
        values=["Not John"]
    )

    clause4 = Clause(
        id="",
        attribute="name",
        op=STARTS_WITH_OPERATOR,
        values=["Not John"]
    )

    testcases = [
        {"scenario": "Evaluate clauses with no clauses",
         "input": [], "expected": False},
        {"scenario": "Evaluate clauses with 2 Clauses both will match",
         "input": [clause1, clause2], "expected": True},
        {"scenario": "Evaluate clauses with 2 Clauses only 1 match",
         "input": [clause1, clause3], "expected": True},
        {"scenario": "Evaluate clauses with 2 Clauses but no match",
         "input": [clause3, clause4], "expected": False}
    ]

    for tc in testcases:
        actual = evaluator._evaluate_clauses(tc["input"], target)
        assert actual is tc["expected"]


def test_evaluate_rules(data_provider, target):
    evaluator = Evaluator(data_provider)

    clause = Clause(
        id="",
        attribute="identifier",
        op=EQUAL_OPERATOR,
        values=[target.identifier]
    )

    rules = [
        ServingRule(
            clauses=[clause],
            priority=1000,
            rule_id="",
            serve=Serve(
                variation=TRUE
            )
        )
    ]

    got = evaluator._evaluate_rules(rules, target)

    assert got == TRUE


def test_evaluate_variation_map(data_provider, target):
    evaluator = Evaluator(data_provider)

    vmap = [
        VariationMap(variation=TRUE, targets=[TargetMap(
            name=target.name, identifier=target.identifier)])
    ]

    got = evaluator._evaluate_variation_map(vmap, target)

    assert got == TRUE


def test_evaluate_variation_segments_map(data_provider, target):
    evaluator = Evaluator(data_provider)

    vmap = [
        VariationMap(variation=TRUE, target_segments=["beta"])
    ]

    got = evaluator._evaluate_variation_map(vmap, target)

    assert got == TRUE


def test_evaluate_flag_off(data_provider, feature, target, false_variation):
    evaluator = Evaluator(data_provider)
    feature.state = FeatureState.OFF
    got = evaluator._evaluate_flag(feature, target)

    assert got == false_variation


def test_evaluate_flag_on(data_provider, feature, target, true_variation):
    evaluator = Evaluator(data_provider)

    got = evaluator._evaluate_flag(feature, target)

    assert got == true_variation


def test_get_flag_kind(data_provider, feature, target, true_variation):
    evaluator = Evaluator(data_provider)

    got = evaluator.get_kind(feature.feature)

    assert got == FeatureConfigKind.BOOLEAN


def load_v2_flags(repo):
    feature_config_or = FeatureConfig(
        feature="boolflag_or",
        environment="test",
        default_serve=Serve(variation=FALSE),
        kind=FeatureConfigKind.BOOLEAN,
        off_variation=FALSE,
        project="test",
        state=FeatureState.ON,
        variation_to_target_map=[
            VariationMap(variation=TRUE, targets=[], target_segments=['or-segment'])
        ],
        variations=[
            Variation(identifier='true', name='True', value='true'),
            Variation(identifier='false', name='False', value='false')
        ],
        version=1
    )

    feature_config_and = FeatureConfig(
        feature="boolflag_and",
        environment="test",
        default_serve=Serve(variation=FALSE),
        kind=FeatureConfigKind.BOOLEAN,
        off_variation=FALSE,
        project="test",
        state=FeatureState.ON,
        variation_to_target_map=[
            VariationMap(variation=TRUE, targets=[], target_segments=['and-segment'])
        ],
        variations=[
            Variation(identifier='true', name='True', value='true'),
            Variation(identifier='false', name='False', value='false')
        ],
        version=1
    )
    repo.set_flag(feature_config_or)
    repo.set_flag(feature_config_and)


def load_v2_segments(repo):
    segment_or = Segment(
        identifier='or-segment',
        name='is_harness_or_somethingelse_email_OR',
        environment='Production',
        # only 1 servingRules needs to be true (OR)

    )

    repo.set_segment(segment)


@pytest.mark.parametrize('flag_name,expected,email,role', [
    # if (target.attr.email endswith '@harness.io' && target.attr.role = 'developer')
    ('boolflag_and', TRUE, 'user@harness.io', 'developer'),
    ('boolflag_and', TRUE, 'user@harness.io', 'manager'),
    ('boolflag_and', FALSE, 'user@gmail.com', 'developer'),
    ('boolflag_and', FALSE, 'user@gmail.com', 'manager'),
    # if (target.attr.email endswith '@harness.io' || target.attr.email endswith '@somethingelse.com')
    ('boolflag_or', TRUE, 'user@harness.io', 'n/a'),
    ('boolflag_or', TRUE, 'user@somethingelse.com', 'n/a'),
    ('boolflag_or', FALSE, 'user@gmail.com', 'n/a'),
])
def test_enhanced_v2_rules(flag_name, email, role, expected):
    cache = LRUCache()
    repository = Repository(cache)

    load_v2_flags(repository)
    load_v2_segments(repository)

    evaluator = Evaluator(repository)
    target = Target(identifier='test', name="test",
                    attributes={"email": email, "role": role})
    got = evaluator.evaluate(flag_name, target, "boolean")

    assert got == expected
