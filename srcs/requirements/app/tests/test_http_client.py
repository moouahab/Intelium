import importlib
from concurrent.futures import ThreadPoolExecutor

from tools.providers.http.download_types import NetworkPolicy, DownloadResult


def test_http_client_blocks_when_robots_forbid(monkeypatch):
    client_module = importlib.import_module("tools.providers.http.client")

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
    client_module = importlib.import_module("tools.providers.http.client")

    captured = {}

    def fake_download_with_context(source, ctx, storage=None):
        captured["max_bytes"] = ctx.policy.max_bytes
        return DownloadResult(status="downloaded", content="ok", content_type="text/plain")

    monkeypatch.setattr(client_module, "download_with_context", fake_download_with_context)
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
    client_module = importlib.import_module("tools.providers.http.client")
    req_ctx_module = importlib.import_module("tools.providers.http.request_context")

    monkeypatch.setattr(client_module.RobotsDelayPolicy, "is_allowed", lambda self, url, respect_override=None: True)
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "wait", lambda self, url, delay_override=None: None)

    captured_headers = {}

    def fake_download_with_context(source, ctx, storage=None):
        captured_headers.update(ctx.headers or {})
        captured_headers["proxy"] = ctx.proxy
        return DownloadResult(status="downloaded", content="ok", content_type="text/plain")

    monkeypatch.setattr(client_module, "download_with_context", fake_download_with_context)

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
    client_module = importlib.import_module("tools.providers.http.client")
    calls = {"count": 0}

    def fake_download_with_context(source, ctx, storage=None):
        calls["count"] += 1
        if calls["count"] == 1:
            return DownloadResult(status="http-error", content=None, status_code=503, error="HTTP 503")
        return DownloadResult(status="downloaded", content="ok", status_code=200)

    monkeypatch.setattr(client_module, "download_with_context", fake_download_with_context)
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
    client_module = importlib.import_module("tools.providers.http.client")
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


def test_http_client_headless_shortcuts_download(monkeypatch):
    client_module = importlib.import_module("tools.providers.http.client")
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "is_allowed", lambda self, url, respect_override=None: True)
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "wait", lambda self, url, delay_override=None: None)
    called = {"headless": 0, "download": 0}

    class FakeHeadlessStrategy:
        def fetch(self, url, timeout=10, user_agent=None, proxy=None):
            called["headless"] += 1
            return "<html>headless</html>"

    def fake_download_with_context(source, ctx, storage=None):
        called["download"] += 1
        return DownloadResult(status="downloaded", content="ok", content_type="text/plain")

    monkeypatch.setattr(client_module, "download_with_context", fake_download_with_context)

    client = client_module.HttpClient(
        policy=NetworkPolicy(enforce_https=False, block_private=False),
        auth_conf={},
        respect_robots=False,
        crawl_delay=0,
        headless_strategy=FakeHeadlessStrategy(),
    )

    result = client.fetch({"url": "http://example.com", "type": "html", "overrides": {"headless": True}})

    assert result.status == "downloaded"
    assert "headless" in result.content
    assert called["headless"] == 1
    assert called["download"] == 0


def test_http_client_enforces_max_bytes_stream(monkeypatch):
    client_module = importlib.import_module("tools.providers.http.client")
    download_module = importlib.import_module("tools.providers.http.download")

    class FakeResponse:
        def __init__(self, content: bytes, ctype="text/plain"):
            self.content = content
            self.headers = {"Content-Type": ctype, "Content-Length": str(len(content))}
            self.status_code = 200
            self.encoding = "utf-8"
            self.closed = False

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size=8192):
            data = self.content
            for i in range(0, len(data), chunk_size):
                yield data[i : i + chunk_size]

        def close(self):
            self.closed = True

    def fake_get(url, timeout=10, stream=True, headers=None, proxies=None, verify=True, allow_redirects=False):
        return FakeResponse(b"a" * 10)

    monkeypatch.setattr(download_module.network.requests, "get", fake_get)
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "is_allowed", lambda self, url, respect_override=None: True)
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "wait", lambda self, url, delay_override=None: None)

    client = client_module.HttpClient(
        policy=NetworkPolicy(enforce_https=False, block_private=False, max_bytes=5),
        auth_conf={},
        respect_robots=False,
        crawl_delay=0,
    )

    res = client.fetch({"url": "http://example.com/large", "type": "txt"})
    assert res.status == "error"
    assert "taille > limite" in (res.error or "")


