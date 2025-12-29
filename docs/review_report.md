# Revue de code (rapport généré)

- Extraits disponibles : 25
- Fonctions détectées  : 44
- Signalements pratiques : 5

## Fonctions indexées
| Fichier | Fonctions |
|---|---|
| `requirements/app/main.py` | main |
| `requirements/app/cti_core/orchestrator.py` | __init__, stop |
| `requirements/app/cti_core/Source.py` | __init__ |
| `requirements/app/cti_core/sources_factory.py` | enqueue_links |
| `requirements/app/cti_core/config_model.py` | __init__ |
| `requirements/app/cti_core/runner.py` | build_cache_manager, run |
| `requirements/app/cti_core/crawler_state.py` | __init__, _guard, add, has_next |
| `requirements/app/cti_core/scraper.py` | __init__ |
| `requirements/app/cti_core/result_recorder.py` | __init__, record_cache_hit |
| `requirements/app/cti_core/cli.py` | render_progress, print_summary |
| `requirements/app/tools/html_links.py` | extract_links |
| `requirements/app/tools/keywords.py` | find_keyword_hits |
| `requirements/app/tools/config_utils.py` | to_int, to_bool |
| `requirements/app/tools/cache_mongo.py` | __init__, _connect, _collection |
| `requirements/app/tools/load_config.py` | load_yaml_config, _deep_merge, get_config_as_json_string, load_keywords_from_confi |
| `requirements/app/tools/report_sections.py` | _truncate, build_markdown_section |
| `requirements/app/tools/scheduling.py` | parse_interval_seconds |
| `requirements/app/tools/ai_runner.py` | run_cli_llm |
| `requirements/app/tools/cache.py` | from_dict, to_dict, __init__, _load |
| `requirements/app/tools/parser.py` | __init__, get |
| `requirements/app/tools/content_sanitizer.py` | sanitize_html, sanitize_xml |
| `requirements/app/tools/secrets.py` | get_secret |
| `requirements/app/tools/ioc_extractor.py` | _enabled_map, extract_iocs, _add |

