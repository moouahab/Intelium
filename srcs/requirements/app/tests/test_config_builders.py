from tools.config_builders import build_http_client_settings
from tools.config_builders import build_crawler_settings


def test_build_http_client_settings_defaults_and_overrides():
    settings = build_http_client_settings(
        {
            "respect_robots": False,
            "crawl_delay_seconds": "3",
            "retry_attempts": "4",
            "retry_backoff_seconds": "1.5",
        }
    )
    assert settings["respect_robots"] is False
    assert settings["crawl_delay_seconds"] == 3
    assert settings["retry_attempts"] == 4
    assert settings["retry_backoff_seconds"] == 1.5

    # fallback defaults
    defaults = build_http_client_settings({})
    assert defaults["respect_robots"] is True
    assert defaults["crawl_delay_seconds"] == 0
    assert defaults["retry_attempts"] == 2
    assert defaults["retry_backoff_seconds"] == 0.5


def test_build_crawler_settings_global_quota():
    settings = build_crawler_settings(
        {
            "max_total_pages": "200",
            "max_total_bytes": "1000000",
            "max_depth": 1,
        }
    )
    assert settings["global_max_pages"] == 200
    assert settings["global_max_bytes"] == 1000000
