# Gestion intelligente et structurée de la configuration
from pathlib import Path
import re
from typing import Any, List
from tools.config.load_config import (
    load_yaml_config,
    load_keywords_from_config,
    get_config_as_json_string,
)
from tools.config.config_builders import build_network_policy, build_crawler_settings, build_http_client_settings
from .Source import Source
from tools.download_types import StorageTarget
from tools.auth import load_auth
from tools.config.validators import validate_auth, validate_crawler, validate_output
from tools.config.config_validator import validate_config
from tools.config.overrides import normalize_overrides


SUPPORTED_SOURCE_TYPES = {"html", "api", "xml", "pdf", "csv", "txt", "image", "ignore"}


class ConfigModel:
    def __init__(self, yaml_config: str | Path, strict: bool = True):
        self.config_path = Path(yaml_config)
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.yaml_config = load_yaml_config(self.config_path)
        self.keywords = load_keywords_from_config(self.yaml_config)
        self.json_config_str = get_config_as_json_string(self.yaml_config)
        self.network_settings = self.yaml_config.get("network", {})
        self.network_policy = build_network_policy(self.network_settings)
        self.crawler_settings = build_crawler_settings(
            self.yaml_config.get("crawler", {}),
            fallback_allow_domains=self.network_policy.allow_domains,
        )
        self.http_settings = build_http_client_settings(self.yaml_config.get("crawler", {}))
        self.url_normalizer_name = self.crawler_settings.get("url_normalizer", "strip")
        self.scraping_settings = self.yaml_config.get("data_scraper", {})
        self.auth_settings = load_auth(self.config_path.parent / "auth.yaml")
        self.user_agents = self.network_settings.get("user_agents", [])
        self.proxies = self.network_settings.get("proxies", [])
        self.sources: List[dict[str, Any]] = self.yaml_config.get("sources", [])
        self.source_objects: List[Source] = self._build_sources(self.sources, strict=strict)
        self._validate_configs()

    def _sanitize_segment(self, value: str | None, default: str) -> str:
        """
        Nettoie un segment de chemin (nom/type) pour éviter les traversals et les séparateurs.
        Conserve uniquement les caractères autorisés, remplace le reste par underscore.
        """
        text = (value or "").strip()
        text = text.replace("/", "_").replace("\\", "_")
        text = re.sub(r"[^A-Za-z0-9._-]", "_", text)
        text = text.lstrip(".")
        if not text or text in {".", ".."}:
            return default
        return text

    def _resolve_base_dir(self) -> Path:
        """
        Détermine le dossier de stockage effectif en respectant un éventuel sandbox_dir.
        Si sandbox_dir est défini et que base_dir n'est pas déjà dedans, on le reloge sous le sandbox.
        """
        base_dir = Path(self.network_settings.get("save", {}).get("base_dir", "docs"))
        sandbox_dir = self.network_settings.get("sandbox_dir")
        if not sandbox_dir:
            return base_dir

        sandbox_path = Path(sandbox_dir)
        try:
            sandbox_resolved = sandbox_path.resolve()
        except Exception:
            sandbox_resolved = sandbox_path

        try:
            base_resolved = base_dir.resolve()
        except Exception:
            base_resolved = base_dir

        if sandbox_resolved in base_resolved.parents or base_resolved == sandbox_resolved:
            return base_dir
        return sandbox_resolved / base_dir

    def build_storage_target(self, source: Source) -> StorageTarget:
        base_dir = self._resolve_base_dir()
        theme = self._sanitize_segment(source.type, "misc")
        name = self._sanitize_segment(source.name, "source")
        return StorageTarget(base_dir=base_dir, theme=theme, name=name)

    def _validate_configs(self) -> None:
        errs, warns = validate_config(self.yaml_config)
        self.errors.extend(errs)
        self.warnings.extend(warns)

    def _build_sources(self, raw_sources: Any, strict: bool) -> List[Source]:
        if not raw_sources:
            self.warnings.append("Aucune source définie dans la configuration.")
            return []
        if not isinstance(raw_sources, list):
            self.errors.append("La clé 'sources' doit être une liste.")
            return []
        built_sources: List[Source] = []
        seen_names: set[str] = set()
        for idx, entry in enumerate(raw_sources):
            if not isinstance(entry, dict):
                self.errors.append(f"Source #{idx} invalide (doit être un dictionnaire).")
                if strict:
                    continue
                entry = {}
            name = entry.get("name") or f"source_{idx}"
            url = entry.get("url")
            stype = (entry.get("type") or "html").lower()
            if not url:
                self.errors.append(f"Source '{name}' sans URL.")
                if strict:
                    continue
            if stype not in SUPPORTED_SOURCE_TYPES:
                self.warnings.append(
                    f"Type '{stype}' non supporté pour la source '{name}', fallback sur 'html'."
                )
                stype = "html"
            if name in seen_names:
                self.warnings.append(f"Nom de source dupliqué: '{name}'.")
            seen_names.add(name)
            normalized = dict(entry)
            normalized["name"] = name
            normalized["url"] = url
            normalized["type"] = stype
            overrides = normalized.get("overrides", {})
            if overrides and isinstance(overrides, dict):
                clean_overrides = normalize_overrides(overrides)
                if clean_overrides:
                    normalized["overrides"] = clean_overrides
            built_sources.append(Source(normalized))
        return built_sources

    def has_errors(self) -> bool:
        return bool(self.errors)

    def has_warnings(self) -> bool:
        return bool(self.warnings)
