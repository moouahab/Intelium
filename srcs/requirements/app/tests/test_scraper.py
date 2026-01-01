import importlib

from tools.cache import CacheManager, CacheEntry
from tools.providers.http.download_types import DownloadResult


def test_scraper_download_and_cache(dummy_config_model, fake_client_factory, tmp_path):
    scraper_module = importlib.import_module("cti_core.scraper")
    source_module = importlib.import_module("cti_core.Source")

    root_url = "http://example.com"
    child_url = "http://example.com/next"
    fake_client = fake_client_factory({root_url: '<a href="/next">next</a>', child_url: "done"})
    root_source = source_module.Source({"url": root_url, "type": "html", "name": "root"})
    config_model = dummy_config_model([root_source])
    cache_file = tmp_path / "cache.json"
    cache = CacheManager(cache_file, auto_save=False)

    scraper = scraper_module.Scraper(config_model, cache, http_client=fake_client)
    scraper.run()

    assert len(fake_client.calls) == 2  # root + child
    assert cache.get(root_url).status == "downloaded"
    assert cache.get(child_url).status == "downloaded"


def test_scraper_uses_cache(dummy_config_model, fake_client_factory, tmp_path):
    scraper_module = importlib.import_module("cti_core.scraper")
    source_module = importlib.import_module("cti_core.Source")

    root_url = "http://example.com"
    fake_client = fake_client_factory({root_url: "ok"})
    root_source = source_module.Source({"url": root_url, "type": "html", "name": "root"})
    config_model = dummy_config_model([root_source])
    cache_file = tmp_path / "cache.json"
    cache = CacheManager(cache_file, auto_save=False)
    cache.update(CacheEntry(url=root_url, type="html", hash="hash", status="downloaded", date="now"))

    scraper = scraper_module.Scraper(config_model, cache, http_client=fake_client)
    scraper.run()

    # aucune nouvelle requête car cache
    assert len(fake_client.calls) == 0
    assert cache.get(root_url).status == "skipped-cache"


def test_scraper_cache_hit_parses_saved_content(dummy_config_model, fake_client_factory, tmp_path):
    scraper_module = importlib.import_module("cti_core.scraper")
    source_module = importlib.import_module("cti_core.Source")

    root_url = "http://example.com"
    fake_client = fake_client_factory({root_url: "should-not-fetch"})
    root_source = source_module.Source({"url": root_url, "type": "html", "name": "root"})
    config_model = dummy_config_model([root_source])
    cache_file = tmp_path / "cache.json"
    cache = CacheManager(cache_file, auto_save=False)

    saved_path = tmp_path / "cached.html"
    saved_path.write_text("<html><a href='#'>cached content</a></html>")
    cache.update(CacheEntry(url=root_url, type="html", hash="hash", status="downloaded", date="now", saved_path=str(saved_path)))

    scraper = scraper_module.Scraper(config_model, cache, http_client=fake_client)
    results = scraper.run()

    assert len(fake_client.calls) == 0  # cache used
    by_url = {r["url"]: r for r in results}
    assert "cached content" in " ".join(by_url[root_url].get("extracted", []))


def test_scraper_offline_without_cache_marks_offline(dummy_config_model, fake_client_factory, tmp_path):
    scraper_module = importlib.import_module("cti_core.scraper")
    source_module = importlib.import_module("cti_core.Source")

    root_url = "http://example.com"
    root_source = source_module.Source({"url": root_url, "type": "html", "name": "root"})
    config_model = dummy_config_model([root_source])
    # Active le mode offline
    config_model.network_policy.offline = True
    cache = CacheManager(tmp_path / "cache.json", auto_save=False)
    fake_client = fake_client_factory({root_url: "should-not-fetch"})

    scraper = scraper_module.Scraper(config_model, cache, http_client=fake_client)
    results = scraper.run()

    assert len(fake_client.calls) == 0
    by_url = {r["url"]: r for r in results}
    assert by_url[root_url]["status"] == "offline"


def test_scraper_concurrent_workers(dummy_config_model, fake_client_factory, tmp_path):
    scraper_module = importlib.import_module("cti_core.scraper")
    source_module = importlib.import_module("cti_core.Source")

    root_url = "http://example.com"
    child_url = "http://example.com/next"
    fake_client = fake_client_factory({root_url: '<a href="/next">next</a>', child_url: "done"})
    root_source = source_module.Source({"url": root_url, "type": "html", "name": "root"})
    config_model = dummy_config_model([root_source], max_concurrent=2)
    cache_file = tmp_path / "cache.json"
    cache = CacheManager(cache_file, auto_save=False)

    scraper = scraper_module.Scraper(config_model, cache, http_client=fake_client)
    scraper.run()

    assert set(fake_client.calls) == {root_url, child_url}
    assert cache.get(root_url).status == "downloaded"
    assert cache.get(child_url).status == "downloaded"


