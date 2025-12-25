from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
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
