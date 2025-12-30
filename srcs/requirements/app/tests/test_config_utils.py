from tools.config_utils import to_int, to_bool


def test_to_int_with_defaults():
    assert to_int("3") == 3
    assert to_int("abc", default=1) == 1
    assert to_int(None, default=5) == 5


def test_to_bool_parses_strings():
    assert to_bool("true") is True
    assert to_bool("False") is False
    assert to_bool(None, default=True) is True
