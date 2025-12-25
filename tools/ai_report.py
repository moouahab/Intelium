"""
Génération de rapport CTI via un LLM local en CLI.
L'outil se contente de construire un prompt et d'appeler une commande locale (pas d'accès réseau).
"""
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.ai_pipeline import LangGraphRunner
from tools.ai_runner import run_cli_llm
from tools.ai import PromptConfig, AiCommandPlan, build_command_plan


def _run_llm(command: str, prompt: str, timeout: int = 120, pass_prompt_as_arg: bool = False, prompt_via_file: bool = False) -> str:
    return run_cli_llm(
        command=command,
        prompt=prompt,
        timeout=timeout,
        pass_prompt_as_arg=pass_prompt_as_arg,
        prompt_via_file=prompt_via_file,
    )


def generate_ai_report(results: List[Dict[str, Any]], ai_conf: dict, logger=None) -> Optional[Path]:
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
    prompt_conf = PromptConfig(
        prompt_template=ai_conf.get("prompt_template"),
        prompt_path=ai_conf.get("prompt_path"),
    )
    prompt = prompt_conf.build_prompt(results, logger=logger)
    plan = build_command_plan(ai_conf, logger=logger)
    output_path = Path(ai_conf.get("output", "reports/ai_report.md"))

    # Mode LangGraph
    if plan.mode == "langgraph":
        template = prompt_conf.load_template(logger=logger) or prompt_conf.prompt_template or ""
        llm_fn = ai_conf.get("langgraph_llm")
        if not llm_fn and plan.langgraph_command:
            llm_fn = lambda text: run_cli_llm(
                plan.langgraph_command,
                text,
                timeout=plan.timeout,
                pass_prompt_as_arg=plan.pass_prompt_as_arg,
                prompt_via_file=plan.prompt_via_file,
            )
        runner = LangGraphRunner(prompt_template=template, llm=llm_fn)
        if LangGraphRunner.available() or runner.llm:
            try:
                text = runner.generate(results)
            except Exception as exc:
                if logger:
                    logger.error("LangGraph generation failed: %s", exc)
                text = None
            if text:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(text)
                if logger:
                    logger.info("Rapport IA (langgraph) écrit : %s", output_path)
                return output_path
        if logger:
            logger.warning("Mode langgraph indisponible ou en échec, fallback CLI.")

    # Fallback CLI
    if not plan.command:
        return None
    try:
        text = _run_llm(
            plan.command,
            prompt,
            timeout=plan.timeout,
            pass_prompt_as_arg=plan.pass_prompt_as_arg,
            prompt_via_file=plan.prompt_via_file,
        )
    except Exception as exc:
        if logger:
            err_msg = str(exc)
            if len(err_msg) > 500:
                err_msg = err_msg[:500] + "...[truncated]"
            logger.error("Echec génération IA : %s", err_msg)
        return None

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text)
    if logger:
        logger.info("Rapport IA écrit : %s", output_path)
    return output_path
