from __future__ import annotations

import logging
from io import BytesIO
from typing import List, Any

logger = logging.getLogger(__name__)

try:
    import pytesseract
    from pytesseract import TesseractNotFoundError  # type: ignore
    from PIL import Image

    HAS_OCR = True
except Exception:
    pytesseract = None  # type: ignore
    Image = None  # type: ignore

    class TesseractNotFoundError(Exception):
        pass

    HAS_OCR = False


def _lang(conf: dict) -> str:
    languages = conf.get("languages")
    if isinstance(languages, str) and languages.strip():
        return languages
    if isinstance(languages, list):
        langs = [l for l in languages if isinstance(l, str) and l.strip()]
        if langs:
            return "+".join(langs)
    return "eng"


def _log_error(conf: dict, message: str, exc: Exception | None = None) -> None:
    mode = str(conf.get("errors", "")).lower()
    if mode in {"log", "warn"}:
        logger.warning("OCR warning: %s%s", message, f" ({exc})" if exc else "")


def parse_image(content: bytes, conf: dict) -> List[str]:
    if not HAS_OCR or not content:
        return []
    if not conf.get("ocr", True):
        return []
    max_chars = conf.get("max_chars")
    try:
        with Image.open(BytesIO(content)) as img:  # type: ignore
            text = pytesseract.image_to_string(img, lang=_lang(conf))  # type: ignore
        text = (text or "").strip()
        if not text:
            return []
        if isinstance(max_chars, int) and max_chars > 0:
            text = text[:max_chars]
        return [text]
    except TesseractNotFoundError as exc:  # type: ignore
        _log_error(conf, "Tesseract introuvable", exc)
    except Exception as exc:
        _log_error(conf, "échec OCR", exc)
    return []
