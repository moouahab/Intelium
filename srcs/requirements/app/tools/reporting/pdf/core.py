from __future__ import annotations

from pathlib import Path
from typing import Iterable

try:
    from fpdf import FPDF
    HAS_FPDF = True
except Exception:  # pragma: no cover - optional dependency
    FPDF = None
    HAS_FPDF = False


MAX_WORD_LEN = 80
MIN_PDF_BYTES = 256
CHAR_REPLACEMENTS = {
    ord("–"): "-",
    ord("—"): "-",
    ord("−"): "-",
    ord("•"): "-",
    ord("…"): "...",
    ord("“"): '"',
    ord("”"): '"',
    ord("’"): "'",
    ord("‘"): "'",
    ord("\u00a0"): " ",
    ord("\u202f"): " ",
    ord("\u2009"): " ",
    ord("\u00b7"): "*",
}


def safe_text(text: str) -> str:
    text = text.translate(CHAR_REPLACEMENTS)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def iter_lines(text: str | Iterable[str]) -> Iterable[str]:
    if isinstance(text, str):
        return text.splitlines()
    return text


def wrap_long_words(text: str, max_len: int = MAX_WORD_LEN) -> str:
    if not text:
        return text
    parts = text.split(" ")
    wrapped = []
    for part in parts:
        if len(part) <= max_len:
            wrapped.append(part)
            continue
        chunks = [part[i : i + max_len] for i in range(0, len(part), max_len)]
        wrapped.append(" ".join(chunks))
    return " ".join(wrapped)


def wrap_to_width(pdf: FPDF, text: str, max_width: float) -> list[str]:
    words = text.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if pdf.get_string_width(candidate) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
        if pdf.get_string_width(word) <= max_width:
            current = word
            continue
        chunk = ""
        for ch in word:
            cand = f"{chunk}{ch}"
            if pdf.get_string_width(cand) <= max_width:
                chunk = cand
            else:
                if chunk:
                    lines.append(chunk)
                chunk = ch
        current = chunk
    if current:
        lines.append(current)
    return lines


def write_wrapped(pdf: FPDF, text: str, line_height: int) -> None:
    max_width = pdf.w - pdf.l_margin - pdf.r_margin
    if max_width <= 1:
        pdf.set_x(pdf.l_margin)
        max_width = pdf.w - pdf.l_margin - pdf.r_margin
    safe = safe_text(text)
    for line in wrap_to_width(pdf, safe, max_width):
        pdf.set_x(pdf.l_margin)
        pdf.cell(0, line_height, line)
        pdf.ln(line_height)


def is_valid_pdf(path: Path) -> bool:
    try:
        data = path.read_bytes()
    except Exception:
        return False
    if len(data) < MIN_PDF_BYTES:
        return False
    if not data.startswith(b"%PDF"):
        return False
    tail = data[-2048:] if len(data) > 2048 else data
    return b"%%EOF" in tail
