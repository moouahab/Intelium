from pathlib import Path

from tools.providers.ai import ai_report


def test_load_template_from_yaml_prompt_key(tmp_path):
    tmpl_path = tmp_path / "prompt.yaml"
    tmpl_path.write_text("prompt:\n  ai_report_template: TEMPLATE {results_json}\n")

    prompt_conf = ai_report.PromptConfig(prompt_path=str(tmpl_path))
    tmpl = prompt_conf.load_template()

    assert "TEMPLATE" in tmpl
    assert "{results_json}" in tmpl


def test_generate_ai_report_sets_pass_prompt_as_arg_for_codex(monkeypatch, tmp_path):
    captured = {}

    def fake_run(cmd, prompt, timeout=120, pass_prompt_as_arg=False, prompt_via_file=False, **kwargs):
        captured["cmd"] = cmd
        captured["pass_prompt_as_arg"] = pass_prompt_as_arg
        captured["prompt_via_file"] = prompt_via_file
        return "OK FIN DU RAPPORT"

    monkeypatch.setattr(ai_report, "_run_llm", fake_run)
    out = tmp_path / "ai.md"
    res = ai_report.generate_ai_report(
        [{"url": "http://x"}],
        {"enabled": True, "command": "codex exec --skip-git-repo-check -", "output": out, "prompt_via_file": True, "pass_prompt_as_arg": False},
        logger=None,
    )

    assert res == out
    assert out.read_text() == "OK FIN DU RAPPORT"
    assert captured["pass_prompt_as_arg"] is False
    assert captured["prompt_via_file"] is True
