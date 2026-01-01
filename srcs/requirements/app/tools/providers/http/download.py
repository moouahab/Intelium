from pathlib import Path
from typing import Any, Optional
import mimetypes
import tempfile
import subprocess

from tools.providers.http.download_types import DownloadResult, NetworkPolicy, StorageTarget
from tools.providers.http import network
from tools.parsers.text_utils import ensure_text
from tools.providers.http.request_context import RequestContext
from tools.parsing.content_sanitizer import sanitize_html, sanitize_xml
from tools.providers.http.scanner import run_scan


def _persist_content(
    storage: Optional[StorageTarget],
    extension: str,
    content: bytes,
    policy: NetworkPolicy,
) -> tuple[Optional[Path], Optional[str]]:
    """
    Écrit le contenu, vérifie la sandbox et lance un scan si configuré.
    Retourne (saved_path, error_message).
    """
    saved = _save_content(storage, extension, content)
    if saved and not _is_path_in_sandbox(saved, policy.sandbox_dir):
        return saved, "Écriture hors sandbox interdite"
    if saved and policy.scan_command:
        error = run_scan(saved, policy.scan_command, timeout=policy.scan_timeout)
        if error:
            return saved, f"Scan échoué: {error}"
    return saved, None


def _save_content(storage: Optional[StorageTarget], extension: str, content: bytes) -> Optional[Path]:
    if not storage:
        return None
    path = storage.path_for(extension)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def _is_path_in_sandbox(path: Path, sandbox: Optional[str]) -> bool:
    if not sandbox:
        return True
    try:
        sandbox_path = Path(sandbox).resolve()
        return sandbox_path in path.resolve().parents or path.resolve() == sandbox_path
    except Exception:
        return False


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