def test_http_client_uses_proxies_round_robin(monkeypatch):
    client_module = importlib.import_module("tools.providers.http.client")
    captured = []

    def fake_download_with_context(source, ctx, storage=None):
        captured.append(ctx.proxy)
        return DownloadResult(status="downloaded", content="ok", content_type="text/plain")

    monkeypatch.setattr(client_module, "download_with_context", fake_download_with_context)
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "is_allowed", lambda self, url, respect_override=None: True)
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "wait", lambda self, url, delay_override=None: None)

    client = client_module.HttpClient(
        policy=NetworkPolicy(enforce_https=False, block_private=False),
        auth_conf={},
        respect_robots=False,
        crawl_delay=0,
        proxies=["http://proxy1", "http://proxy2"],
    )

    client.fetch({"url": "http://a.com", "type": "txt"})
    client.fetch({"url": "http://b.com", "type": "txt"})

    assert captured[0] == {"http": "http://proxy1", "https": "http://proxy1"}
    assert captured[1] == {"http": "http://proxy2", "https": "http://proxy2"}


def test_http_client_respect_robots_override(monkeypatch):
    client_module = importlib.import_module("tools.providers.http.client")
    calls = {"allowed": []}

    def fake_is_allowed(self, url, respect_override=None):
        calls["allowed"].append(respect_override)
        return False if respect_override else True

    monkeypatch.setattr(client_module.RobotsDelayPolicy, "is_allowed", fake_is_allowed)
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "wait", lambda self, url, delay_override=None: None)

    def fake_download_with_context(source, ctx, storage=None):
        return DownloadResult(status="downloaded", content="ok", content_type="text/plain")

    monkeypatch.setattr(client_module, "download_with_context", fake_download_with_context)

    client = client_module.HttpClient(
        policy=NetworkPolicy(enforce_https=False, block_private=False),
        auth_conf={},
        respect_robots=True,
        crawl_delay=0,
    )

    # override respect_robots=False doit forcer l'accès
    res = client.fetch({"url": "http://example.com", "type": "txt", "overrides": {"respect_robots": False}})
    assert res.status == "downloaded"
    assert calls["allowed"][0] is False


def test_http_client_blocks_private_dns_resolution(monkeypatch):
    client_module = importlib.import_module("tools.providers.http.client")
    network_module = importlib.import_module("tools.providers.http.network")

    # Force la résolution à retourner une IP privée
    monkeypatch.setattr(network_module, "resolve_host_ips", lambda host: ["192.168.0.10"])
    # Évite l'appel réseau
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "is_allowed", lambda self, url, respect_override=None: True)
    monkeypatch.setattr(client_module.RobotsDelayPolicy, "wait", lambda self, url, delay_override=None: None)

    client = client_module.HttpClient(
        policy=NetworkPolicy(enforce_https=False, block_private=True),
        auth_conf={},
        respect_robots=False,
        crawl_delay=0,
    )

    res = client.fetch({"url": "http://example.com", "type": "txt"})

    assert res.status == "error"
    assert "réseau privé" in (res.error or "").lower()


def test_http_client_user_agent_and_proxy_increment_thread_safe():
    client_module = importlib.import_module("tools.providers.http.client")

    client = client_module.HttpClient(
        policy=NetworkPolicy(enforce_https=False, block_private=False),
        auth_conf={},
        respect_robots=False,
        crawl_delay=0,
        user_agents=["ua"],
        proxies=["http://proxy"],
    )

    calls = 200
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(lambda _: client._next_user_agent(), range(calls)))
        list(executor.map(lambda _: client._next_proxy(), range(calls)))

    assert client._ua_idx == calls
    assert client._proxy_idx == calls
