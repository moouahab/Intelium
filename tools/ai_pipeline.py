"""
Intégration optionnelle LangGraph/LLM.
Par défaut, ne dépend pas de langgraph ; injectez ou monkeypatchez LangGraphRunner.generate
dans les tests ou fournissez un callback pour générer le texte.
"""
from __future__ import annotations

import json
import shlex
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable


def _validate_report_text(text: str) -> str:
    if not text or not text.strip():
        raise ValueError("Rapport IA vide")
    return text.strip()


@dataclass
class LangGraphRunner:
    prompt_template: str
    llm: Optional[Callable[[str], str]] = None

    @classmethod
    def available(cls) -> bool:
        # Autorise l'utilisation même si langgraph n'est pas installé en mode injecté/test.
        try:
            import langgraph  # type: ignore  # noqa: F401
            return True
        except Exception:
            return False

    def build_prompt(self, results: List[Dict[str, Any]]) -> str:
        results_json = json.dumps(results, ensure_ascii=False, indent=2)
        try:
            return self.prompt_template.format(results_json=results_json)
        except Exception:
            return f"{self.prompt_template}\n\n{results_json}"

    def generate(self, results: List[Dict[str, Any]]) -> str:
        prompt = self.build_prompt(results)
        if self.llm:
            text = self.llm(prompt)
            return _validate_report_text(text)
        if not self.available():
            raise RuntimeError("LangGraph non disponible et aucun LLM fourni.")
        # Si LangGraph est dispo mais aucun LLM n'est injecté, on échoue explicitement
        raise RuntimeError("Aucun LLM fourni pour LangGraph.")


def build_cli_llm(command: str, pass_prompt_as_arg: bool = False, timeout: int = 120) -> Callable[[str], str]:
    """
    Construit une fonction LLM qui appelle un binaire local (codex, ollama...).
    """
    def llm(prompt: str) -> str:
        cmd_list = shlex.split(command)
        run_kwargs = {"text": True, "capture_output": True, "timeout": timeout}
        if pass_prompt_as_arg:
            cmd_list = cmd_list + [prompt]
            run_kwargs["input"] = None
        else:
            run_kwargs["input"] = prompt
        proc = subprocess.run(cmd_list, **run_kwargs)
        if proc.returncode != 0:
            raise RuntimeError(f"LLM CLI échec ({proc.returncode}): {proc.stderr.strip()}")
        return proc.stdout.strip()

    return llm
