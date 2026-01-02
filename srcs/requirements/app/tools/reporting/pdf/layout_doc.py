from __future__ import annotations

from typing import List, Dict, Any
import datetime as dt

from tools.reporting.pdf import core
from tools.reporting.pdf import styles


DEFAULT_MARGINS = (12, 12, 12)
DEFAULT_PAGE_BREAK_MARGIN = 15
DEFAULT_FONT_FAMILY = "Helvetica"
DEFAULT_FONT_SIZE = 11


def configure_document(pdf: core.FPDF, add_page: bool = False, set_font: bool = False) -> None:
    pdf.set_margins(*DEFAULT_MARGINS)
    pdf.set_auto_page_break(auto=True, margin=DEFAULT_PAGE_BREAK_MARGIN)
    if add_page:
        pdf.add_page()
    if set_font:
        pdf.set_font(DEFAULT_FONT_FAMILY, size=DEFAULT_FONT_SIZE)


def _truncate_to_width(pdf: core.FPDF, text: str, max_width: float) -> str:
    safe_text = core.safe_text(text)
    if pdf.get_string_width(safe_text) <= max_width:
        return safe_text
    ellipsis = "..."
    max_width = max(0.0, max_width - pdf.get_string_width(ellipsis))
    for idx in range(len(safe_text), 0, -1):
        candidate = safe_text[:idx]
        if pdf.get_string_width(candidate) <= max_width:
            return f"{candidate}{ellipsis}"
    return ellipsis


def render_cover(pdf: core.FPDF, title: str, subtitle: str) -> None:
    pdf.add_page()
    pdf.set_fill_color(*styles.COLOR_PRIMARY)
    pdf.rect(0, 0, pdf.w, 28, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(pdf.l_margin, 10)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 8, core.safe_text(title), ln=1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(18)
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 12, core.safe_text("Rapport CTI"), ln=1)
    pdf.set_font("Helvetica", size=12)
    if subtitle:
        pdf.cell(0, 8, core.safe_text(subtitle), ln=1)
    pdf.ln(4)
    date_label = dt.datetime.now().strftime("Genere le %Y-%m-%d %H:%M")
    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(*styles.COLOR_MUTED)
    pdf.cell(0, 6, core.safe_text(date_label), ln=1)
    pdf.set_text_color(0, 0, 0)


def render_toc(pdf: core.FPDF, entries: List[Dict[str, Any]], title: str, with_pages: bool) -> None:
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 8, core.safe_text(title), ln=1)
    pdf.ln(2)
    pdf.set_font("Helvetica", size=11)
    max_width = pdf.w - pdf.l_margin - pdf.r_margin
    for entry in entries:
        level = int(entry.get("level", 2))
        if level > 2:
            continue
        indent = "  " * (level - 1)
        label = f"{indent}{entry.get('text', '')}".strip()
        page_text = str(entry.get("page", "")) if with_pages else ""
        number_width = max(12.0, pdf.get_string_width(page_text) + 2)
        title_width = max(10.0, max_width - number_width)
        title_value = _truncate_to_width(pdf, label, title_width)
        dots_count = max(0, int((title_width - pdf.get_string_width(title_value)) / 2))
        dots = "." * min(dots_count, 60)
        pdf.cell(title_width, 6, core.safe_text(f"{title_value} {dots}"), ln=0)
        pdf.cell(number_width, 6, core.safe_text(page_text), ln=1, align="R")


def build_toc_entries(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    entries = []
    for block in blocks:
        if block.get("type") == "heading":
            entries.append({"text": block.get("text", ""), "level": block.get("level", 2), "page": ""})
    return entries


def assign_toc_page(entries: List[Dict[str, Any]], block: Dict[str, Any], page_no: int) -> None:
    for entry in entries:
        if entry["text"] == block.get("text") and not entry["page"]:
            entry["page"] = page_no
            break


if core.FPDF:
    class CTIPDF(core.FPDF):
        def footer(self):
            self.set_y(-12)
            self.set_font("Helvetica", size=9)
            self.set_text_color(*styles.COLOR_MUTED)
            self.cell(0, 6, f"Page {self.page_no()}/{{nb}}", align="R")
            self.set_text_color(0, 0, 0)
else:  # pragma: no cover - fpdf2 optional
    class CTIPDF:
        pass
