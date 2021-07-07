import pytest

from featureflags.ftypes.utils import (get_float_value, get_int_value,
                                       get_str_value, get_value)


@pytest.mark.parametrize(
    ["input", "expected"],
    [
        (True, True),
        ([True, False], True),
        ([True, True], True),
        ([False, True], False),
        ([False, False], False),
    ],
)
def test_get_value(input, expected):
    got = get_value(input)

    assert got == expected


def test_get_str_value(mocker):
    value = "value"
    m = mocker.patch("featureflags.ftypes.utils.get_value", return_value=value)

    val = get_str_value([value])

    m.assert_called_with([value])
    assert val == value


def test_get_int_value(mocker):
    value = 1
    m = mocker.patch("featureflags.ftypes.utils.get_value", return_value=value)

    val = get_int_value([value])

    m.assert_called_with([value])
    assert val == value


def test_get_number_value(mocker):
    value = 1.1
    m = mocker.patch("featureflags.ftypes.utils.get_value", return_value=value)

    val = get_float_value([value])

    m.assert_called_with([value])
    assert val == value
