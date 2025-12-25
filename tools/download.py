from pathlib import Path
from typing import Any, Optional
import mimetypes

from tools.download_types import DownloadResult, NetworkPolicy, StorageTarget
from tools.http import network
from tools.parsers.text_utils import ensure_text


def _save_content(storage: Optional[StorageTarget], extension: str, content: bytes) -> Optional[Path]:
    if not storage:
        return None
    path = storage.path_for(extension)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def _too_large_error(max_bytes: int) -> DownloadResult:
    return DownloadResult(
        status="error",
        content=None,
        error=f"Téléchargement interrompu : taille > limite ({max_bytes} octets)",
    )


def _stream_content(resp, max_bytes: Optional[int]) -> tuple[Optional[bytes], bool]:
    """
    Lit la réponse en streaming pour éviter de charger de gros fichiers en mémoire.
    Retourne (content_bytes, truncated_flag).
    """
    data = bytearray()
    truncated = False
    try:
        for chunk in resp.iter_content(chunk_size=8192):
            if not chunk:
                continue
            data.extend(chunk)
            if max_bytes and len(data) > max_bytes:
                truncated = True
                break
    finally:
        resp.close()
    return (bytes(data) if not truncated else None, truncated)


def _check_content_length(resp, max_bytes: Optional[int]) -> bool:
    if not max_bytes:
        return False
    try:
        length = int(resp.headers.get("Content-Length", 0))
    except (TypeError, ValueError):
        return False
    return length > max_bytes


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
    if _check_content_length(resp, policy.max_bytes):
        resp.close()
        return _too_large_error(policy.max_bytes or 0)

    content_bytes, truncated = _stream_content(resp, policy.max_bytes)
    if truncated:
        return _too_large_error(policy.max_bytes or 0)
    if content_bytes is None:
        return DownloadResult(status="error", content=None, error="Contenu vide ou non récupéré")

    text_content = ensure_text(content_bytes, encoding=resp.encoding)
    if stype == "html" or stype not in {"api", "xml", "pdf", "csv", "txt", "image"}:
        saved = _save_content(storage, ".html", content_bytes)
        return DownloadResult(
            status="downloaded",
            content=text_content,
            content_type=ctype or "text/html",
            saved_path=saved,
            status_code=resp.status_code,
        )

    if stype == "api":
        if "json" not in ctype:
            return DownloadResult(status="error", content=None, error=f"Type de contenu non supporté pour l'API: {ctype}")
        saved = _save_content(storage, ".json", content_bytes)
        return DownloadResult(
            status="downloaded",
            content=text_content,
            content_type=ctype or "application/json",
            saved_path=saved,
            status_code=resp.status_code,
        )

    if stype == "xml":
        saved = _save_content(storage, ".xml", content_bytes)
        return DownloadResult(
            status="downloaded",
            content=text_content,
            content_type=ctype or "application/xml",
            saved_path=saved,
            status_code=resp.status_code,
        )

    if stype == "pdf":
        saved = _save_content(storage, ".pdf", content_bytes)
        return DownloadResult(status="downloaded", content=content_bytes, content_type=ctype or "application/pdf", saved_path=saved, status_code=resp.status_code)

    if stype == "csv":
        saved = _save_content(storage, ".csv", content_bytes)
        return DownloadResult(
            status="downloaded",
            content=text_content,
            content_type=ctype or "text/csv",
            saved_path=saved,
            status_code=resp.status_code,
        )

    if stype == "txt":
        saved = _save_content(storage, ".txt", content_bytes)
        return DownloadResult(
            status="downloaded",
            content=text_content,
            content_type=ctype or "text/plain",
            saved_path=saved,
            status_code=resp.status_code,
        )

    if stype == "image":
        ext = mimetypes.guess_extension(ctype.split(";")[0]) if ctype else ".bin"
        ext = ext or ".bin"
        saved = _save_content(storage, ext, content_bytes)
        return DownloadResult(status="downloaded", content=content_bytes, content_type=ctype or "application/octet-stream", saved_path=saved, status_code=resp.status_code)

    return DownloadResult(status="error", content=None, error="Type non supporté")
