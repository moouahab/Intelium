from __future__ import annotations

import logging
from io import BytesIO
from typing import List, Any

from tools.parsers.text_utils import ensure_text

logger = logging.getLogger(__name__)

try:
    import pdfplumber

    HAS_PDF = True
except Exception:
    pdfplumber = None  # type: ignore
    HAS_PDF = False


def _to_bytes(content: Any) -> bytes:
    if isinstance(content, bytes):
        return content
    if content is None:
        return b""
    return ensure_text(content).encode("utf-8", errors="ignore")


def _image_description(img: Any, page_index: int) -> str | None:
    if not isinstance(img, dict):
        return None
    width = img.get("width")
    height = img.get("height")
    # pdfplumber expose parfois x0/x1 et top/bottom sans width/height
    if not width and "x0" in img and "x1" in img:
        try:
            width = float(img["x1"]) - float(img["x0"])
        except Exception:
            width = None
    if not height and "top" in img and "bottom" in img:
        try:
            height = float(img["bottom"]) - float(img["top"])
        except Exception:
            height = None
    parts = [f"page={page_index}"]
    if width:
        try:
            parts.append(f"width={int(width)}")
        except Exception:
            pass
    if height:
        try:
            parts.append(f"height={int(height)}")
        except Exception:
            pass
    return f"[image {' '.join(parts)}]" if parts else None


def _log_error(conf: dict, message: str, exc: Exception) -> None:
    mode = str(conf.get("errors", "")).lower()
    if mode in {"log", "warn"}:
        logger.warning("PDF parsing warning: %s (%s)", message, exc)


def parse_pdf(content: bytes | str, conf: dict) -> List[str]:
    if not HAS_PDF:
        return []
    data = _to_bytes(content)
    if not data:
        return []
    extract_text = conf.get("extract_text", True)
    keep_images = conf.get("keep_images", False)
    max_pages = conf.get("max_pages")
    max_chars = conf.get("max_chars")
    max_total_chars = conf.get("max_total_chars")
    results: List[str] = []
    total_chars = 0
    stop = False
    try:
        with pdfplumber.open(BytesIO(data)) as pdf:
            for idx, page in enumerate(pdf.pages):
                if isinstance(max_pages, int) and max_pages >= 0 and idx >= max_pages:
                    break
                if extract_text:
                    try:
                        text = page.extract_text() or ""
                    except Exception as exc:
                        _log_error(conf, "extract_text failed", exc)
                        text = ""
                    text = text.strip()
                    if text:
                        if isinstance(max_chars, int) and max_chars > 0:
                            text = text[:max_chars]
                        if isinstance(max_total_chars, int) and max_total_chars > 0:
                            remaining = max_total_chars - total_chars
                            if remaining <= 0:
                                stop = True
                                break
                            if len(text) > remaining:
                                text = text[:remaining]
                                stop = True
                        results.append(text)
                        total_chars += len(text)
                if keep_images:
                    for img in getattr(page, "images", []) or []:
                        desc = _image_description(img, idx + 1)
                        if desc:
                            results.append(desc)
                if stop:
                    break
    except Exception as exc:
        _log_error(conf, "failed to parse PDF", exc)
        return []
    return results