def download_with_context(
    source: dict,
    ctx: RequestContext,
    storage: Optional[StorageTarget] = None,
) -> DownloadResult:
    """
    Pipeline unifié : utilise le RequestContext (policy/headers/proxy) pour télécharger en streaming
    avec respect de max_bytes et sauvegarde éventuelle.
    """
    stype = (source.get("type") or "html").lower()
    url = source.get("url")
    if stype == "ignore":
        return DownloadResult(status="skipped", content=None)

    try:
        policy = ctx.policy
        timeout = (
            (policy.connect_timeout, policy.read_timeout)
            if policy.connect_timeout or policy.read_timeout
            else policy.timeout
        )
        verify_opt = policy.ca_bundle if policy.ca_bundle else policy.verify_ssl
        resp = network.requests.get(url, timeout=timeout, stream=True, headers=ctx.headers, proxies=ctx.proxy, verify=verify_opt)
        if resp.status_code >= 400:
            resp.close()
            return DownloadResult(status="http-error", content=None, error=f"HTTP {resp.status_code}", status_code=resp.status_code)
        resp.raise_for_status()
        # Pinning fingerprint si demandé
        if ctx.policy.pinned_fingerprints:
            try:
                cert = resp.raw.connection.sock.getpeercert(binary_form=True)  # type: ignore
                import ssl
                import hashlib

                fp = hashlib.sha256(cert).hexdigest()
                if fp not in ctx.policy.pinned_fingerprints:
                    resp.close()
                    return DownloadResult(status="error", content=None, error="Certificat TLS non autorisé (pinning)")
            except Exception as exc:
                resp.close()
                return DownloadResult(status="error", content=None, error=f"Echec pinning TLS: {exc}")
    except Exception as exc:
        return DownloadResult(status="error", content=None, error=str(exc))

    ctype = resp.headers.get("Content-Type", "").lower()
    if _check_content_length(resp, ctx.policy.max_bytes):
        resp.close()
        return _too_large_error(ctx.policy.max_bytes or 0)

    content_bytes, truncated = _stream_content(resp, ctx.policy.max_bytes)
    size_bytes = len(content_bytes) if content_bytes else None
    if truncated:
        return _too_large_error(ctx.policy.max_bytes or 0)
    if content_bytes is None:
        return DownloadResult(status="error", content=None, error="Contenu vide ou non récupéré")

    text_content = ensure_text(content_bytes, encoding=resp.encoding)
    if stype == "html" or stype not in {"api", "xml", "pdf", "csv", "txt", "image"}:
        saved, error = _persist_content(storage, ".html", content_bytes, ctx.policy)
        if error:
            return DownloadResult(status="error", content=None, error=error, saved_path=saved)
        if ctx.policy.sanitize_downloads:
            text_content = sanitize_html(text_content)
        return DownloadResult(
            status="downloaded",
            content=text_content,
            content_type=ctype or "text/html",
            saved_path=saved,
            status_code=resp.status_code,
            size_bytes=size_bytes,
        )

    if stype == "api":
        if "json" not in ctype:
            return DownloadResult(status="error", content=None, error=f"Type de contenu non supporté pour l'API: {ctype}")
        saved, error = _persist_content(storage, ".json", content_bytes, ctx.policy)
        if error:
            return DownloadResult(status="error", content=None, error=error, saved_path=saved)
        return DownloadResult(
            status="downloaded",
            content=text_content,
            content_type=ctype or "application/json",
            saved_path=saved,
            status_code=resp.status_code,
            size_bytes=size_bytes,
        )

    if stype == "xml":
        saved, error = _persist_content(storage, ".xml", content_bytes, ctx.policy)
        if error:
            return DownloadResult(status="error", content=None, error=error, saved_path=saved)
        if ctx.policy.sanitize_downloads:
            text_content = sanitize_xml(text_content)
        return DownloadResult(
            status="downloaded",
            content=text_content,
            content_type=ctype or "application/xml",
            saved_path=saved,
            status_code=resp.status_code,
            size_bytes=size_bytes,
        )

    if stype == "pdf":
        saved, error = _persist_content(storage, ".pdf", content_bytes, ctx.policy)
        if error:
            return DownloadResult(status="error", content=None, error=error, saved_path=saved)
        return DownloadResult(
            status="downloaded",
            content=content_bytes,
            content_type=ctype or "application/pdf",
            saved_path=saved,
            status_code=resp.status_code,
            size_bytes=size_bytes,
        )

    if stype == "csv":
        saved, error = _persist_content(storage, ".csv", content_bytes, ctx.policy)
        if error:
            return DownloadResult(status="error", content=None, error=error, saved_path=saved)
        return DownloadResult(
            status="downloaded",
            content=text_content,
            content_type=ctype or "text/csv",
            saved_path=saved,
            status_code=resp.status_code,
            size_bytes=size_bytes,
        )

    if stype == "txt":
        saved, error = _persist_content(storage, ".txt", content_bytes, ctx.policy)
        if error:
            return DownloadResult(status="error", content=None, error=error, saved_path=saved)
        return DownloadResult(
            status="downloaded",
            content=text_content,
            content_type=ctype or "text/plain",
            saved_path=saved,
            status_code=resp.status_code,
            size_bytes=size_bytes,
        )

    if stype == "image":
        ext = mimetypes.guess_extension(ctype.split(";")[0]) if ctype else ".bin"
        ext = ext or ".bin"
        saved, error = _persist_content(storage, ext, content_bytes, ctx.policy)
        if error:
            return DownloadResult(status="error", content=None, error=error, saved_path=saved)
        return DownloadResult(
            status="downloaded",
            content=content_bytes,
            content_type=ctype or "application/octet-stream",
            saved_path=saved,
            status_code=resp.status_code,
            size_bytes=size_bytes,
        )

    return DownloadResult(status="error", content=None, error="Type non supporté")


def download_source(
    source: dict,
    policy: NetworkPolicy,
    storage: Optional[StorageTarget] = None,
    headers: Optional[dict] = None,
    proxies: Optional[dict] = None,
    ctx: Optional[RequestContext] = None,
) -> DownloadResult:
    if ctx is None:
        ctx = RequestContext(
            policy=policy,
            headers=headers or {},
            respect_robots=True,
            crawl_delay=0,
            proxy=proxies,
        )
    return download_with_context(source, ctx, storage=storage)
