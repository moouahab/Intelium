from pathlib import Path
from tools.cache import CacheManager, CacheEntry, CacheRegistry


def test_cache_manager_load_and_update(tmp_path):
    cache_file = tmp_path / "data" / "cache.json"
    manager = CacheManager(cache_file, auto_save=False)
    assert manager.get("https://example.com") is None

    entry = CacheEntry(url="https://example.com", type="html", hash="abc", date="2024-01-01")
    manager.update(entry)
    assert manager.get("https://example.com").hash == "abc"

    manager.save()
    # reload
    manager2 = CacheManager(cache_file, auto_save=False)
    cached = manager2.get("https://example.com")
    assert cached is not None
    assert cached.hash == "abc"
    assert cached.date == "2024-01-01"


def test_cache_manager_has_changed(tmp_path):
    cache_file = tmp_path / "cache.json"
    manager = CacheManager(cache_file, auto_save=False)
    entry = CacheEntry(url="https://example.com", type="html", hash="abc")
    manager.update(entry)

    assert manager.has_changed("https://example.com", "abc") is False
    assert manager.has_changed("https://example.com", "def") is True
    assert manager.has_changed("https://new.com", "abc") is True


def test_cache_record_scrape_auto_save(tmp_path):
    cache_file = tmp_path / "data" / "cache.json"
    manager = CacheManager(cache_file, auto_save=True)
    manager.record_scrape(
        url="https://target.com/page",
        source_type="html",
        status="downloaded",
        hash_value="deadbeef",
        date="2024-02-02",
        error=None,
        saved_path="/tmp/file.html",
    )
    assert cache_file.exists()
    reloaded = CacheManager(cache_file, auto_save=False)
    entry = reloaded.get("https://target.com/page")
    assert entry is not None
    assert entry.status == "downloaded"
    assert entry.hash == "deadbeef"
    assert entry.date == "2024-02-02"
    assert entry.saved_path == "/tmp/file.html"


def test_cache_registry_separate_files(tmp_path):
    base_dir = tmp_path / "caches"
    registry = CacheRegistry(base_dir, auto_save=True)
    registry.record_scrape(
        url="https://a.example.com/page",
        source_type="html",
        status="downloaded",
        hash_value="aaa",
    )
    registry.record_scrape(
        url="https://b.example.com/page",
        source_type="html",
        status="downloaded",
        hash_value="bbb",
    )

    a_cache = base_dir / "a-example-com.json"
    b_cache = base_dir / "b-example-com.json"

    assert a_cache.exists()
    assert b_cache.exists()

    reg2 = CacheRegistry(base_dir, auto_save=False)
    assert reg2.get("https://a.example.com/page").hash == "aaa"
    assert reg2.get("https://b.example.com/page").hash == "bbb"
