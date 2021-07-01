import pytest

from featureflags.ftypes.integer import Integer


@pytest.mark.parametrize(
    ["arg", "input", "mocked", "method", "expected"],
    [
        ("", [], None, "starts_with", False),
        ("", [], None, "ends_with", False),
        ("", [], None, "match", False),
        ("", [], None, "contains", False),
        ("", [], None, "equal_sensitive", False),
        (1, 1, 1, "equal", True),
        (2, 1, 1, "greater_than", True),
        (2, 1, 2, "greater_than_equal", True),
        (1, 1, 2, "less_than", True),
        (1, 1, 2, "less_than_equal", True),
    ],
)
def test_type_methods(mocker, arg, input, mocked, method, expected):

    m = mocker.patch("featureflags.ftypes.integer.get_int_value",
                     return_value=mocked)
    _integer = Integer(value=arg)

    fn = getattr(_integer, method)
    got = fn(input)

    assert got == expected
    if mocked:
        m.assert_called_with(input)


def test_in_list():

    _integer = Integer(value=1)

    got = _integer.in_list([1, 2])
    expected = True

    assert got == expected
