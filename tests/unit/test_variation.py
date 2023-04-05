import json

import pytest

from featureflags.evaluations.auth_target import Target
from featureflags.evaluations.variation import Variation


@pytest.mark.parametrize(
    "test_input, target, flag_identifier, default,expected",
    [
        ("true", Target(identifier='harness'), "flag1", False, True),
        ("false", Target(identifier='harness'), "flag1", False, False),
        ("", Target(identifier='harness'), "flag1", False, False),
    ],
)
def test_variation_bool(test_input, target, flag_identifier,
                        default, expected):
    variation = Variation(identifier="test", value=test_input)

    got = variation.bool(target, flag_identifier, default=default)

    assert got == expected


@pytest.mark.parametrize(
    "test_input, target, flag_identifier, default,expected",
    [
        ("test", Target(identifier='harness'), "flag1", "test_default",
         "test"),
        (None, Target(identifier='harness'), "flag1", "test_default",
         "test_default"),
    ],
)
def test_variation_string(test_input, target, flag_identifier,
                          default, expected):
    variation = Variation(identifier="test", value=test_input)

    got = variation.string(target, flag_identifier, default=default)

    assert got == expected


@pytest.mark.parametrize(
    "test_input,target,flag_identifier,default,expected", [
        (1.1, Target(identifier='harness'), "flag1", 1.0, 1.1),
        (None, Target(identifier='harness'), "flag1", 1.0, 1.0)
    ]
)
def test_variation_number(test_input, target, flag_identifier,
                          default, expected):
    variation = Variation(identifier="test", value=test_input)

    got = variation.number(target, flag_identifier, default=default)

    assert got == expected


@pytest.mark.parametrize(
    "test_input,target,flag_identifier,expected",
    [
        (json.dumps({"field": "value"}), Target(identifier='harness'),
         "flag1", json.dumps({"field": "value"})),
        (None, Target(identifier='harness'), "flag1",
         json.dumps({"field": "value2"})),
    ],
)
def test_variation_json(test_input, target,
                        flag_identifier, expected):
    variation = Variation(identifier="test", value=test_input)

    got = variation.json(target, flag_identifier, default={"field": "value2"})

    assert got == json.loads(expected)
