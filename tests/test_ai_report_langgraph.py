from pathlib import Path
from tools import ai_report
from tools import ai_pipeline


def test_generate_ai_report_langgraph_mode(monkeypatch, tmp_path):
    monkeypatch.setattr(ai_pipeline.LangGraphRunner, "available", classmethod(lambda cls: True))

    def fake_generate(self, results):
        return "LANGGRAPH REPORT"

    monkeypatch.setattr(ai_pipeline.LangGraphRunner, "generate", fake_generate)
    out = tmp_path / "ai.md"
    res = ai_report.generate_ai_report(
        [{"url": "http://x"}],
        {"enabled": True, "mode": "langgraph", "output": out, "prompt_template": "PROMPT"},
        logger=None,
    )
    assert res == out
    assert out.read_text() == "LANGGRAPH REPORT"


def test_generate_ai_report_langgraph_with_cli_llm(monkeypatch, tmp_path):
    monkeypatch.setattr(ai_pipeline.LangGraphRunner, "available", classmethod(lambda cls: False))

    def fake_run(cmd, **kwargs):
        class P:
            returncode = 0
            stdout = "CLI REPORT"
            stderr = ""
        return P()

    monkeypatch.setattr("subprocess.run", fake_run)
    out = tmp_path / "ai.md"
    res = ai_report.generate_ai_report(
        [{"url": "http://x"}],
        {
            "enabled": True,
            "mode": "langgraph",
            "output": out,
            "prompt_template": "PROMPT",
            "langgraph_llm_command": "codex chat",
            "pass_prompt_as_arg": True,
        },
        logger=None,
    )
    assert res == out
    assert out.read_text() == "CLI REPORT"
