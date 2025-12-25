# Gestion intelligente et structurée de la configuration
from pathlib import Path
from typing import Any, List
from tools.load_config import (
    load_yaml_config,
    load_keywords_from_config,
    get_config_as_json_string,
)
from tools.config_builders import build_network_policy, build_crawler_settings, build_http_client_settings
from .Source import Source
from tools.download_types import StorageTarget
from tools.auth import load_auth
from tools.validators import validate_auth, validate_crawler, validate_output


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

    def build_storage_target(self, source: Source) -> StorageTarget:
        base_dir = Path(self.network_settings.get("save", {}).get("base_dir", "docs"))
        theme = source.type or "misc"
        name = source.name or "source"
        return StorageTarget(base_dir=base_dir, theme=theme, name=name)

    def _validate_configs(self) -> None:
        self.errors.extend(validate_auth(self.auth_settings))
        self.errors.extend(validate_crawler(self.crawler_settings))
        self.errors.extend(validate_output(self.yaml_config.get("output", {})))

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
                normalized["overrides"] = overrides
            built_sources.append(Source(normalized))
        return built_sources

    def has_errors(self) -> bool:
        return bool(self.errors)

    def has_warnings(self) -> bool:
        return bool(self.warnings)
