from featureflags.evaluation.enum import FeatureState, Kind
from featureflags.evaluation.feature import (
    Distribution,
    Evaluation,
    FeatureConfig,
    Serve,
    WeightedVariation,
)
from featureflags.evaluation.target import Target
from featureflags.evaluation.variation import Variation


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
        kind=Kind.BOOLEAN,
        off_variation="false",
        project="default",
        state=FeatureState.ON,
        variations=variations,
    )

    got = fc.evaluate(target)

    assert got == evaluation
