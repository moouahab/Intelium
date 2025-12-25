from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any, Set


@dataclass
class NetworkPolicy:
    enforce_https: bool = True
    block_private: bool = True
    allow_domains: Optional[Set[str]] = None
    max_bytes: Optional[int] = None
    timeout: int = 10
    connect_timeout: Optional[int] = None
    read_timeout: Optional[int] = None


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
