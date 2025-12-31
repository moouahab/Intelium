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
    extracted: Optional[list] = None
    keywords: Optional[dict] = None

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
            extracted=data.get("extracted"),
            keywords=data.get("keywords"),
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
        if not self.cache_path.exists():
            with self._lock:
                self._entries = {}
            return
        try:
            data = json.loads(self.cache_path.read_text() or "{}")
            if not isinstance(data, dict):
                data = {}
            with self._lock:
                self._entries = {
                    url: CacheEntry.from_dict(entry) for url, entry in data.items() if isinstance(entry, dict)
                }
        except (json.JSONDecodeError, OSError):
            with self._lock:
                self._entries = {}

    def save(self) -> None:
        with self._lock:
            payload = {url: entry.to_dict() for url, entry in self._entries.items()}
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(json.dumps(payload, indent=2))

    def get(self, url: str) -> Optional[CacheEntry]:
        with self._lock:
            return self._entries.get(url)

    def update(self, entry: CacheEntry) -> None:
        with self._lock:
            self._entries[entry.url] = entry
        if self.auto_save:
            self.save()

    def record_scrape(
        self,
        url: str,
        source_type: str,
        status: str,
        hash_value: Optional[str] = None,
        date: Optional[str] = None,
        error: Optional[str] = None,
        saved_path: Optional[str] = None,
        extracted: Optional[list] = None,
        keywords: Optional[dict] = None,
    ) -> CacheEntry:
        if date is None:
            date = datetime.now(timezone.utc).isoformat()
        entry = CacheEntry(
            url=url,
            type=source_type,
            hash=hash_value,
            date=date,
            status=status,
            error=error,
            saved_path=saved_path,
            extracted=extracted,
            keywords=keywords,
        )
        self.update(entry)
        return entry

    def has_changed(self, url: str, current_hash: Optional[str]) -> bool:
        """Retourne True si l'URL n'est pas en cache ou si le hash diffère."""
        cached = self.get(url)
        if cached is None:
            return True
        if cached.hash is None or current_hash is None:
            return True
        return cached.hash != current_hash

    def clear(self) -> None:
        with self._lock:
            self._entries = {}
        if self.cache_path.exists():
            try:
                self.cache_path.unlink()
            except OSError:
                pass


class CacheRegistry:
    """
    Permet de stocker un cache par site (fichier JSON par domaine).
    Expose la même API minimale que CacheManager pour l'utiliser dans le scraper.
    """
    def __init__(self, base_dir: str | Path, auto_save: bool = True):
        self.base_dir = Path(base_dir)
        self.auto_save = auto_save
        self._managers: Dict[Path, CacheManager] = {}
        self._lock = threading.Lock()

    def _path_for(self, url: str) -> Path:
        host = urlparse(url).hostname or "default"
        host_slug = host.replace(".", "-")
        return self.base_dir / f"{host_slug}.json"

    def _get_manager(self, url: str) -> CacheManager:
        path = self._path_for(url)
        with self._lock:
            if path not in self._managers:
                self._managers[path] = CacheManager(path, auto_save=self.auto_save)
            return self._managers[path]

    def get(self, url: str) -> Optional[CacheEntry]:
        return self._get_manager(url).get(url)

    def record_scrape(
        self,
        url: str,
        source_type: str,
        status: str,
        hash_value: Optional[str] = None,
        date: Optional[str] = None,
        error: Optional[str] = None,
        saved_path: Optional[str] = None,
        extracted: Optional[list] = None,
        keywords: Optional[dict] = None,
    ) -> CacheEntry:
        return self._get_manager(url).record_scrape(
            url=url,
            source_type=source_type,
            status=status,
            hash_value=hash_value,
            date=date,
            error=error,
            saved_path=saved_path,
            extracted=extracted,
            keywords=keywords,
        )

    def has_changed(self, url: str, current_hash: Optional[str]) -> bool:
        return self._get_manager(url).has_changed(url, current_hash)
