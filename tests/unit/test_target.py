import pytest

from featureflags.evaluations.auth_target import Target
from featureflags.ftypes import JSON, Boolean, Integer, Number, String


@pytest.mark.parametrize(
    ["target", "attribute", "expected"],
    [
        (Target(identifier="harness"), "identifier", "harness"),
        (Target(identifier="harness", name="Harness"), "name", "Harness"),
        (
            Target(identifier="harness", name="Harness", anonymous=True),
            "anonymous",
            True,
        ),
        (
            Target(identifier="harness", name="Harness",
                   attributes={"height": 180}),
            "height",
            180,
        ),
    ],
)
def test_get_attr_value(target, attribute, expected):

    got = target.get_attr_value(attribute)

    assert got == expected


@pytest.mark.parametrize(
    ["target", "attribute", "expected"],
    [
        (Target(identifier="harness"), "identifier", String),
        (
            Target(identifier="harness", name="Harness", anonymous=True),
            "anonymous",
            Boolean,
        ),
        (
            Target(identifier="harness", attributes={"height": 180}),
            "height",
            Integer
        ),
        (
            Target(identifier="harness", attributes={"weight": 90.5}),
            "weight",
            Number
        ),
        (
            Target(identifier="harness", attributes={
                "custom": {
                    "key": "value"
                }
            }),
            "custom",
            JSON,
        ),
    ],
)
def test_get_type(target, attribute, expected):

    got = target.get_type(attribute)

    assert got.__class__ == expected
