"""
Génération de rapport CTI via un LLM local en CLI.
L'outil se contente de construire un prompt et d'appeler une commande locale (pas d'accès réseau).
"""
from dataclasses import dataclass
from pathlib import Path
import json
import shlex
import subprocess
from typing import Any, Dict, List, Optional
import shutil
import yaml


@dataclass
class PromptConfig:
    prompt_template: Optional[str] = None
    prompt_path: Optional[str] = None

    def load_template(self, logger=None) -> Optional[str]:
        if not self.prompt_path:
            return self.prompt_template
        try:
            raw = Path(self.prompt_path).read_text()
        except OSError as exc:
            if logger:
                logger.warning("Impossible de lire prompt_path=%s: %s", self.prompt_path, exc)
            return self.prompt_template
        # Tente de parser YAML si possible
        try:
            data = yaml.safe_load(raw)
            if isinstance(data, dict):
                if "prompt" in data and isinstance(data["prompt"], dict):
                    tmpl = data["prompt"].get("ai_report_template")
                    if isinstance(tmpl, str):
                        return tmpl
                if "ai_report_template" in data and isinstance(data["ai_report_template"], str):
                    return data["ai_report_template"]
        except Exception:
            pass
        return raw or self.prompt_template

    def build_prompt(self, results: List[Dict[str, Any]], logger=None) -> str:
        results_json = json.dumps(results, ensure_ascii=False, indent=2)
        template = self.load_template(logger=logger) or self.prompt_template
        if template:
            try:
                return template.format(results_json=results_json)
            except Exception:
                if logger:
                    logger.warning("Echec formatage template IA, fallback sur défaut.")
        lines = [
            "Tu es un analyste CTI.",
            "Produis un rapport concis en français avec sections :",
            "- Résumé exécutif",
            "- Sources analysées (statut, type, erreurs éventuelles)",
            "- Indicateurs notables / tendances",
            "- Recommandations",
            "",
            "Données d'entrée (JSON) :",
            results_json,
        ]
        return "\n".join(lines)


def _run_llm(command: str, prompt: str, timeout: int = 120, pass_prompt_as_arg: bool = False) -> str:
    cmd_list = shlex.split(command)
    run_kwargs = {
        "text": True,
        "capture_output": True,
        "timeout": timeout,
    }
    if pass_prompt_as_arg:
        cmd_list = cmd_list + [prompt]
        run_kwargs["input"] = None
    else:
        run_kwargs["input"] = prompt

    proc = subprocess.run(cmd_list, **run_kwargs)
    if proc.returncode != 0:
        raise RuntimeError(f"Commande IA échouée ({proc.returncode}): {proc.stderr.strip()}")
    return proc.stdout.strip()


def _detect_local_llm() -> Optional[str]:
    """
    Essaie de détecter un binaire LLM local et retourne une commande prête à l'emploi.
    Priorité : ollama -> llama/llama.cpp -> codex -> copilot -> code (VS Code).
    """
    if shutil.which("ollama"):
        return "ollama run llama3"
    if shutil.which("llama"):
        return "llama -m model.gguf"
    if shutil.which("llama.cpp"):
        return "llama.cpp -m model.gguf"
    if shutil.which("codex"):
        return "codex chat"
    if shutil.which("copilot"):
        return "copilot chat"
    if shutil.which("code"):
        return "code"
    return None


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
    """
    if not ai_conf or not ai_conf.get("enabled"):
        return None
    command = ai_conf.get("command")
    if not command:
        command = _detect_local_llm()
        if not command:
            if logger:
                logger.warning("AI report demandé mais aucune commande fournie ou détectée.")
            return None
    output_path = Path(ai_conf.get("output", "reports/ai_report.md"))
    timeout = int(ai_conf.get("timeout", 120))

    prompt_conf = PromptConfig(
        prompt_template=ai_conf.get("prompt_template"),
        prompt_path=ai_conf.get("prompt_path"),
    )
    prompt = prompt_conf.build_prompt(results, logger=logger)
    pass_as_arg_opt = ai_conf.get("pass_prompt_as_arg")
    if pass_as_arg_opt is None:
        # heuristique : certaines CLI (codex, copilot, code) ne lisent pas stdin
        if command and any(token in command for token in ["codex", "copilot", "code"]):
            pass_as_arg = True
        else:
            pass_as_arg = False
    else:
        pass_as_arg = bool(pass_as_arg_opt)
    try:
        text = _run_llm(command, prompt, timeout=timeout, pass_prompt_as_arg=pass_as_arg)
    except Exception as exc:
        if logger:
            logger.error("Echec génération IA : %s", exc)
        return None

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text)
    if logger:
        logger.info("Rapport IA écrit : %s", output_path)
    return output_path
