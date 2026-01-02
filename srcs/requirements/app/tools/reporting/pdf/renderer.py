from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from tools.reporting.pdf import core
from tools.reporting.pdf import markdown
from tools.reporting.pdf import layout


def _init_pdf(pdf_cls, add_page: bool = False, set_font: bool = False, with_alias: bool = False):
    pdf = pdf_cls()
    if with_alias and hasattr(pdf, "alias_nb_pages"):
        pdf.alias_nb_pages()
    layout.configure_document(pdf, add_page=add_page, set_font=set_font)
    return pdf


def _render_enterprise_pass(
    pdf,
    blocks,
    toc_entries,
    title: str,
    with_pages: bool,
    record_pages: bool,
) -> None:
    layout.render_cover(pdf, title, "")
    layout.render_toc(pdf, toc_entries, "Sommaire", with_pages=with_pages)
    on_heading = None
    if record_pages:
        def on_heading(block):
            layout.assign_toc_page(toc_entries, block, pdf.page_no())
    layout.render_blocks(
        pdf,
        blocks,
        on_heading=on_heading,
        page_break_level=2,
        page_break_on_first=True,
    )


def render_markdown_to_pdf(text: str | Iterable[str], output_path: Path, title: Optional[str] = None) -> Path:
    if not core.HAS_FPDF:
        raise RuntimeError("fpdf2 non disponible (installez la dependance fpdf2).")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = _init_pdf(core.FPDF, add_page=True, set_font=True)
    if title:
        pdf.set_font("Helvetica", "B", 14)
        pdf.multi_cell(0, 8, core.safe_text(title))
        pdf.ln(2)
        pdf.set_font("Helvetica", size=11)
    lines = markdown.normalize_markdown_lines(core.iter_lines(text))
    for line in lines:
        layout.render_line(pdf, line)
    pdf.output(str(output_path))
    if not core.is_valid_pdf(output_path):
        raise RuntimeError("PDF invalide (header/EOF manquant ou taille trop petite).")
    return output_path


def render_enterprise_pdf(text: str | Iterable[str], output_path: Path, title: Optional[str] = None) -> Path:
    if not core.HAS_FPDF:
        raise RuntimeError("fpdf2 non disponible (installez la dependance fpdf2).")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    blocks = markdown.parse_markdown_blocks(core.iter_lines(text))
    toc_entries = layout.build_toc_entries(blocks)
    report_title = title or "Rapport CTI"

    pdf = _init_pdf(layout.CTIPDF, with_alias=True)
    _render_enterprise_pass(pdf, blocks, toc_entries, report_title, with_pages=False, record_pages=True)

    pdf = _init_pdf(layout.CTIPDF, with_alias=True)
    _render_enterprise_pass(pdf, blocks, toc_entries, report_title, with_pages=True, record_pages=False)
    pdf.output(str(output_path))
    if not core.is_valid_pdf(output_path):
        raise RuntimeError("PDF invalide (header/EOF manquant ou taille trop petite).")
    return output_path


def render_report_pdf(
    text: str | Iterable[str],
    output_path: Path,
    title: Optional[str] = None,
    style: str = "basic",
) -> Path:
    style = (style or "basic").lower()
    if style == "enterprise":
        return render_enterprise_pdf(text, output_path, title=title)
    return render_markdown_to_pdf(text, output_path, title=title)
