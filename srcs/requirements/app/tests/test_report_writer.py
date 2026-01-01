from pathlib import Path

from tools.reporting.report_writer import ReportWriter
from tools.providers.ai.ai_report import generate_ai_report


def _sample_results():
    return [
        {"url": "http://example.com", "name": "root", "type": "html", "status": "downloaded", "saved_path": "docs/html/root.html"},
        {"url": "http://example.com/cache", "name": "cached", "type": "html", "status": "skipped-cache", "saved_path": "docs/html/cached.html"},
        {"url": "http://example.com/error", "name": "err", "type": "api", "status": "error", "error": "boom"},
    ]


def test_markdown_skipped_cache_keeps_existing(tmp_path):
    detail_dir = tmp_path / "sources"
    existing = detail_dir / "cached.md"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("ancien contenu")

    writer = ReportWriter({"file": tmp_path / "report.md", "detail_dir": detail_dir, "split_per_source": True})
    writer.write(_sample_results())

    assert existing.read_text() == "ancien contenu"


def test_json_report_creates_detail_and_main(tmp_path):
    writer = ReportWriter({"file": tmp_path / "report.json", "detail_dir": tmp_path / "sources", "format": "json", "split_per_source": True})
    path = writer.write(_sample_results())

    assert path.exists()
    detail = tmp_path / "sources" / "root.json"
    assert detail.exists()


def test_markdown_detail_includes_keywords(tmp_path):
    results = [
        {
            "url": "http://example.com",
            "name": "root",
            "type": "html",
            "status": "downloaded",
            "saved_path": "docs/html/root.html",
            "keywords": {"indicator": ["ioc1", "ioc2"]},
            "extracted": ["ioc1 present"],
        }
    ]
    detail_dir = tmp_path / "sources"
    writer = ReportWriter({"file": tmp_path / "report.md", "detail_dir": detail_dir, "split_per_source": True})

    writer.write(results)

    detail = detail_dir / "root.md"
    assert "Mots-clés" in detail.read_text()
    assert "indicator: ioc1, ioc2" in detail.read_text()


def test_markdown_main_includes_keywords_when_no_split(tmp_path):
    results = [
        {
            "url": "http://example.com",
            "name": "root",
            "type": "html",
            "status": "downloaded",
            "keywords": {"indicator": ["ioc1"]},
            "extracted": ["ioc1 present"],
        }
    ]
    writer = ReportWriter({"file": tmp_path / "report.md", "split_per_source": False})

    main = writer.write(results)

    content = main.read_text()
    assert "Mots-clés" in content
    assert "indicator: ioc1" in content


def test_ai_report_writes_file(tmp_path, monkeypatch):
    called = {}

    def fake_run(command, prompt, timeout=120, **kwargs):
        called["cmd"] = command
        called["prompt"] = prompt
        return "AI REPORT FIN DU RAPPORT"

    monkeypatch.setattr("tools.providers.ai.ai_report._run_llm", fake_run)
    out = tmp_path / "ai.md"
    tmpl = "PROMPT:\n{results_json}"
    res = generate_ai_report([{"url": "http://x"}], {"enabled": True, "command": "echo ai", "output": out, "prompt_template": tmpl})
    assert res == out
    assert out.read_text() == "AI REPORT FIN DU RAPPORT"
    assert "PROMPT:" in called["prompt"]


def test_ai_report_disabled_returns_none(tmp_path):
    res = generate_ai_report([{"url": "http://x"}], {"enabled": False, "command": "echo ai", "output": tmp_path / "ai.md"})
    assert res is None


def test_ai_report_autodetect_returns_none_if_not_found(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.providers.ai.command_plan.shutil.which", lambda cmd: None)
    res = generate_ai_report([{"url": "http://x"}], {"enabled": True, "command": ""}, logger=None)
    assert res is None


def test_ai_report_prompt_path(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.providers.ai.ai_report._run_llm", lambda command, prompt, timeout=120, **kwargs: "OK FIN DU RAPPORT")
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("PROMPT FILE {results_json}")
    out = tmp_path / "ai.md"
    res = generate_ai_report(
        [{"url": "http://x"}],
        {"enabled": True, "command": "echo ai", "output": out, "prompt_path": prompt_file},
    )
    assert res == out


def test_ai_report_autodetect_codex(tmp_path, monkeypatch):
    # Simule la détection de "codex"
    def fake_which(cmd):
        return "/usr/bin/codex" if cmd == "codex" else None
    monkeypatch.setattr("tools.providers.ai.command_plan.shutil.which", fake_which)
    monkeypatch.setattr("tools.providers.ai.ai_report._run_llm", lambda command, prompt, timeout=120, **kwargs: "OK FIN DU RAPPORT")
    out = tmp_path / "ai.md"
    res = generate_ai_report([{"url": "http://x"}], {"enabled": True, "command": "", "output": out})
    assert res == out


def test_report_writer_additional_formats(tmp_path):
    writer = ReportWriter(
        {
            "file": tmp_path / "report.md",
            "detail_dir": tmp_path / "sources",
            "format": "markdown",
            "additional_formats": ["json"],
            "split_per_source": True,
        }
    )
    results = _sample_results()
    writer.write(results)

    assert (tmp_path / "report.md").exists()
    assert (tmp_path / "report.json").exists()
    # detail JSON should be under sources/json
    assert (tmp_path / "sources" / "json" / "root.json").exists()
