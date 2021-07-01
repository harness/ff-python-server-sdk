from featureflags.ftypes.boolean import Boolean


def test_equal(mocker):
    input = [True, False]

    m = mocker.patch("featureflags.ftypes.boolean.get_value",
                     return_value=True)
    boolean = Boolean(value=True)

    got = boolean.equal(input)
    expected = True

    assert got == expected
    m.assert_called_with(input)
