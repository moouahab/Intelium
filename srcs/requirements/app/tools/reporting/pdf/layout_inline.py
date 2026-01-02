from __future__ import annotations

import re

from tools.reporting.pdf import core


def render_line(pdf: core.FPDF, line: str) -> None:
    raw = line.rstrip()
    if not raw.strip():
        pdf.ln(4)
        return
    stripped = raw.lstrip()
    stripped = core.wrap_long_words(stripped)
    stripped = re.sub(r"[ \t]{2,}", " ", stripped)
    if stripped.startswith("#"):
        level = len(stripped) - len(stripped.lstrip("#"))
        title = stripped[level:].strip()
        size = 14 if level == 1 else 12 if level == 2 else 11
        pdf.set_font("Helvetica", "B", size)
        core.write_wrapped(pdf, title, 6)
        pdf.set_font("Helvetica", size=11)
        return
    prefix_len = len(raw) - len(raw.lstrip())
    prefix = " " * min(prefix_len, 4)
    core.write_wrapped(pdf, f"{prefix}{stripped}", 5)
