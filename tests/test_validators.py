from tools.validators import validate_output, validate_auth
from tools.http.url_utils import resolve_normalizer
from tools.validators import validate_crawler


def test_validate_output_format_and_ai_report_dict():
    errs = validate_output({"format": "yaml"})
    assert errs and "format" in errs[0]
    errs = validate_output({"ai_report": "bad"})
    assert errs and "ai_report" in errs[0]
    errs = validate_output({"format": "markdown", "ai_report": {"enabled": False}})
    assert errs == []


def test_resolve_normalizer_options():
    assert resolve_normalizer("strip")(" URL ") == "URL"
    assert resolve_normalizer("lower")("HTTPS://EXAMPLE.COM") == "https://example.com"
    assert resolve_normalizer("strip-lower")(" HTTP://ExAmpLe ") == "http://example"
    errs = validate_crawler({"url_normalizer": "unknown"})
    assert errs and "url_normalizer" in errs[0]


def test_validate_auth_hosts_structure():
    errs = validate_auth({"hosts": {"api.example.com": "bad"}})
    assert errs and "hosts.api.example.com" in errs[0]
    errs_ok = validate_auth({"hosts": {"api.example.com": {"Authorization": "Bearer token"}}})
    assert errs_ok == []
