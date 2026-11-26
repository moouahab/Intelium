import pytest
from tools.providers.http import download
from tools.providers.http.download import NetworkPolicy, StorageTarget


class FakeResponse:
    def __init__(self, text="", content=b"", headers=None, status_code=200):
        self.text = text
        self.content = content or text.encode("utf-8")
        self.headers = headers or {}
        self.status_code = status_code
        self.encoding = "utf-8"
        self.closed = False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise download.network.requests.HTTPError(f"Status {self.status_code}")

    def iter_content(self, chunk_size=8192):
        data = self.content
        for i in range(0, len(data), chunk_size):
            yield data[i : i + chunk_size]

    def close(self):
        self.closed = True


def test_download_html(monkeypatch, tmp_path):
    def fake_get(url, timeout=10, stream=False, headers=None, proxies=None, verify=True, allow_redirects=False):
        return FakeResponse(text="<html>ok</html>", headers={"Content-Type": "text/html"})
    monkeypatch.setattr("tools.providers.http.network.requests.get", fake_get)
    policy = NetworkPolicy(enforce_https=False, block_private=False)
    result = download.download_source({"url": "http://example.com", "type": "html"}, policy=policy)
    assert result.status == "downloaded"
    assert "<html>" in result.content
    assert "text/html" in result.content_type


def test_download_api_content_type_error(monkeypatch):
    def fake_get(url, timeout=10, stream=False, headers=None, proxies=None, verify=True, allow_redirects=False):
        return FakeResponse(text="not json", headers={"Content-Type": "text/html"})
    monkeypatch.setattr("tools.providers.http.network.requests.get", fake_get)
    policy = NetworkPolicy(enforce_https=False, block_private=False)
    result = download.download_source({"url": "http://example.com/api", "type": "api"}, policy=policy)
    assert result.status == "error"
    assert "Type de contenu non supporté" in result.error


def test_download_image(monkeypatch):
    def fake_get(url, timeout=10, stream=False, headers=None, proxies=None, verify=True, allow_redirects=False):
        return FakeResponse(content=b"\x89PNG", headers={"Content-Type": "image/png"})
    monkeypatch.setattr("tools.providers.http.network.requests.get", fake_get)
    policy = NetworkPolicy(enforce_https=False, block_private=False)
    result = download.download_source({"url": "http://example.com/image", "type": "image"}, policy=policy)
    assert result.status == "downloaded"
    assert result.content.startswith(b"\x89PNG")
    assert "image/png" in result.content_type


def test_download_ignore_type_skipped():
    policy = NetworkPolicy(enforce_https=False, block_private=False)
    result = download.download_source({"url": "http://example.com/ignore", "type": "ignore"}, policy=policy)
    assert result.status == "skipped"
    assert result.content is None


def test_download_unknown_type_fallback(monkeypatch):
    def fake_get(url, timeout=10, stream=False, headers=None, proxies=None, verify=True, allow_redirects=False):
        return FakeResponse(text="fallback html", headers={"Content-Type": "text/html"})
    monkeypatch.setattr("tools.providers.http.network.requests.get", fake_get)
    policy = NetworkPolicy(enforce_https=False, block_private=False)
    result = download.download_source({"url": "http://example.com/unknown", "type": "unsupported"}, policy=policy)
    assert result.status == "downloaded"
    assert "fallback html" in result.content


def test_download_txt(monkeypatch):
    def fake_get(url, timeout=10, stream=False, headers=None, proxies=None, verify=True, allow_redirects=False):
        return FakeResponse(text="plain text", headers={"Content-Type": "text/plain"})
    monkeypatch.setattr("tools.providers.http.network.requests.get", fake_get)
    policy = NetworkPolicy(enforce_https=False, block_private=False)
    result = download.download_source({"url": "http://example.com/file.txt", "type": "txt"}, policy=policy)
    assert result.status == "downloaded"
    assert result.content == "plain text"
    assert "text/plain" in result.content_type


def test_download_respects_max_bytes_stream(monkeypatch):
    def fake_get(url, timeout=10, stream=False, headers=None, proxies=None, verify=True, allow_redirects=False):
        return FakeResponse(content=b"a" * 10, headers={"Content-Type": "text/plain"})
    monkeypatch.setattr("tools.providers.http.network.requests.get", fake_get)
    policy = NetworkPolicy(enforce_https=False, block_private=False, max_bytes=5)
    result = download.download_source({"url": "http://example.com/file.txt", "type": "txt"}, policy=policy)
    assert result.status == "error"
    assert "taille > limite" in result.error


@pytest.mark.parametrize("kind,mime,extension,binary", [
    ("html", "text/html", ".html", False),
    ("api", "application/json", ".json", False),
    ("xml", "application/xml", ".xml", False),
    ("pdf", "application/pdf", ".pdf", True),
    ("csv", "text/csv", ".csv", False),
    ("txt", "text/plain", ".txt", False),
    ("image", "image/png", ".png", True),
    ("unknown", "text/html", ".html", False),
])
def test_download_format_preserves_payload_and_storage(monkeypatch, tmp_path, kind, mime, extension, binary):
    payload = b'{"message":"audit"}'
    response = FakeResponse(content=payload, headers={"Content-Type": mime})
    monkeypatch.setattr(download.network, "get_response", lambda *a, **kw: response)
    if binary:
        def unexpected_decode(*args, **kwargs):
            pytest.fail("Binary downloads must not be decoded as text")
        monkeypatch.setattr(download, "ensure_text", unexpected_decode)
    result = download.download_source(
        {"url": "https://example.com/file", "type": kind},
        NetworkPolicy(sandbox_dir=str(tmp_path)),
        StorageTarget(tmp_path, "fixtures", "artifact"),
    )
    assert result.status == "downloaded"
    assert result.content == (payload if binary else payload.decode())
    assert result.saved_path.suffix == extension
    assert result.saved_path.read_bytes() == payload
    assert result.content_type == mime
    assert response.closed
