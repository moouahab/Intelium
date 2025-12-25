from pathlib import Path
from typing import Any, Optional
import mimetypes

from tools.download_types import DownloadResult, NetworkPolicy, StorageTarget
from tools.http import network


def _save_content(storage: Optional[StorageTarget], extension: str, content: bytes) -> Optional[Path]:
    if not storage:
        return None
    path = storage.path_for(extension)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def download_source(
    source: dict,
    policy: NetworkPolicy,
    storage: Optional[StorageTarget] = None,
    headers: Optional[dict] = None,
    proxies: Optional[dict] = None,
) -> DownloadResult:
    stype = (source.get("type") or "html").lower()
    url = source.get("url")
    if stype == "ignore":
        return DownloadResult(status="skipped", content=None)

    try:
        timeout = (policy.connect_timeout, policy.read_timeout) if policy.connect_timeout or policy.read_timeout else policy.timeout
        resp = network.requests.get(url, timeout=timeout, stream=True, headers=headers, proxies=proxies)
        if resp.status_code >= 400:
            return DownloadResult(status="http-error", content=None, error=f"HTTP {resp.status_code}", status_code=resp.status_code)
        resp.raise_for_status()
    except Exception as exc:
        return DownloadResult(status="error", content=None, error=str(exc))

    ctype = resp.headers.get("Content-Type", "").lower()
    content_bytes = resp.content
    if policy.max_bytes and len(content_bytes) > policy.max_bytes:
        return DownloadResult(status="error", content=None, error=f"Téléchargement interrompu : taille > limite ({policy.max_bytes} octets)")

    if stype == "html" or stype not in {"api", "xml", "pdf", "csv", "txt", "image"}:
        saved = _save_content(storage, ".html", content_bytes)
        return DownloadResult(status="downloaded", content=resp.text, content_type=ctype or "text/html", saved_path=saved, status_code=resp.status_code)

    if stype == "api":
        if "json" not in ctype:
            return DownloadResult(status="error", content=None, error=f"Type de contenu non supporté pour l'API: {ctype}")
        saved = _save_content(storage, ".json", content_bytes)
        return DownloadResult(status="downloaded", content=resp.text, content_type=ctype or "application/json", saved_path=saved, status_code=resp.status_code)

    if stype == "xml":
        saved = _save_content(storage, ".xml", content_bytes)
        return DownloadResult(status="downloaded", content=resp.text, content_type=ctype or "application/xml", saved_path=saved, status_code=resp.status_code)

    if stype == "pdf":
        saved = _save_content(storage, ".pdf", content_bytes)
        return DownloadResult(status="downloaded", content=content_bytes, content_type=ctype or "application/pdf", saved_path=saved, status_code=resp.status_code)

    if stype == "csv":
        saved = _save_content(storage, ".csv", content_bytes)
        return DownloadResult(status="downloaded", content=resp.text, content_type=ctype or "text/csv", saved_path=saved, status_code=resp.status_code)

    if stype == "txt":
        saved = _save_content(storage, ".txt", content_bytes)
        return DownloadResult(status="downloaded", content=resp.text, content_type=ctype or "text/plain", saved_path=saved, status_code=resp.status_code)

    if stype == "image":
        ext = mimetypes.guess_extension(ctype.split(";")[0]) if ctype else ".bin"
        ext = ext or ".bin"
        saved = _save_content(storage, ext, content_bytes)
        return DownloadResult(status="downloaded", content=content_bytes, content_type=ctype or "application/octet-stream", saved_path=saved, status_code=resp.status_code)

    return DownloadResult(status="error", content=None, error="Type non supporté")
