from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import mimetypes
import tempfile

from tools.providers.http.download_types import DownloadResult, NetworkPolicy, StorageTarget
from tools.providers.http import network
from tools.parsers.text_utils import ensure_text
from tools.providers.http.request_context import RequestContext
from tools.parsing.content_sanitizer import sanitize_html, sanitize_xml
from tools.providers.http.scanner import run_scan


@dataclass(frozen=True)
class DownloadFormat:
    extension: str
    content_type: str
    binary: bool = False


DOWNLOAD_FORMATS = {
    "html": DownloadFormat(".html", "text/html"),
    "api": DownloadFormat(".json", "application/json"),
    "stix": DownloadFormat(".json", "application/json"),
    "xml": DownloadFormat(".xml", "application/xml"),
    "pdf": DownloadFormat(".pdf", "application/pdf", binary=True),
    "csv": DownloadFormat(".csv", "text/csv"),
    "txt": DownloadFormat(".txt", "text/plain"),
    "image": DownloadFormat(".bin", "application/octet-stream", binary=True),
}
SANITIZERS = {"html": sanitize_html, "xml": sanitize_xml}


def _persist_content(
    storage: Optional[StorageTarget],
    extension: str,
    content: bytes,
    policy: NetworkPolicy,
) -> tuple[Optional[Path], Optional[str]]:
    """Valide et scanne un fichier temporaire avant publication atomique.

    Un contenu rejeté n'écrase jamais un artefact existant et n'expose aucun
    saved_path aux étapes suivantes. Le scan s'applique aussi sans stockage.
    """
    if policy.max_bytes and len(content) > policy.max_bytes:
        return None, "Téléchargement interrompu : taille > limite"
    target = storage.path_for(extension) if storage else None
    if target and not _is_path_in_sandbox(target, policy.sandbox_dir):
        return None, "Écriture hors sandbox interdite"
    if target is None and not policy.scan_command:
        return None, None
    pending = None
    try:
        if target is not None:
            target = target.resolve()
            target.parent.mkdir(parents=True, exist_ok=True)
            directory = target.parent
        else:
            directory = Path(policy.sandbox_dir).resolve() if policy.sandbox_dir else None
            if directory:
                directory.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=directory, prefix=".pending-", suffix=extension, delete=False) as handle:
            pending = Path(handle.name)
            handle.write(content)
        if policy.scan_command:
            error = run_scan(pending, policy.scan_command, timeout=policy.scan_timeout, scanner=policy.scanner)
            if error:
                return None, f"Scan échoué: {error}"
        if target is not None:
            pending.replace(target)
        return target, None
    except (OSError, ValueError) as exc:
        return None, f"Écriture ou scan impossible: {exc}"
    finally:
        if pending is not None:
            pending.unlink(missing_ok=True)


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
        resp = network.get_response(
            url, ctx.policy, headers=ctx.headers, proxies=ctx.proxy,
            redirect_headers=ctx.redirect_headers,
        )
        if resp.status_code >= 400:
            resp.close()
            return DownloadResult(status="http-error", content=None, error=f"HTTP {resp.status_code}", status_code=resp.status_code)
        resp.raise_for_status()
    except Exception as exc:
        return DownloadResult(status="error", content=None, error=str(exc))

    ctype = resp.headers.get("Content-Type", "").lower()
    if _check_content_length(resp, ctx.policy.max_bytes):
        resp.close()
        return _too_large_error(ctx.policy.max_bytes or 0)

    try:
        content_bytes, truncated = _stream_content(resp, ctx.policy.max_bytes)
    except Exception as exc:
        return DownloadResult(status="error", content=None, error=f"Lecture HTTP interrompue: {exc}")
    size_bytes = len(content_bytes) if content_bytes else None
    if truncated:
        return _too_large_error(ctx.policy.max_bytes or 0)
    if content_bytes is None:
        return DownloadResult(status="error", content=None, error="Contenu vide ou non récupéré")

    # Preserve the historical HTML fallback for unknown source types.
    format_key = stype if stype in DOWNLOAD_FORMATS else "html"
    download_format = DOWNLOAD_FORMATS[format_key]
    if format_key == "api" and "json" not in ctype:
        return DownloadResult(status="error", content=None, error=f"Type de contenu non supporté pour l'API: {ctype}")

    extension = download_format.extension
    if format_key == "image":
        extension = mimetypes.guess_extension(ctype.split(";")[0]) or extension
    saved, error = _persist_content(storage, extension, content_bytes, ctx.policy)
    if error:
        return DownloadResult(status="error", content=None, error=error, saved_path=saved)

    content = content_bytes
    if not download_format.binary:
        content = ensure_text(content_bytes, encoding=resp.encoding)
        sanitizer = SANITIZERS.get(format_key)
        if ctx.policy.sanitize_downloads and sanitizer:
            content = sanitizer(content)
    return DownloadResult(
        status="downloaded",
        content=content,
        content_type=ctype or download_format.content_type,
        saved_path=saved,
        status_code=resp.status_code,
        size_bytes=size_bytes,
    )


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
