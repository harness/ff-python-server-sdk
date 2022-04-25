import pytest

from featureflags.evaluations.auth_target import Target
from featureflags.evaluations.clause import Clause
from featureflags.evaluations.constants import EQUAL_OPERATOR
from featureflags.evaluations.distribution import Distribution
from featureflags.evaluations.enum import FeatureState
from featureflags.evaluations.evaluator import Evaluator
from featureflags.evaluations.feature import FeatureConfig, FeatureConfigKind
from featureflags.evaluations.segment import Segment
from featureflags.evaluations.serve import Serve
from featureflags.evaluations.serving_rule import ServingRule
from featureflags.evaluations.target_map import TargetMap
from featureflags.evaluations.variation import Variation
from featureflags.evaluations.variation_map import VariationMap
from featureflags.evaluations.weighted_variation import WeightedVariation
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
    ("identifier", 'harness', 10)
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
