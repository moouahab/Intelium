import importlib
from pathlib import Path

from tools.cache import CacheManager
from tools.download_types import DownloadResult


def test_e2e_scrape_to_report(tmp_path, dummy_config_model):
    scraper_module = importlib.import_module("cti_core.scraper")
    source_module = importlib.import_module("cti_core.Source")
    runner_module = importlib.import_module("cti_core.runner")
    report_module = importlib.import_module("tools.report")

    root_url = "http://example.com"
    root_source = source_module.Source({"url": root_url, "type": "html", "name": "root"})
    config_model = dummy_config_model([root_source])

    cache_file = tmp_path / "cache.json"
    cache = CacheManager(cache_file, auto_save=False)

    class FakeClient:
        def fetch(self, source, storage=None):
            return DownloadResult(status="downloaded", content="<html>ok</html>", content_type="text/html")

    scraper = scraper_module.Scraper(config_model, cache, http_client=FakeClient())
    results = scraper.run()

    output_conf = {
        "format": "markdown",
        "file": tmp_path / "report.md",
        "split_per_source": True,
        "detail_dir": tmp_path / "sources",
        "language": "fr",
        "ai_report": {"enabled": False},
    }
    report_path = report_module.write_report(results, output_conf)

    assert report_path.exists()
    detail_file = tmp_path / "sources" / "root.md"
    assert detail_file.exists()


def test_runner_ai_report_with_prompt_path(tmp_path, monkeypatch, dummy_config_model):
    runner_module = importlib.import_module("cti_core.runner")
    scraper_module = importlib.import_module("cti_core.scraper")
    source_module = importlib.import_module("cti_core.Source")
    report_module = importlib.import_module("tools.report")

    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("PROMPT {results_json}")

    root_url = "http://example.com"
    root_source = source_module.Source({"url": root_url, "type": "html", "name": "root"})
    config_model = dummy_config_model([root_source])
    cache_file = tmp_path / "cache.json"
    cache = CacheManager(cache_file, auto_save=False)

    class FakeClient:
        def fetch(self, source, storage=None):
            return DownloadResult(status="downloaded", content="<html>ok</html>", content_type="text/html")

    scraper = scraper_module.Scraper(config_model, cache, http_client=FakeClient())
    results = scraper.run()

    # Mock LLM call
    monkeypatch.setattr("tools.ai_report._run_llm", lambda cmd, prompt, timeout=120, **kwargs: "AI OK")

    output_conf = {
        "format": "markdown",
        "file": tmp_path / "report.md",
        "split_per_source": True,
        "detail_dir": tmp_path / "sources",
        "language": "fr",
        "ai_report": {"enabled": True, "command": "echo ai", "prompt_path": prompt_file, "output": tmp_path / "ai.md"},
    }
    report_path = report_module.write_report(results, output_conf)
    ai_path = runner_module.generate_ai_report(results, output_conf.get("ai_report", {}))

    assert report_path.exists()
    assert ai_path == output_conf["ai_report"]["output"]
    assert ai_path.exists()


def test_e2e_multi_sources_overrides_and_reports(tmp_path, dummy_config_model, monkeypatch):
    scraper_module = importlib.import_module("cti_core.scraper")
    source_module = importlib.import_module("cti_core.Source")
    report_module = importlib.import_module("tools.report")
    runner_module = importlib.import_module("cti_core.runner")

    s1 = source_module.Source({"url": "http://a.com", "type": "html", "name": "a"})
    s1.overrides = {"respect_robots": False, "crawl_delay_seconds": "0", "max_bytes": "5"}
    s2 = source_module.Source({"url": "http://b.com", "type": "html", "name": "b"})
    config_model = dummy_config_model([s1, s2], max_concurrent=2)
    cache_file = tmp_path / "cache.json"
    cache = CacheManager(cache_file, auto_save=False)

    content_map = {
        "http://a.com": '<a href="/next-a">A</a>',
        "http://a.com/next-a": "A-child",
        "http://b.com": "B-root",
    }

    class FakeClient:
        def __init__(self):
            self.calls = []

        def fetch(self, source, storage=None):
            url = source.get("url")
            self.calls.append(url)
            content = content_map.get(url, "")
            return DownloadResult(status="downloaded", content=content, content_type="text/html", saved_path=storage.base_dir / "f")

    scraper = scraper_module.Scraper(config_model, cache, http_client=FakeClient())
    results = scraper.run()

    output_conf = {
        "format": "markdown",
        "file": tmp_path / "report.md",
        "split_per_source": True,
        "detail_dir": tmp_path / "sources",
        "language": "fr",
        "ai_report": {"enabled": True, "command": "echo ai", "output": tmp_path / "ai.md"},
    }
    # mock IA
    monkeypatch.setattr("tools.ai_report._run_llm", lambda cmd, prompt, timeout=120, **kwargs: "AI OK")
    report_path = report_module.write_report(results, output_conf)
    ai_path = runner_module.generate_ai_report(results, output_conf.get("ai_report", {}))

    assert report_path.exists()
    assert (tmp_path / "sources" / "a.md").exists()
    assert (tmp_path / "sources" / "b.md").exists()
    assert (tmp_path / "sources" / "a-d1.md").exists()
    assert ai_path == output_conf["ai_report"]["output"]
    assert ai_path.exists()
