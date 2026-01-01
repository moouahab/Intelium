from pathlib import Path
import pytest
from tools.providers.http.download_types import NetworkPolicy, StorageTarget, DownloadResult


class DummyConfigModel:
    def __init__(
        self,
        sources,
        tmp_path: Path,
        max_concurrent: int = 1,
        keywords: dict | None = None,
        global_max_pages: int | None = None,
        global_max_bytes: int | None = None,
    ):
        self.source_objects = sources
        self.yaml_config = {
            "crawler": {
                "max_depth": 1,
                "same_domain_only": True,
                "respect_robots": False,
                "crawl_delay_seconds": 0,
                "max_concurrent": max_concurrent,
            }
        }
        self.network_policy = NetworkPolicy(enforce_https=False, block_private=False)
        self.crawler_settings = {
            "max_depth": 1,
            "max_pages": None,
            "same_domain_only": True,
            "allow_domains": set(),
            "respect_robots": False,
            "crawl_delay_seconds": 0,
            "max_concurrent": max_concurrent,
            "global_max_pages": global_max_pages,
            "global_max_bytes": global_max_bytes,
        }
        self.http_settings = {
            "respect_robots": False,
            "crawl_delay_seconds": 0,
            "retry_attempts": 2,
            "retry_backoff_seconds": 0.5,
        }
        self.keywords = keywords or {}
        self.scraping_settings = {
            "html": {"extract": [{"tag": "a"}], "include_attributes": []},
            "api": {},
            "xml": {},
            "csv": {},
            "pdf": {},
            "image": {},
            "txt": {},
        }
        self.auth_settings = {}
        self.tmp_path = tmp_path

    def build_storage_target(self, source):
        return StorageTarget(base_dir=self.tmp_path, theme=source.type, name=source.name or "source")


@pytest.fixture
def dummy_config_model(tmp_path):
    def _build(
        sources,
        max_concurrent: int = 1,
        keywords: dict | None = None,
        global_max_pages: int | None = None,
        global_max_bytes: int | None = None,
    ):
        return DummyConfigModel(
            sources,
            tmp_path,
            max_concurrent=max_concurrent,
            keywords=keywords,
            global_max_pages=global_max_pages,
            global_max_bytes=global_max_bytes,
        )

    return _build


@pytest.fixture
def minimal_config():
    return {
        "ops": {
            "strict_env": True,
            "require_auth_env": True,
            "require_alerting_env": False,
            "required_env": [],
        },
        "cache": {"backend": "mongo"},
        "output": {"ai_report": {"enabled": True, "command": "python3 scripts/mistral_llm.py"}},
    }


@pytest.fixture
def fake_client_factory():
    """
    Fabrique un faux client HTTP basé sur une table url->content.
    Chaque instance expose l'attribut 'calls' pour inspection.
    """

    def _build(content_map: dict[str, str], content_type: str = "text/html"):
        class FakeClient:
            def __init__(self):
                self.calls = []
            def fetch(self, source, storage=None):
                url = source.get("url")
                self.calls.append(url)
                content = content_map.get(url, "")
                saved = storage.base_dir / "file" if storage else None
                return DownloadResult(status="downloaded", content=content, content_type=content_type, saved_path=saved)
        return FakeClient()
    return _build