def test_scraper_e2e_multi_sources_with_overrides(dummy_config_model, tmp_path):
    scraper_module = importlib.import_module("cti_core.scraper")
    source_module = importlib.import_module("cti_core.Source")
    cache_file = tmp_path / "cache.json"
    cache = CacheManager(cache_file, auto_save=False)

    # Deux sources, l'une avec override robots/delay/max_bytes
    s1 = source_module.Source({"url": "http://a.com", "type": "html", "name": "a"})
    s1.overrides = {"respect_robots": False, "crawl_delay_seconds": "0", "max_bytes": "5"}
    s2 = source_module.Source({"url": "http://b.com", "type": "html", "name": "b"})

    content_map = {
        "http://a.com": '<a href="/next-a">A</a>',
        "http://a.com/next-a": "A-child",
        "http://b.com": "B-root",
    }

    class MultiFakeClient:
        def __init__(self):
            self.calls = []

        def fetch(self, source, storage=None):
            url = source.get("url")
            self.calls.append(url)
            content = content_map.get(url, "")
            return DownloadResult(status="downloaded", content=content, content_type="text/html", saved_path=storage.base_dir / "f")

    config_model = dummy_config_model([s1, s2], max_concurrent=2)
    scraper = scraper_module.Scraper(config_model, cache, http_client=MultiFakeClient())
    results = scraper.run()

    # Vérifie que toutes les URLs sont passées, y compris l'enfant de a.com
    urls = {r["url"] for r in results}
    assert "http://a.com" in urls
    assert "http://a.com/next-a" in urls
    assert "http://b.com" in urls
    # Statuts en cache
    assert cache.get("http://a.com").status == "downloaded"
    assert cache.get("http://a.com/next-a").status == "downloaded"
    assert cache.get("http://b.com").status == "downloaded"


def test_scraper_records_keyword_hits(dummy_config_model, fake_client_factory, tmp_path):
    scraper_module = importlib.import_module("cti_core.scraper")
    source_module = importlib.import_module("cti_core.Source")

    root_url = "http://example.com"
    child_url = "http://example.com/next"
    keywords = {"indicator": ["next"], "misc": ["done"]}
    fake_client = fake_client_factory(
        {root_url: '<a href="/next">Next link</a>', child_url: "done and dusted"},
        content_type="text/html",
    )
    root_source = source_module.Source({"url": root_url, "type": "html", "name": "root"})
    config_model = dummy_config_model([root_source], keywords=keywords)
    cache_file = tmp_path / "cache.json"
    cache = CacheManager(cache_file, auto_save=False)

    scraper = scraper_module.Scraper(config_model, cache, http_client=fake_client)
    results = scraper.run()

    by_url = {r["url"]: r for r in results}
    assert "indicator" in by_url[root_url].get("keywords", {})
    assert "next" in by_url[root_url]["keywords"]["indicator"]
    assert "misc" in by_url[child_url].get("keywords", {})
    assert "done" in by_url[child_url]["keywords"]["misc"]


def test_scraper_respects_global_page_quota(dummy_config_model, fake_client_factory, tmp_path):
    scraper_module = importlib.import_module("cti_core.scraper")
    source_module = importlib.import_module("cti_core.Source")

    s1 = source_module.Source({"url": "http://a.com", "type": "html", "name": "a"})
    s2 = source_module.Source({"url": "http://b.com", "type": "html", "name": "b"})
    fake_client = fake_client_factory({"http://a.com": "A", "http://b.com": "B"})
    cache = CacheManager(tmp_path / "cache.json", auto_save=False)
    config_model = dummy_config_model([s1, s2], global_max_pages=1)

    scraper = scraper_module.Scraper(config_model, cache, http_client=fake_client)
    results = scraper.run()

    # Une seule page consommée, la seconde source est marquée quota
    assert "http://a.com" in [r["url"] for r in results]
    quota_records = [r for r in results if r["url"] == "http://b.com"]
    assert quota_records and quota_records[0]["status"] == "skipped-quota"
    assert fake_client.calls == ["http://a.com"]
