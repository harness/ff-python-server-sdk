
from featureflags.evaluations.auth_target import Target
from featureflags.evaluations.clause import Clause, Clauses
from featureflags.evaluations.constants import SEGMENT_MATCH_OPERATOR
from featureflags.evaluations.distribution import Distribution
from featureflags.evaluations.feature import (Evaluation, FeatureConfig,
                                              FeatureConfigKind, FeatureState)
from featureflags.evaluations.segment import Segment, Segments
from featureflags.evaluations.serve import Serve
from featureflags.evaluations.serving_rule import ServingRule, ServingRules
from featureflags.evaluations.variation import Variation
from featureflags.evaluations.variation_map import VariationMap
from featureflags.evaluations.weighted_variation import WeightedVariation


def test_get_key_name():
    target = Target(identifier="john", attributes={"email": "john@doe.com"})
    wv1 = WeightedVariation("true", 70)
    wv2 = WeightedVariation("false", 30)
    distribution = Distribution("email", [wv1, wv2])

    key = distribution.get_key_name(target)

    assert key == "true"


def test_evaluate_basic():

    target = Target(identifier="john", attributes={"email": "john@doe.com"})

    default_serve = Serve(variation="true")

    variations = [
        Variation(identifier="true", value="true"),
        Variation(identifier="false", value="false"),
    ]

    evaluation = Evaluation("bool-flag", variations[0])

    fc = FeatureConfig(
        feature="bool-flag",
        environment="production",
        default_serve=default_serve,
        kind=FeatureConfigKind.BOOLEAN,
        off_variation="false",
        project="default",
        state=FeatureState.ON,
        variations=variations,
    )

    got = fc.evaluate(target)

    assert got == evaluation


def test_evaluate_target_map():
    target = Target(identifier="user1@example.com")

    default_serve = Serve(variation="true")

    variations = [
        Variation(identifier="true", value="true"),
        Variation(identifier="false", value="false"),
    ]

    evaluation = Evaluation("bool-flag", variations[1])

    variation_to_target_map = VariationMap(variation=variations[1].identifier,
                                           targets=[target])

    fc = FeatureConfig(
        feature="bool-flag",
        environment="production",
        default_serve=default_serve,
        kind=FeatureConfigKind.BOOLEAN,
        off_variation="false",
        project="default",
        state=FeatureState.ON,
        variations=variations,
        variation_to_target_map=[variation_to_target_map]
    )

    got = fc.evaluate(target)

    assert got == evaluation


def test_evaluate_segment_match():
    target = Target(identifier="user1@example.com")
    segment = Segment(
        identifier='beta',
        name='Beta',
        included=[target.identifier]
    )

    default_serve = Serve(variation="true")

    variations = [
        Variation(identifier="true", value="true"),
        Variation(identifier="false", value="false"),
    ]

    evaluation = Evaluation("bool-flag", variations[1])

    clause = Clause(
        attribute='',
        id='',
        op=SEGMENT_MATCH_OPERATOR,
        values=['beta']
    )
    clauses = Clauses([clause])

    serve = Serve(variation="false")

    rule = ServingRule(clauses=clauses, priority=1000, rule_id='', serve=serve)
    rules = ServingRules([rule])

    fc = FeatureConfig(
        feature="bool-flag",
        environment="production",
        default_serve=default_serve,
        kind=FeatureConfigKind.BOOLEAN,
        off_variation="false",
        project="default",
        state=FeatureState.ON,
        variations=variations,
        segments=Segments({
            'beta': segment
        }),
        rules=rules
    )

    got = fc.evaluate(target)

    assert got.variation.identifier == evaluation.variation.identifier
