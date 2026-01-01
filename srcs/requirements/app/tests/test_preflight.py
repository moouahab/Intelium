from tools.preflight import check_env_requirements, collect_required_env


def test_preflight_collects_required_env(minimal_config):
    auth_conf = {
        "hosts": {
            "otx.alienvault.com": {"X-OTX-API-KEY": "${OTX_API_KEY}"},
        }
    }
    required = collect_required_env(minimal_config, auth_conf=auth_conf)
    assert "MONGO_URI" in required
    assert "MISTRAL_API_KEY" in required
    assert "OTX_API_KEY" in required
    assert "SLACK_WEBHOOK_URL" not in required


def test_preflight_collects_alerting_env_when_required(minimal_config):
    config = dict(minimal_config)
    config["ops"] = dict(config["ops"], require_alerting_env=True)
    required = collect_required_env(config, auth_conf={})
    assert "SLACK_WEBHOOK_URL" in required
    assert "ALERT_EMAIL_TO" in required
    assert "SMTP_HOST" in required


def test_preflight_scopes_auth_env_to_sources(minimal_config):
    config = dict(minimal_config)
    config["sources"] = [
        {"url": "https://www.cert.ssi.gouv.fr/alerte/", "type": "html"},
    ]
    auth_conf = {
        "hosts": {
            "otx.alienvault.com": {"X-OTX-API-KEY": "${OTX_API_KEY}"},
            "www.cert.ssi.gouv.fr": {"Authorization": "${CERT_TOKEN}"},
        }
    }
    required = collect_required_env(config, auth_conf=auth_conf)
    assert "CERT_TOKEN" in required
    assert "OTX_API_KEY" not in required


def test_preflight_blocks_when_missing(monkeypatch, minimal_config):
    auth_conf = {"hosts": {"otx.alienvault.com": {"X-OTX-API-KEY": "${OTX_API_KEY}"}}}
    # Assure que les variables ne sont pas présentes
    for key in [
        "MONGO_URI",
        "MISTRAL_API_KEY",
        "OTX_API_KEY",
        "SLACK_WEBHOOK_URL",
        "ALERT_EMAIL_TO",
        "ALERT_EMAIL_FROM",
        "SMTP_HOST",
        "SMTP_PORT",
    ]:
        monkeypatch.delenv(key, raising=False)
    assert check_env_requirements(minimal_config, auth_conf, logger=None) is False


def test_preflight_passes_when_present(monkeypatch, minimal_config):
    auth_conf = {"hosts": {"otx.alienvault.com": {"X-OTX-API-KEY": "${OTX_API_KEY}"}}}
    monkeypatch.setenv("MONGO_URI", "mongodb://localhost:27017/cti")
    monkeypatch.setenv("MISTRAL_API_KEY", "test")
    monkeypatch.setenv("OTX_API_KEY", "test")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://example.invalid/webhook")
    monkeypatch.setenv("ALERT_EMAIL_TO", "test@example.com")
    monkeypatch.setenv("ALERT_EMAIL_FROM", "test@example.com")
    monkeypatch.setenv("SMTP_HOST", "localhost")
    monkeypatch.setenv("SMTP_PORT", "25")
    assert check_env_requirements(minimal_config, auth_conf, logger=None) is True


def test_preflight_flags_invalid_alerting_env(monkeypatch, minimal_config):
    config = dict(minimal_config)
    config["ops"] = dict(config["ops"], require_alerting_env=True)
    auth_conf = {}
    monkeypatch.setenv("MONGO_URI", "mongodb://localhost:27017/cti")
    monkeypatch.setenv("MISTRAL_API_KEY", "test")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "not-a-url")
    monkeypatch.setenv("ALERT_EMAIL_TO", "test@example.com")
    monkeypatch.setenv("ALERT_EMAIL_FROM", "test@example.com")
    monkeypatch.setenv("SMTP_HOST", "localhost")
    monkeypatch.setenv("SMTP_PORT", "25")
    assert check_env_requirements(config, auth_conf, logger=None) is False
