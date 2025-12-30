from cti_core.sources_factory import normalize_overrides


def test_normalize_overrides_handles_numeric_and_bool_strings():
    overrides = {"max_bytes": "10", "respect_robots": "false", "crawl_delay_seconds": "2"}
    result = normalize_overrides(overrides)
    assert result["max_bytes"] == 10
    assert result["respect_robots"] is False
    assert result["crawl_delay_seconds"] == 2


def test_normalize_overrides_drops_invalid_values():
    overrides = {"max_bytes": "abc", "crawl_delay_seconds": "x"}
    result = normalize_overrides(overrides)
    assert "max_bytes" not in result
    assert "crawl_delay_seconds" not in result
