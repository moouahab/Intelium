from tools.config_builders import build_http_client_settings


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
