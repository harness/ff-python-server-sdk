import pytest

from featureflags.ftypes.number import Number


@pytest.mark.parametrize(
    ["arg", "input", "mocked", "method", "expected"],
    [
        ("", [], None, "starts_with", False),
        ("", [], None, "ends_with", False),
        ("", [], None, "match", False),
        ("", [], None, "contains", False),
        ("", [], None, "equal_sensitive", False),
        (1.1, 1.1, 1.1, "equal", True),
        (2.0, 1.0, 1.0, "greater_than", True),
        (2.0, 1.0, 2.0, "greater_than_equal", True),
        (1.0, 1.0, 2.0, "less_than", True),
        (1.1, 1.1, 2.0, "less_than_equal", True),
    ],
)
def test_type_methods(mocker, arg, input, mocked, method, expected):

    m = mocker.patch("featureflags.ftypes.number.get_float_value",
                     return_value=mocked)
    number = Number(value=arg)

    fn = getattr(number, method)
    got = fn(input)

    assert got == expected
    if mocked:
        m.assert_called_with(input)


def test_in_list():

    number = Number(value=1)

    got = number.in_list([1, 2])
    expected = True

    assert got == expected
