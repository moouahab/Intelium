from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
import time
import unicodedata
from typing import Any, Dict, List, Optional, Callable

from tools.providers.ai.prompt_config import PromptConfig
from tools.providers.ai.command_plan import AiCommandPlan, build_command_plan, detect_local_llm
from tools.providers.ai.ai_pipeline import LangGraphRunner
from tools.providers.ai.ai_runner import run_cli_llm
from tools.interfaces import AIProvider
from tools.scorer import score_results


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
    run_llm: Callable[..., str],
    command: str,
    prompt: str,
    timeout: int,
    pass_prompt_as_arg: bool,
    prompt_via_file: bool,
    output_path: Optional[Path],
    logger,
    label: str,
) -> str:
    text = run_llm(
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
    run_llm: Callable[..., str],
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
                run_llm,
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


def _run_fallback(
    run_llm: Callable[..., str],
    ai_conf: dict,
    prompt: str,
    output_path: Path,
    logger,
) -> Optional[str]:
    fallback = ai_conf.get("fallback") or {}
    fb_command = fallback.get("command")
    if not fb_command:
        return None
    fb_timeout = int(fallback.get("timeout", ai_conf.get("timeout", 120)))
    fb_pass_arg = bool(fallback.get("pass_prompt_as_arg", False))
    fb_prompt_via_file = bool(fallback.get("prompt_via_file", ai_conf.get("prompt_via_file", False)))
    try:
        return _run_cli_task(
            run_llm,
            fb_command,
            prompt,
            timeout=fb_timeout,
            pass_prompt_as_arg=fb_pass_arg,
            prompt_via_file=fb_prompt_via_file,
            output_path=output_path,
            logger=logger,
            label="Rapport IA (fallback)",
        )
    except Exception as exc:
        _log_warn(logger, "Echec fallback IA", exc)
        return None


def _run_local_autodetect(
    run_llm: Callable[..., str],
    prompt: str,
    output_path: Path,
    logger,
    timeout: int = 120,
    pass_prompt_as_arg: bool = False,
    prompt_via_file: bool = False,
) -> Optional[str]:
    cmd = detect_local_llm()
    if not cmd:
        return None
    try:
        return _run_cli_task(
            run_llm,
            cmd,
            prompt,
            timeout=timeout,
            pass_prompt_as_arg=pass_prompt_as_arg,
            prompt_via_file=prompt_via_file,
            output_path=output_path,
            logger=logger,
            label="Rapport IA (local autodetect)",
        )
    except Exception as exc:
        _log_warn(logger, "Echec fallback LLM local", exc)
        return None


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    stripped = normalized.encode("ascii", "ignore").decode("ascii")
    return stripped.lower()


def is_complete(
    text: Optional[str],
    required_markers: Optional[list[str]] = None,
    required_sections: Optional[list[str]] = None,
) -> bool:
    if not text:
        return False
    markers = required_markers or ["FIN DU RAPPORT"]
    lowered = _normalize_text(text)
    for m in markers:
        if _normalize_text(m) not in lowered:
            return False
    for sec in required_sections or []:
        if _normalize_text(sec) not in lowered:
            return False
    return True


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


def _to_int(val: Any, default: int) -> int:
    try:
        return int(val)
    except Exception:
        return default


def _truncate_text(text: Any, max_len: int) -> Any:
    if not isinstance(text, str):
        return text
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _fill_missing_sections(
    text: str,
    required_sections: list[str],
    required_markers: list[str],
) -> str:
    if not text:
        text = ""
    normalized = _normalize_text(text)
    lines: list[str] = []
    for sec in required_sections:
        if _normalize_text(sec) in normalized:
            continue
        lines.append(f"## {sec}")
        lines.append("- Donnees absentes dans les extraits fournis.")
        lines.append("")
    if required_markers:
        marker_norm = [_normalize_text(m) for m in required_markers]
        combined = _normalize_text(text + "\n" + "\n".join(lines))
        for marker, marker_n in zip(required_markers, marker_norm):
            if marker_n not in combined:
                lines.append(marker)
    if lines:
        prefix = "" if text.endswith("\n") or not text else "\n"
        return text + prefix + "\n".join(lines).rstrip() + "\n"
    return text


def _compact_results(
    results: List[Dict[str, Any]],
    max_results: int,
    max_extracted: int,
    max_extracted_chars: int,
) -> List[Dict[str, Any]]:
    """
    Réduit la taille du payload envoyé au LLM (limite le nombre de sources et la longueur des extraits).
    """
    trimmed = []
    for res in results[:max_results]:
        clone = deepcopy(res)
        extracted = clone.get("extracted")
        if isinstance(extracted, list):
            compacted = []
            for item in extracted[:max_extracted]:
                compacted.append(_truncate_text(item, max_extracted_chars))
            clone["extracted"] = compacted
        else:
            clone["extracted"] = []
        # Nettoie d'éventuels champs volumineux accidentels
        for heavy_key in ("content", "raw", "body"):
            if heavy_key in clone:
                clone.pop(heavy_key, None)
        trimmed.append(clone)
    return trimmed


class DefaultAIProvider(AIProvider):
    """
    Provider IA par défaut (CLI / LangGraph / fallback) avec scoring et compaction.
    """

    def __init__(self, run_llm: Callable[..., str] = run_cli_llm):
        self.run_llm = run_llm

    def generate(self, results: List[Dict[str, Any]], ai_conf: dict, logger=None) -> Optional[Path]:
        if not ai_conf or not ai_conf.get("enabled"):
            return None

        # Réduction du payload pour éviter les prompts trop gros (413, etc.)
        max_results = _to_int(ai_conf.get("max_results", len(results) or 0), default=len(results) or 0) or len(results)
        max_extracted = _to_int(ai_conf.get("max_extracted_per_source", 30), default=30)
        max_extracted_chars = _to_int(ai_conf.get("max_extracted_chars", 500), default=500)

        # Filtre optionnel sur vulnérabilités seulement
        filt_conf = ai_conf.get("filter") or {}
        if filt_conf.get("vulnerability_only"):
            results = _filter_vuln_only(results)

        compacted = _compact_results(
            results,
            max_results=max_results,
            max_extracted=max_extracted,
            max_extracted_chars=max_extracted_chars,
        )
        scoring_conf = ai_conf.get("scoring") or {}
        try:
            scored_results = score_results(
                compacted,
                weights=scoring_conf.get("weights"),
                per_type_weights=scoring_conf.get("per_type"),
                cvss_conf=scoring_conf.get("cvss"),
            )
        except Exception:
            scored_results = compacted

        prompt_conf = _make_prompt_conf(ai_conf, "ai_report_template")
        prompt = prompt_conf.build_prompt(scored_results, logger=logger)
        plan = build_command_plan(ai_conf, logger=logger)
        output_path = Path(ai_conf.get("output", "reports/ai_report.md"))

        # Étape 1 (optionnelle) : agent d'analyse préliminaire
        analysis_text: Optional[str] = None
        analysis_conf = ai_conf.get("analysis")
        if analysis_conf and analysis_conf.get("enabled"):
            analysis_prompt_conf = _make_prompt_conf(
                analysis_conf, analysis_conf.get("template_key", "ai_analysis_template")
            )
            analysis_prompt = analysis_prompt_conf.build_prompt(scored_results, logger=logger)
            analysis_command = analysis_conf.get("command") or plan.command
            analysis_timeout = int(analysis_conf.get("timeout", plan.timeout))
            analysis_output_path = Path(analysis_conf.get("output", "reports/ai_analysis.md"))
            try:
                analysis_text = _run_cli_task(
                    self.run_llm,
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
        prompt = prompt_conf.build_prompt(compacted, logger=logger, extra={"analysis_text": analysis_text or ""})

        # Mode LangGraph
        if plan.mode == "langgraph":
            template = prompt_conf.load_template(logger=logger) or prompt_conf.prompt_template or ""
            llm_fn = ai_conf.get("langgraph_llm")
            if not llm_fn and plan.langgraph_command:
                llm_fn = lambda text: self.run_llm(
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
        required_markers = ["FIN DU RAPPORT"]
        required_sections = ai_conf.get("required_sections") or []
        accept_incomplete = bool(ai_conf.get("accept_incomplete", False))
        fill_missing = bool(ai_conf.get("fill_missing_sections", True))
        last_text: Optional[str] = None
        text = _run_with_retries(self.run_llm, plan, prompt, output_path, retries, retry_delay, logger)
        if text:
            last_text = text
        if not is_complete(text, required_markers, required_sections):
            _log_warn(logger, "Rapport IA incomplet, tentative fallback", Exception("rapport incomplet"))
            text = _run_fallback(self.run_llm, ai_conf, prompt, output_path, logger)
            if text:
                last_text = text
        if not is_complete(text, required_markers, required_sections):
            text = _run_local_autodetect(
                self.run_llm,
                prompt,
                output_path,
                logger,
                timeout=plan.timeout,
                pass_prompt_as_arg=plan.pass_prompt_as_arg,
                prompt_via_file=plan.prompt_via_file,
            )
            if text:
                last_text = text
        if not is_complete(text, required_markers, required_sections):
            if accept_incomplete and last_text:
                if fill_missing:
                    last_text = _fill_missing_sections(last_text, required_sections, required_markers)
                _write_text(output_path, last_text, logger, "Rapport IA (incomplet)")
                return output_path
            if logger:
                logger.warning("Rapport IA final incomplet : un résumé minimal sera écrit.")
            try:
                fallback_text = "Rapport IA non disponible. Synthèse minimale:\nFIN DU RAPPORT"
                _write_text(output_path, fallback_text, logger, "Rapport IA (minimal)")
                return output_path
            except Exception:
                return None
        return output_path
