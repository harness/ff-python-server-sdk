import pytest

from featureflags.ftypes.string import String


@pytest.mark.parametrize(
    ["arg", "input", "mocked", "method", "expected"],
    [
        ("harness.io", ["harness"], "harness", "starts_with", True),
        ("ci/cd harness", ["harness"], "harness", "ends_with", True),
        ("^harness", ["harness"], "harness", "match", True),
        ("ci/cd harness software", ["harness"], "harness", "contains", True),
        ("harness", ["harness"], "harness", "equal_sensitive", True),
        ("harness", ["harneSS"], "harneSS", "equal_sensitive", False),
        ("harness", ["harneSS"], "harneSS", "equal", True),
        ("harnessb", ["harnessa"], "harnessa", "greater_than", True),
        ("harness", ["harness"], "harness", "greater_than_equal", True),
        ("harnessa", ["harnessb"], "harnessb", "less_than", True),
        ("harness", ["harness"], "harness", "less_than_equal", True),
    ],
)
def test_type_methods(mocker, arg, input, mocked, method, expected):

    m = mocker.patch("featureflags.ftypes.string.get_str_value",
                     return_value=mocked)
    _string = String(value=arg)

    fn = getattr(_string, method)
    got = fn(input)

    assert got == expected
    if mocked:
        m.assert_called_with(input)


def test_in_list():

    _string = String(value="harness")

    got = _string.in_list(["wings", "harness"])
    expected = True

    assert got == expected
