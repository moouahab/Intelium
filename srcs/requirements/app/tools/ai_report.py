"""
Génération de rapport CTI via un LLM local en CLI.
L'outil se contente de construire un prompt et d'appeler une commande locale (pas d'accès réseau).
"""
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.ai_runner import run_cli_llm
from tools.ai import PromptConfig
from tools.interfaces import AIProvider
from tools.ai.providers import DefaultAIProvider, is_complete as _is_complete
from tools.result_entry import normalize_results


def _run_llm(
    command: str,
    prompt: str,
    timeout: int = 120,
    pass_prompt_as_arg: bool = False,
    prompt_via_file: bool = False,
) -> str:
    return run_cli_llm(
        command=command,
        prompt=prompt,
        timeout=timeout,
        pass_prompt_as_arg=pass_prompt_as_arg,
        prompt_via_file=prompt_via_file,
    )


def generate_ai_report(
    results: List[Dict[str, Any]],
    ai_conf: dict,
    logger=None,
    provider: AIProvider | None = None,
) -> Optional[Path]:
    """
    ai_conf attend :
      - enabled: bool
      - command: str (ex: "ollama run llama3" ou "llama.cpp -m model.gguf")
      - output: chemin du fichier rapport (par défaut reports/ai_report.md)
      - timeout: optionnel (sec)
      - prompt_template: optionnel, chaîne utilisable avec `{results_json}`
      - prompt_path: optionnel, chemin vers un fichier template
      - pass_prompt_as_arg: bool, si True passe le prompt en argument (utile pour certaines CLI qui ne lisent pas stdin)
      - prompt_via_file: bool, écrit le prompt dans un fichier temporaire (évite les prompts trop longs et limite l’exposition en logs)
    """
    if not ai_conf or not ai_conf.get("enabled"):
        return None
    results = normalize_results(results)
    if provider:
        try:
            return provider.generate(results, ai_conf, logger=logger)
        except Exception as exc:
            if logger:
                logger.warning("AI provider custom en échec, fallback plan par défaut : %s", exc)
    default_provider = DefaultAIProvider(run_llm=_run_llm)
    return default_provider.generate(results, ai_conf, logger=logger)
