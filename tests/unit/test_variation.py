import json

import pytest

from featureflags.evaluations.variation import Variation


@pytest.mark.parametrize(
    "test_input,default,expected",
    [
        ("true", False, True),
        ("false", False, False),
        ("", False, False),
    ],
)
def test_variation_bool(test_input, default, expected):
    variation = Variation(identifier="test", value=test_input)

    got = variation.bool(default=default)

    assert got == expected


@pytest.mark.parametrize(
    "test_input,default,expected",
    [
        ("test", "test_default", "test"),
        (None, "test_default", "test_default"),
    ],
)
def test_variation_string(test_input, default, expected):
    variation = Variation(identifier="test", value=test_input)

    got = variation.string(default=default)

    assert got == expected


@pytest.mark.parametrize(
    "test_input,default,expected", [(1.1, 1.0, 1.1), (None, 1.0, 1.0)]
)
def test_variation_number(test_input, default, expected):
    variation = Variation(identifier="test", value=test_input)

    got = variation.number(default=default)

    assert got == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (json.dumps({"field": "value"}), json.dumps({"field": "value"})),
        (None, json.dumps({"field": "value2"})),
    ],
)
def test_variation_json(test_input, expected):
    variation = Variation(identifier="test", value=test_input)

    got = variation.json(default={"field": "value2"})

    assert got == json.loads(expected)
