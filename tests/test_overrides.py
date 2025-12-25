from tools.overrides import normalize_overrides, merge_headers


def test_normalize_overrides_headers_and_user_agent():
    raw = {
        "max_bytes": "1000",
        "respect_robots": "no",
        "crawl_delay_seconds": "5",
        "headers": {"X-Test": "1"},
        "user_agent": " UA ",
    }
    result = normalize_overrides(raw)

    assert result["max_bytes"] == 1000
    assert result["respect_robots"] is False
    assert result["crawl_delay_seconds"] == 5
    assert result["headers"] == {"X-Test": "1"}
    assert result["user_agent"] == "UA"


def test_merge_headers_applies_user_agent_and_overrides():
    base = {"Authorization": "Bearer x", "User-Agent": "base-UA"}
    override = {"User-Agent": "custom-UA", "X-Extra": "1"}

    merged = merge_headers(base, override_headers=override, user_agent="default-UA")

    # existing UA should stay if override sets a new one
    assert merged["User-Agent"] == "custom-UA"
    assert merged["Authorization"] == "Bearer x"
    assert merged["X-Extra"] == "1"
