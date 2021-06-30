
from featureflags.evaluations.variation_map import VariationMap
from featureflags.evaluations.feature import Evaluation, FeatureConfig, FeatureState, FeatureConfigKind
from featureflags.evaluations.weighted_variation import WeightedVariation
from featureflags.evaluations.distribution import Distribution
from featureflags.evaluations.serve import Serve
from featureflags.evaluations.auth_target import Target
from featureflags.evaluations.variation import Variation


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