## Logique / extrait par fichier
### requirements/app/main.py
```
import argparse

from cti_core.runner import run


def main():
    parser = argparse.ArgumentParser(description="CTI Scraper")
    parser.add_argument("--config", default="config/conf.yaml", help="Chemin vers le fichier de configuration")
    parser.add_argument("--ai-report", dest="ai_report", action="store_true", help="Forcer l'activation du rapport IA")
    parser.add_argument("--no-ai-report", dest="ai_report", action="store_false", help="Désactiver le rapport IA")
    parser.set_defaults(ai_report=None)
    args = parser.parse_args()
    run(config_path=args.config, force_ai_report=args.ai_report)


if __name__ == "__main__":
    main()
```
### requirements/app/cti_core/orchestrator.py
```
"""
Boucle d'orchestration/scheduling pour lancer le scraper à intervalle régulier.
Utilisation : python -m scripts.orchestrator --config config/conf.yaml
"""
from __future__ import annotations

import logging
import signal
import threading
import time
from pathlib import Path
from typing import Optional

from tools.load_config import load_yaml_config
from tools.scheduling import load_schedule_config, compute_initial_delay
from tools.metrics import RunMetrics, record_run
from cti_core.runner import run


class Orchestrator:
    def __init__(self, config_path: str, metrics_path: str = "data/health.json", logger: Optional[logging.Logger] = None):
        self.config_path = config_path
        self.metrics_path = metrics_path
        self._stop = threading.Event()
        self._running = threading.Lock()
        self.logger = logger or logging.getLogger("orchestrator")
        if not self.logger.handlers:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

        yaml_conf = load_yaml_config(config_path)
        self.schedule = load_schedule_config(yaml_conf.get("scheduling"))

    def stop(self):
        self._stop.set()

    def
```
### requirements/app/cti_core/__init__.py
```
from .config_model import *
from .Source import *
from .scraper import *
from .runner import *
from .crawler_state import *
```
### requirements/app/cti_core/Source.py
```
from typing import Any, Dict, Optional
from pathlib import Path
import hashlib
from tools.crypter import compute_sha256_from_text
from tools.download import download_source
from tools.download_types import DownloadResult, NetworkPolicy, StorageTarget
from tools.overrides import normalize_overrides


class Source:
    """
        Représente une source d'information (site web, API, etc.)

        Attributs :
        - name : Nom de la source
        - url : URL de la source
        - type : Type de la source (html, api, etc.)
        - hash : Hash SHA-256 du contenu, pour vérifier les changements
        - date : Date connue de la source
        - content : Contenu extrait (texte brut)
        - status : État actuel (pending, downloaded, error)
        - error : Message d'erreur éventuel
    """

    def __init__(self, source: Dict):
        self.name: Optional[str] = source.get("name")
        self.url: str = source.get("url", "")
        self.type: str = source.get("type", "html")
        self.hash: Optional[str] = source.get("hash")
        self.date: Optional[str] = source.get("date")
        self.content: Optional[Any] = None
        self.status: str = "pending"
        self.err
```
### requirements/app/cti_core/sources_factory.py
```
from typing import Optional, Set

from cti_core.Source import Source
from tools.html_links import extract_links
from tools.http.url_utils import normalize_url
from tools.http.url_policy import UrlPolicy
from tools.overrides import normalize_overrides


def enqueue_links(current: Source, depth: int, state, max_depth: int, url_policy: UrlPolicy):
    """
    Extrait les liens HTML et les ajoute dans la queue si autorisés.
    """
    if (
        current.status != "downloaded"
        or current.type != "html"
        or depth >= max_depth
        or not isinstance(current.content, str)
    ):
        return
    for link in extract_links(current.content, current.url):
        if not url_policy.can_follow(current.url, link):
            continue
        if state.already_visited(link):
            continue
        normalized = url_policy.normalize(link)
        name = f"{(current.name or 'source')}-d{depth+1}"
        new_source = Source({"url": normalized, "type": "html", "name": name})
        state.add(new_source, depth + 1)
```
### requirements/app/cti_core/config_model.py
```
# Gestion intelligente et structurée de la configuration
from pathlib import Path
import re
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
from tools.config_validator import validate_config
from tools.overrides import normalize_overrides


SUPPORTED_SOURCE_TYPES = {"html", "api", "xml", "pdf", "csv", "txt", "image", "ignore"}


class ConfigModel:
    def __init__(self, yaml_config: str | Path, strict: bool = True):
        self.config_path = Path(yaml_config)
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.yaml_config = load_yaml_config(self.config_path)
        self.keywords = load_keywords_from_config(self.yaml_config)
        self.json_config_str = get_config_as_json_string(self.yaml_config)
        self.network_settings = self.yaml_config.get("network", {
```
### requirements/app/cti_core/runner.py
```
import logging

from cti_core.config_model import ConfigModel
from cti_core.scraper import Scraper
from tools.load_config import get_config_as_json_string
from tools.cache_factory import build_cache
from tools.cache import CacheManager, CacheRegistry
from tools.logger_utils import setup_logger, log_structured
from tools.report import write_report
from cti_core.cli import render_progress, print_summary
from tools.ai_report import generate_ai_report


def build_cache_manager(cache_conf: dict) -> CacheManager | CacheRegistry:
    return build_cache(cache_conf)


def run(config_path: str = "config/conf.yaml", force_ai_report: bool | None = None):
    try:
        config_model = ConfigModel(config_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Erreur de configuration : {exc}")
        return

    logger = setup_logger(config_model.yaml_config.get("logging", {}))

    if config_model.has_warnings():
        for warning in config_model.warnings:
            logger.warning("Avertissement configuration : %s", warning)
        log_structured(logger, logging.WARNING, "config_warnings", warnings=config_model.warnings)

    if config_model.has_errors():
        for err
```
### requirements/app/cti_core/crawler_state.py
```
from collections import deque
from typing import Set
import threading
import contextlib
from .Source import Source


class CrawlerState:
    """Gère la frontier (queue) et les visites pour le crawl."""

    def __init__(self, max_depth: int, max_pages: int | None, normalizer, thread_safe: bool = False):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self._normalizer = normalizer
        self.queue = deque()
        self.visited: Set[str] = set()
        self.pages_processed = 0
        self._thread_safe = thread_safe
        self._lock = threading.Lock() if thread_safe else None

    def _guard(self):
        if not self._thread_safe or self._lock is None:
            return contextlib.nullcontext()
        return self._lock

    def add(self, source: Source, depth: int) -> None:
        if depth > self.max_depth:
            return
        norm = self._normalizer(source.url)
        with self._guard():
            if norm in self.visited:
                return
            self.queue.append((source, depth))

    def has_next(self) -> bool:
        with self._guard():
            if self.max_pages and self.pages_processed >= self.max_pages:
```
### requirements/app/cti_core/scraper.py
```
from typing import Set
from concurrent.futures import ThreadPoolExecutor

from .Source import Source
from .crawler_state import CrawlerState
from cti_core.sources_factory import enqueue_links
from cti_core.result_recorder import ResultRecorder
from tools.cache import CacheManager
from tools.download_types import NetworkPolicy
from tools.http.url_utils import normalize_url, same_domain
import tools.parser as parser
from tools.keywords import find_keyword_hits
from tools.http.client import HttpClient
from tools.http.url_policy import UrlPolicy
from tools.parsers.text_utils import ensure_text


class Scraper:
    def __init__(self, config_model, cache_manager: CacheManager, http_client: HttpClient | None = None):
        self.config_model = config_model
        self.cache = cache_manager
        self.results = []
        self.policy: NetworkPolicy = config_model.network_policy
        crawler_conf = config_model.crawler_settings
        self.max_depth = crawler_conf.get("max_depth", 2)
        self.max_pages = crawler_conf.get("max_pages")
        self.same_domain_only = bool(crawler_conf.get("same_domain_only", True))
        self.allow_domains: Set[str] = set(crawler_conf.get("allow
```
### requirements/app/cti_core/result_recorder.py
```
import threading
from typing import Any
from tools.cache import CacheManager, CacheRegistry
from cti_core.Source import Source
from tools.storage_mongo import save_result


class ResultRecorder:
    """
    Centralise l'écriture thread-safe des résultats et du cache.
    """

    def __init__(self, cache: CacheManager | CacheRegistry, results_store: list[dict[str, Any]]):
        self.cache = cache
        self.results = results_store
        self._lock = threading.Lock()

    def record_cache_hit(self, url: str, source_type: str, name: str, cached_entry) -> None:
        with self._lock:
            self.cache.record_scrape(
                url=url,
                source_type=source_type,
                status="skipped-cache",
                hash_value=cached_entry.hash,
                date=cached_entry.date,
                error=None,
                saved_path=cached_entry.saved_path,
            )
            self.results.append(
                {
                    "url": url,
                    "name": name,
                    "type": source_type,
                    "status": "skipped-cache",
                    "error": None,
                    "saved_path": cached
```
### requirements/app/cti_core/cli.py
```
import json
import sys
from typing import List, Dict, Any


def render_progress(idx: int, total: int, name: str, status: str = ""):
    width = 30
    filled = int(width * idx / total) if total else width
    bar = "=" * filled + ">" + "." * max(0, width - filled - 1)
    sys.stdout.write(f"\r[{bar}] {idx}/{total} {name} {status}")
    sys.stdout.flush()


def print_summary(results: List[Dict[str, Any]], report_path: str | None = None):
    summary = {"sources": results}
    if report_path:
        summary["report"] = report_path
    print(json.dumps(summary, ensure_ascii=False, indent=2))
```
### requirements/app/tools/html_links.py
```
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from urllib.parse import urljoin
import warnings

# Supprime les warnings bs4 quand un contenu XML est parsé via le parser HTML
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


def extract_links(html_content: str, base_url: str):
    soup = BeautifulSoup(html_content, "html.parser")
    links = set()
    for tag in soup.find_all("a", href=True):
        links.add(urljoin(base_url, tag["href"]))
    for tag in soup.find_all("script", src=True):
        links.add(urljoin(base_url, tag["src"]))
    return links
```
### requirements/app/tools/keywords.py
```
from __future__ import annotations

from typing import Dict, Iterable, List


def find_keyword_hits(items: Iterable[str], keywords: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Retourne un dictionnaire {categorie: [mots-clés trouvés]} basé sur une recherche
    insensible à la casse dans la liste de textes fournie.
    """
    hits: Dict[str, List[str]] = {}
    texts = [item.lower() for item in items if isinstance(item, str)]
    if not texts or not keywords:
        return hits

    for category, words in keywords.items():
        found = set()
        for word in words or []:
            needle = (word or "").strip()
            if not needle:
                continue
            lower = needle.lower()
            if any(lower in text for text in texts):
                found.add(needle)
        if found:
            hits[category] = sorted(found)
    return hits
```
### requirements/app/tools/config_utils.py
```
from __future__ import annotations

from typing import Any


def to_int(value: Any, default: int | None = None) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() not in {"false", "0", "no", "n", ""}
    return bool(value)
```
### requirements/app/tools/cache_mongo.py
```
"""
Cache MongoDB minimal pour suivre les scrapes.
Configuration via variables d'environnement :
 - MONGO_URI (obligatoire pour activer)
 - MONGO_DB (défaut: cti)
 - MONGO_CACHE_COLLECTION (défaut: cache)
Le cache ne fait pas de suppression ni d'auto-save (Mongo gère la persistance).
"""
from __future__ import annotations

import os
from typing import Optional

try:
    from pymongo import MongoClient  # type: ignore
except Exception:  # pragma: no cover
    MongoClient = None

from tools.cache import CacheEntry


class MongoCache:
    def __init__(self, uri: str, db_name: str = "cti", collection: str = "cache"):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection
        self._client: Optional["MongoClient"] = None
        self._coll = None
        self._connect()

    def _connect(self):
        if MongoClient is None:
            return
        try:
            self._client = MongoClient(self.uri)
            self._coll = self._client[self.db_name][self.collection_name]
        except Exception:
            self._client = None
            self._coll = None

    def _collection(self):
        if self._coll is None:
            self._con
```
### requirements/app/tools/__init__.py
```
# Tools package
```
### requirements/app/tools/load_config.py
```
import json
from pathlib import Path
from typing import Any
import yaml


def load_yaml_config(path: str | Path) -> dict:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config introuvable: {path}")
    data = yaml.safe_load(path.read_text()) or {}
    if "include" in data and isinstance(data["include"], list):
        for inc in data["include"]:
            inc_path = path.parent / inc
            include_data = yaml.safe_load(inc_path.read_text()) or {}
            data = _deep_merge(data, include_data)
    return data


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _deep_merge(result[k], v)
        elif isinstance(v, list) and isinstance(result.get(k), list):
            # Concatène les listes pour conserver les entrées existantes (ex: sources) tout en ajoutant les nouvelles
            result[k] = result[k] + v
        else:
            result[k] = v
    return result


def get_config_as_json_string(config: dict) -> str:
    return json.dumps(config, indent=2)


def load_keywords_from_confi
```
### requirements/app/tools/report_sections.py
```
from __future__ import annotations

from typing import Any, Dict, List

MAX_SNIPPET_LEN = 300


def _truncate(text: str, max_len: int = MAX_SNIPPET_LEN) -> str:
    if not isinstance(text, str):
        return text
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def build_markdown_section(
    res: Dict[str, Any],
    heading_prefix: str,
    detail_path: str | None = None,
    extracted_limit: int | None = None,
    include_keywords: bool = True,
) -> List[str]:
    lines = [f"{heading_prefix} {res.get('name') or res.get('url')}"]
    lines.append(f"- Type : {res.get('type')}")
    lines.append(f"- Statut : {res.get('status')}")
    if res.get("error"):
        lines.append(f"- Erreur : {res.get('error')}")
    if res.get("saved_path"):
        lines.append(f"- Fichier : {res.get('saved_path')}")
    if detail_path:
        lines.append(f"- Détail : {detail_path}")
    extracted = res.get("extracted") or []
    if extracted and extracted_limit != 0:
        lines.append("- Extraits :")
        limit = extracted_limit if extracted_limit is not None else len(extracted)
        for item in extracted[:limit]:
            lines.append(f"  - {_t
```
### requirements/app/tools/scheduling.py
```
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any, Optional

from tools.config_utils import to_bool, to_int


def parse_interval_seconds(value: Any, default: int = 3600) -> int:
    """
    Convertit un intervalle sous forme str ou int en secondes.
    Accepte "6h", "15m", "30s", "1d" ou un entier (secondes).
    """
    if isinstance(value, (int, float)):
        return int(value)
    if not isinstance(value, str):
        return default
    text = value.strip().lower()
    if text.endswith("ms"):
        num = to_int(text[:-2], default=None)
        return int(num / 1000) if num is not None else default
    if text.endswith("s"):
        num = to_int(text[:-1], default=None)
        return num if num is not None else default
    if text.endswith("m"):
        num = to_int(text[:-1], default=None)
        return num * 60 if num is not None else default
    if text.endswith("h"):
        num = to_int(text[:-1], default=None)
        return num * 3600 if num is not None else default
    if text.endswith("d"):
        num = to_int(text[:-1], default=None)
        return num * 86400 if num is not None else default
    re
```
### requirements/app/tools/ai_runner.py
```
"""
Utilitaires d'exécution LLM en CLI avec gestion sécurisée du prompt.
- Permet de passer le prompt via stdin ou via un fichier temporaire pour éviter
  les erreurs "argument list too long" ou les CLIs qui ne lisent pas stdin.
"""
from __future__ import annotations

import shlex
import subprocess
import tempfile
from typing import Optional


def run_cli_llm(
    command: str,
    prompt: str,
    timeout: int = 120,
    pass_prompt_as_arg: bool = False,
    prompt_via_file: bool = False,
) -> str:
    """
    Exécute une commande LLM locale.
    - pass_prompt_as_arg : ajoute le prompt (ou le chemin du fichier) aux arguments
    - prompt_via_file : écrit le prompt dans un fichier temporaire pour éviter les lignes trop longues
      et le passe en stdin (ou en argument si pass_prompt_as_arg=True)
    """
    cmd_list = shlex.split(command)
    run_kwargs = {"text": True, "capture_output": True, "timeout": timeout}

    if prompt_via_file:
        with tempfile.NamedTemporaryFile(mode="w+", delete=True) as tmp:
            tmp.write(prompt)
            tmp.flush()
            if pass_prompt_as_arg:
                cmd_list = cmd_list + [tmp.name]
                run_kwargs["input"]
```
### requirements/app/tools/cache.py
```
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse
import threading


@dataclass
class CacheEntry:
    url: str
    type: str
    hash: Optional[str] = None
    date: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None
    saved_path: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheEntry":
        return cls(
            url=data.get("url", ""),
            type=data.get("type", ""),
            hash=data.get("hash"),
            date=data.get("date"),
            status=data.get("status"),
            error=data.get("error"),
            saved_path=data.get("saved_path"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CacheManager:
    def __init__(self, cache_file: str | Path, auto_save: bool = True):
        self.cache_path = Path(cache_file)
        self.auto_save = auto_save
        self._entries: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self) -> None:
        i
```
### requirements/app/tools/parser.py
```
from typing import Any, List, Callable, Dict

from tools.parsers.html_parser import parse_html
from tools.parsers.json_parser import parse_json
from tools.parsers.xml_parser import parse_xml
from tools.parsers.csv_parser import parse_csv
from tools.parsers.pdf_parser import parse_pdf
from tools.parsers.ocr_parser import parse_image
from tools.parsers.txt_parser import parse_txt
from tools.parsers.text_utils import ensure_text
from tools.ioc_extractor import extract_iocs
from tools.content_sanitizer import sanitize_html, sanitize_xml
from copy import deepcopy
from typing import Optional


PARSERS: dict[str, Callable[[Any, dict], List[str]]] = {
    "html": parse_html,
    "api": parse_json,
    "xml": parse_xml,
    "csv": parse_csv,
    "pdf": parse_pdf,
    "image": parse_image,
    "txt": parse_txt,
}


class ParserRegistry:
    """
    Petit registre injectable pour lier un type à un parseur.
    Permet de surcharger/ajouter des parseurs dans les tests ou extensions.
    """

    def __init__(self, initial: dict[str, Callable[[Any, dict], List[str]]] | None = None):
        self._parsers = dict(initial or {})

    def get(self, name: str) -> Callable[[Any, dict], List[str]] | No
```
### requirements/app/tools/content_sanitizer.py
```
"""
Sanitisation légère des contenus HTML/XML.
Objectif : enlever scripts/style/commentaires et normaliser le texte pour limiter
les surprises lors de la réutilisation ou du reporting.
"""
from __future__ import annotations

from bs4 import BeautifulSoup, Comment


def sanitize_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Supprime scripts/styles/comments
    for tag in soup(["script", "style"]):
        tag.decompose()
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    # Retourne le markup nettoyé (structure conservée)
    return str(soup)


def sanitize_xml(xml: str) -> str:
    soup = BeautifulSoup(xml, "xml")
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    # retire scripts dans les flux xml/atom/rss
    for tag in soup.find_all("script"):
        tag.decompose()
    return str(soup)
```
### requirements/app/tools/secrets.py
```
"""
Récupération de secrets via variables d'environnement ou Vault (optionnel).
- Si la variable d'env <KEY> est présente, on l'utilise.
- Sinon, si VAULT_ADDR et VAULT_TOKEN sont définis et hvac installé, on tente de lire
  un secret KV v2 à l'emplacement VAULT_SECRET_PATH (défaut: secret/data/cti).
"""
from __future__ import annotations

import os
from typing import Optional

try:
    import hvac  # type: ignore
except Exception:  # pragma: no cover
    hvac = None


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    # Priorité env
    val = os.getenv(key)
    if val:
        return val
    # Vault (optionnel)
    if hvac is None:
        return default
    addr = os.getenv("VAULT_ADDR")
    token = os.getenv("VAULT_TOKEN")
    path = os.getenv("VAULT_SECRET_PATH", "secret/data/cti")
    if not addr or not token:
        return default
    try:
        client = hvac.Client(url=addr, token=token)
        resp = client.secrets.kv.v2.read_secret_version(path=path)
        data = resp.get("data", {}).get("data", {})
        return data.get(key, default)
    except Exception:
        return default
```
### requirements/app/tools/ioc_extractor.py
```
from __future__ import annotations

import re
from typing import Iterable, List, Dict


DEFAULT_PATTERNS = {
    "cve": re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE),
    "url": re.compile(r"https?://[^\s)'\"<>]+", re.IGNORECASE),
    "ipv4": re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
    ),
}


def _enabled_map(options) -> Dict[str, bool]:
    """
    Normalise la config extract_iocs.
    - bool => tous les patterns activés ou désactivés
    - dict => active uniquement les clés truthy (cve/url/ipv4)
    """
    if isinstance(options, bool):
        return {name: options for name in DEFAULT_PATTERNS.keys()}
    if isinstance(options, dict):
        return {name: bool(options.get(name, False)) for name in DEFAULT_PATTERNS.keys()}
    return {}


def extract_iocs(texts: Iterable[str], options) -> List[str]:
    """
    Extrait des IOC simples (CVE, URLs, IPv4) à partir d'une liste de textes.
    Utilise des regex rapides pour limiter les faux positifs.
    """
    enabled = _enabled_map(options)
    if not enabled or not any(enabled.values()):
        return []

    seen = set()
    results: List[str] = []

    def _add(match: s
```

## Signalements (best practices / redondance)
| Type | Cible | Détail |
|---|---|---|
| dup_function_name | __init__ | Même nom de fonction dans plusieurs fichiers (risque collision/ambiguïté). (requirements/app/cti_core/orchestrator.py, requirements/app/cti_core/Source.py, requirements/app/cti_core/config_model.py, requirements/app/cti_core/crawler_state.py, requirements/app/cti_core/scraper.py) |
| best_practice | requirements/app/cti_core/runner.py | Print debug présent |
| best_practice | requirements/app/cti_core/cli.py | Print debug présent |
| best_practice | requirements/app/tools/cache_mongo.py | Catch large (Exception) détecté |
| best_practice | requirements/app/tools/secrets.py | Catch large (Exception) détecté |

> Rapport généré automatiquement par l’agent revue (limité aux extraits scannés).