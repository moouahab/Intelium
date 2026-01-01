from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any, Set


@dataclass
class NetworkPolicy:
    enforce_https: bool = True
    block_private: bool = True
    offline: bool = False  # mode cache-only
    allow_domains: Optional[Set[str]] = None
    max_bytes: Optional[int] = None
    timeout: int = 10
    connect_timeout: Optional[int] = None
    read_timeout: Optional[int] = None
    verify_ssl: bool = True
    ca_bundle: Optional[str] = None
    pinned_fingerprints: Optional[Set[str]] = None  # empreintes SHA256 de certificats TLS autorisés
    scanner: Optional[str] = None  # none|yara|av (optionnel)
    scan_command: Optional[str] = None  # commande effective de scan (utilise {file} comme placeholder)
    scan_timeout: int = 60
    sanitize_downloads: bool = False
    sandbox_dir: Optional[str] = None  # répertoire racine autorisé pour l'écriture
    metrics_path: Optional[str] = None  # fichier health.json optionnel pour tracer fetch success/erreur


@dataclass
class StorageTarget:
    base_dir: Path
    theme: str
    name: str
    def path_for(self, extension: str) -> Path:
        return self.base_dir / self.theme / f"{self.name}{extension}"


@dataclass
class DownloadResult:
    status: str
    content: Any
    content_type: Optional[str] = None
    error: Optional[str] = None
    saved_path: Optional[Path] = None
    hash: Optional[str] = None
    date: Optional[str] = None
    status_code: Optional[int] = None
    size_bytes: Optional[int] = None
