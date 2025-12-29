"""
Génération de rapport CTI via un LLM local en CLI.
L'outil se contente de construire un prompt et d'appeler une commande locale (pas d'accès réseau).
"""
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
from tools.ai_pipeline import LangGraphRunner
from tools.ai_runner import run_cli_llm
from tools.ai import PromptConfig, AiCommandPlan, build_command_plan
from tools.scorer import score_results
import re
from typing import Dict, Any, List


def _run_llm(command: str, prompt: str, timeout: int = 120, pass_prompt_as_arg: bool = False, prompt_via_file: bool = False) -> str:
    return run_cli_llm(
        command=command,
        prompt=prompt,
        timeout=timeout,
        pass_prompt_as_arg=pass_prompt_as_arg,
        prompt_via_file=prompt_via_file,
    )


def _make_prompt_conf(conf: dict, default_template_key: str) -> PromptConfig:
    return PromptConfig(
        prompt_template=conf.get("prompt_template"),
        prompt_path=conf.get("prompt_path"),
        template_key=conf.get("template_key", default_template_key),
    )


def _write_text(path: Path, text: str, logger, label: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    if logger:
        logger.info("%s écrit : %s", label, path)


def _log_warn(logger, prefix: str, exc: Exception):
    if not logger:
        return
    err_msg = str(exc)
    if len(err_msg) > 500:
        err_msg = err_msg[:500] + "...[truncated]"
    logger.warning("%s : %s", prefix, err_msg)


def _run_cli_task(
    command: str,
    prompt: str,
    timeout: int,
    pass_prompt_as_arg: bool,
    prompt_via_file: bool,
    output_path: Optional[Path],
    logger,
    label: str,
) -> str:
    text = _run_llm(
        command,
        prompt,
        timeout=timeout,
        pass_prompt_as_arg=pass_prompt_as_arg,
        prompt_via_file=prompt_via_file,
    )
    if output_path:
        _write_text(output_path, text, logger, label)
    return text


def _run_with_retries(
    plan: AiCommandPlan,
    prompt: str,
    output_path: Path,
    retries: int,
    retry_delay: float,
    logger,
) -> Optional[str]:
    last_exc: Optional[Exception] = None
    text: Optional[str] = None
    for attempt in range(1, retries + 1):
        try:
            text = _run_cli_task(
                plan.command,
                prompt,
                timeout=plan.timeout,
                pass_prompt_as_arg=plan.pass_prompt_as_arg,
                prompt_via_file=plan.prompt_via_file,
                output_path=output_path,
                logger=logger,
                label="Rapport IA",
            )
            break
        except Exception as exc:
            last_exc = exc
            _log_warn(logger, f"Echec génération IA tentative {attempt}/{retries}", exc)
            if retry_delay > 0 and attempt < retries:
                time.sleep(retry_delay)
    if text is None and logger and last_exc:
        logger.error("Echec génération IA après %s tentatives : %s", retries, last_exc)
    return text


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
    # Filtre optionnel sur vulnérabilités seulement
    filt_conf = ai_conf.get("filter") or {}
    if filt_conf.get("vulnerability_only"):
        results = _filter_vuln_only(results)
    scoring_conf = ai_conf.get("scoring") or {}
    scored_results = score_results(
        results,
        weights=scoring_conf.get("weights"),
        per_type_weights=scoring_conf.get("per_type"),
        cvss_conf=scoring_conf.get("cvss"),
    )
    prompt_conf = _make_prompt_conf(ai_conf, "ai_report_template")
    prompt = prompt_conf.build_prompt(scored_results, logger=logger)
    plan = build_command_plan(ai_conf, logger=logger)
    output_path = Path(ai_conf.get("output", "reports/ai_report.md"))

    # Étape 1 (optionnelle) : agent d'analyse préliminaire
    analysis_text: Optional[str] = None
    analysis_conf = ai_conf.get("analysis")
    if analysis_conf and analysis_conf.get("enabled"):
        analysis_prompt_conf = _make_prompt_conf(analysis_conf, analysis_conf.get("template_key", "ai_analysis_template"))
        analysis_prompt = analysis_prompt_conf.build_prompt(scored_results, logger=logger)
        analysis_command = analysis_conf.get("command") or plan.command
        analysis_timeout = int(analysis_conf.get("timeout", plan.timeout))
        analysis_output_path = Path(analysis_conf.get("output", "reports/ai_analysis.md"))
        try:
            analysis_text = _run_cli_task(
                analysis_command,
                analysis_prompt,
                timeout=analysis_timeout,
                pass_prompt_as_arg=bool(analysis_conf.get("pass_prompt_as_arg", False)),
                prompt_via_file=bool(analysis_conf.get("prompt_via_file", ai_conf.get("prompt_via_file", False))),
                output_path=analysis_output_path,
                logger=logger,
                label="Analyse IA intermédiaire",
            )
        except Exception as exc:
            _log_warn(logger, "Echec agent d'analyse, on continue sans", exc)
            analysis_text = None

    # Reconstruit le prompt final en injectant l'analyse si disponible
    prompt = prompt_conf.build_prompt(results, logger=logger, extra={"analysis_text": analysis_text or ""})

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
                _write_text(output_path, text, logger, "Rapport IA (langgraph)")
                return output_path
        if logger:
            logger.warning("Mode langgraph indisponible ou en échec, fallback CLI.")

    # Fallback CLI avec retries optionnels
    if not plan.command:
        return None

    retries = max(1, int(ai_conf.get("retries", 1)))
    retry_delay = float(ai_conf.get("retry_delay", 0))
    text = _run_with_retries(plan, prompt, output_path, retries, retry_delay, logger)
    return output_path if text else None
def _is_vuln_entry(res: Dict[str, Any]) -> bool:
    keywords = res.get("keywords") or {}
    if keywords.get("vulnerability"):
        return True
    extracted = res.get("extracted") or []
    for item in extracted:
        if isinstance(item, str) and re.search(r"\bCVE-\d{4}-\d{4,7}\b", item, flags=re.IGNORECASE):
            return True
    return False


def _filter_vuln_only(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [r for r in results if _is_vuln_entry(r)]
