from tools.config_validator import validate_config


def test_validate_config_output_and_auth():
    conf = {
        "output": {"format": "yaml"},
        "authentication": {"hosts": {"api.example.com": "bad"}},
        "crawler": {"url_normalizer": "unknown"},
    }
    errors, warnings = validate_config(conf)
    assert errors
    assert any("output.format" in e or "output" in e for e in errors)
    assert any("authentication.hosts" in e for e in errors)
