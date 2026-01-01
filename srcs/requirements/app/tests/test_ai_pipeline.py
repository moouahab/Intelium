from tools.providers.ai.ai_pipeline import LangGraphRunner, _validate_report_text, build_cli_llm


def test_langgraph_runner_builds_prompt_and_uses_llm():
    outputs = {}

    def fake_llm(prompt: str) -> str:
        outputs["prompt"] = prompt
        return "RESULT"

    runner = LangGraphRunner(prompt_template="PROMPT {results_json}", llm=fake_llm)
    text = runner.generate([{"url": "http://x"}])

    assert "http://x" in outputs["prompt"]
    assert text == "RESULT"


def test_validate_report_text_raises_on_empty():
    try:
        _validate_report_text("   ")
    except ValueError:
        assert True
    else:  # pragma: no cover
        assert False


def test_build_cli_llm_runs_command(monkeypatch):
    def fake_run(cmd, **kwargs):
        class P:
            returncode = 0
            stdout = "OK"
            stderr = ""

        return P()

    monkeypatch.setattr("subprocess.run", fake_run)
    llm = build_cli_llm("codex chat", pass_prompt_as_arg=True, timeout=5)
    out = llm("prompt")
    assert out == "OK"
