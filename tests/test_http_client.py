import importlib

from tools.download_types import NetworkPolicy, DownloadResult


def test_http_client_blocks_when_robots_forbid(monkeypatch):
    client_module = importlib.import_module("tools.http.client")

    # Force robots à refuser
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "is_allowed", lambda self, url, respect_override=None: False)
    # Empêche toute attente
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "wait", lambda self, url, delay_override=None: None)

    client = client_module.HttpClient(
        policy=NetworkPolicy(enforce_https=False, block_private=False),
        auth_conf={},
        respect_robots=True,
        crawl_delay=0,
    )

    result = client.fetch({"url": "http://example.com/blocked", "type": "html"})

    assert result.status == "blocked-robots"


def test_http_client_applies_max_bytes_override(monkeypatch):
    client_module = importlib.import_module("tools.http.client")

    captured = {}

    def fake_download_source(source, policy, storage=None, headers=None, proxies=None):
        captured["max_bytes"] = policy.max_bytes
        return DownloadResult(status="downloaded", content="ok", content_type="text/plain")

    monkeypatch.setattr(client_module, "download_source", fake_download_source)
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "is_allowed", lambda self, url, respect_override=None: True)
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "wait", lambda self, url, delay_override=None: None)

    client = client_module.HttpClient(
        policy=NetworkPolicy(enforce_https=False, block_private=False, max_bytes=1000),
        auth_conf={},
        respect_robots=False,
        crawl_delay=0,
    )

    client.fetch({"url": "http://example.com/file", "type": "api", "overrides": {"max_bytes": 10}})

    assert captured["max_bytes"] == 10


def test_request_context_applies_user_agent_and_headers(monkeypatch):
    client_module = importlib.import_module("tools.http.client")
    req_ctx_module = importlib.import_module("tools.http.request_context")

    monkeypatch.setattr(client_module.RobotsDelayPolicy, "is_allowed", lambda self, url, respect_override=None: True)
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "wait", lambda self, url, delay_override=None: None)

    captured_headers = {}

    def fake_download_source(source, policy, storage=None, headers=None, proxies=None):
        captured_headers.update(headers or {})
        captured_headers["proxy"] = proxies
        return DownloadResult(status="downloaded", content="ok", content_type="text/plain")

    monkeypatch.setattr(client_module, "download_source", fake_download_source)

    client = client_module.HttpClient(
        policy=NetworkPolicy(enforce_https=False, block_private=False),
        auth_conf={"headers": {"Authorization": "token"}},
        respect_robots=False,
        crawl_delay=0,
        user_agent="default-UA",
        user_agents=["ua1", "ua2"],
        proxies=["http://proxy1", "http://proxy2"],
    )

    client.fetch({"url": "http://example.com/file", "type": "api", "overrides": {"headers": {"X-Test": "1"}, "user_agent": "override-UA"}})

    assert captured_headers["Authorization"] == "token"
    assert captured_headers["X-Test"] == "1"
    assert captured_headers["User-Agent"] == "override-UA"
    assert captured_headers["proxy"] == {"http": "http://proxy1", "https": "http://proxy1"}


def test_http_client_retries_on_http_error(monkeypatch):
    client_module = importlib.import_module("tools.http.client")
    calls = {"count": 0}

    def fake_download_source(source, policy, storage=None, headers=None, proxies=None):
        calls["count"] += 1
        if calls["count"] == 1:
            return DownloadResult(status="http-error", content=None, status_code=503, error="HTTP 503")
        return DownloadResult(status="downloaded", content="ok", status_code=200)

    monkeypatch.setattr(client_module, "download_source", fake_download_source)
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "is_allowed", lambda self, url, respect_override=None: True)
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "wait", lambda self, url, delay_override=None: None)

    client = client_module.HttpClient(
        policy=NetworkPolicy(enforce_https=False, block_private=False),
        auth_conf={},
        respect_robots=False,
        crawl_delay=0,
        retries=2,
        backoff_seconds=0,
    )

    result = client.fetch({"url": "http://example.com/file", "type": "api"})

    assert result.status == "downloaded"
    assert calls["count"] == 2


def test_http_client_backoff_adaptive(monkeypatch):
    client_module = importlib.import_module("tools.http.client")
    res_429 = DownloadResult(status="http-error", content=None, status_code=429)
    res_403 = DownloadResult(status="http-error", content=None, status_code=403)
    client = client_module.HttpClient(
        policy=NetworkPolicy(enforce_https=False, block_private=False),
        auth_conf={},
        backoff_seconds=1,
    )

    delay_429 = client._backoff_delay(res_429, attempt=0)
    delay_403 = client._backoff_delay(res_403, attempt=0)

    assert delay_429 > delay_403
