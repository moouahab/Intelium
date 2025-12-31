from urllib.parse import urlparse

from cti_core.runner import _validate_allowlist


class DummySource:
    def __init__(self, url, name="src"):
        self.url = url
        self.name = name
        self.type = "html"


class DummyLogger:
    def __init__(self):
        self.errors = []

    def error(self, msg, *args):
        self.errors.append(msg % args if args else msg)

    def warning(self, msg, *args):
        pass


class DummyConfig:
    def __init__(self, allow_domains, sources):
        self.network_policy = type("NP", (), {"allow_domains": allow_domains})()
        self.crawler_settings = {"allow_domains": set()}
        self.source_objects = sources


def test_validate_allowlist_accepts_in_scope():
    cfg = DummyConfig({"example.com"}, [DummySource("http://example.com/path", "ok")])
    logger = DummyLogger()
    assert _validate_allowlist(cfg, logger) is True
    assert not logger.errors


def test_validate_allowlist_rejects_out_of_scope():
    cfg = DummyConfig({"example.com"}, [DummySource("http://evil.com", "bad")])
    logger = DummyLogger()
    assert _validate_allowlist(cfg, logger) is False
    assert any("Sources hors allowlist" in e for e in logger.errors)
