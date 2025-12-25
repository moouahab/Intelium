import hashlib
import importlib
from pathlib import Path
from tools.download import NetworkPolicy, StorageTarget


def _get_source_module():
    return importlib.import_module("cti_core.Source")


def test_download_manager_downloaded(monkeypatch):
    source_module = _get_source_module()
    Source = source_module.Source
    policy = NetworkPolicy(enforce_https=False, block_private=False)
    storage = StorageTarget(base_dir=Path("docs"), theme="html", name="test")

    def fake_download_source(params, policy=None, storage=None, headers=None):
        return source_module.DownloadResult(
            status="downloaded",
            content="hello world",
            content_type="text/html",
        )

    monkeypatch.setattr(source_module, "download_source", fake_download_source)

    src = Source({"url": "http://example.com", "type": "html"})
    result = src.download_manager(policy=policy, storage=storage)

    assert result.status == "downloaded"
    assert src.status == "downloaded"
    assert src.content == "hello world"
    assert src.hash == source_module.compute_sha256_from_text("hello world")


def test_download_manager_error(monkeypatch):
    source_module = _get_source_module()
    Source = source_module.Source
    policy = NetworkPolicy(enforce_https=False, block_private=False)
    storage = StorageTarget(base_dir=Path("docs"), theme="api", name="api")

    def fake_download_source(params, policy=None, storage=None, headers=None):
        return source_module.DownloadResult(
            status="error",
            content=None,
            error="network failed",
        )

    monkeypatch.setattr(source_module, "download_source", fake_download_source)

    src = Source({"url": "http://example.com", "type": "api"})
    result = src.download_manager(policy=policy, storage=storage)

    assert result.status == "error"
    assert src.status == "error"
    assert src.error == "network failed"
    assert src.content is None
    assert src.hash is None


def test_download_manager_skipped(monkeypatch):
    source_module = _get_source_module()
    Source = source_module.Source
    policy = NetworkPolicy(enforce_https=False, block_private=False)
    storage = StorageTarget(base_dir=Path("docs"), theme="ignore", name="ignore")

    def fake_download_source(params, policy=None, storage=None, headers=None):
        return source_module.DownloadResult(status="skipped", content=None, error=None)

    monkeypatch.setattr(source_module, "download_source", fake_download_source)

    src = Source({"url": "http://example.com/ignore", "type": "ignore"})
    result = src.download_manager(policy=policy, storage=storage)
    assert result.status == "skipped"
    assert src.status == "skipped"
    assert src.content is None
    assert src.hash is None


def test_download_manager_binary_hash(monkeypatch):
    source_module = _get_source_module()
    Source = source_module.Source
    policy = NetworkPolicy(enforce_https=False, block_private=False)
    storage = StorageTarget(base_dir=Path("docs"), theme="image", name="image")
    binary_payload = b"\x89PNG\r\n"

    def fake_download_source(params, policy=None, storage=None, headers=None):
        return source_module.DownloadResult(
            status="downloaded",
            content=binary_payload,
            content_type="image/png",
        )

    monkeypatch.setattr(source_module, "download_source", fake_download_source)

    src = Source({"url": "http://example.com/image.png", "type": "image"})
    src.download_manager(policy=policy, storage=storage)

    expected_hash = hashlib.sha256(binary_payload).hexdigest()
    assert src.hash == expected_hash
