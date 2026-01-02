from __future__ import annotations

from typing import List, Dict, Any, Optional, Callable

from tools.reporting.pdf import core
from tools.reporting.pdf import styles
from tools.reporting.pdf import table as table_renderer
from tools.reporting.pdf.layout_inline import render_line


def render_heading(pdf: core.FPDF, text: str, level: int) -> None:
    size = 16 if level <= 1 else 13 if level == 2 else 12
    pdf.set_font("Helvetica", "B", size)
    pdf.set_text_color(*styles.COLOR_PRIMARY)
    core.write_wrapped(pdf, text, 6 if level <= 2 else 5)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", size=11)
    pdf.ln(1)


def render_paragraph(pdf: core.FPDF, text: str) -> None:
    core.write_wrapped(pdf, text, 5)
    pdf.ln(2)


def render_list(pdf: core.FPDF, items: List[str]) -> None:
    for item in items:
        core.write_wrapped(pdf, f"- {item}", 5)
        pdf.ln(1)
    pdf.ln(1)


def render_blocks(
    pdf: core.FPDF,
    blocks: List[Dict[str, Any]],
    on_heading: Optional[Callable[[Dict[str, Any]], None]] = None,
    page_break_level: Optional[int] = None,
    page_break_on_first: bool = False,
) -> None:
    first_section = True
    for block in blocks:
        btype = block.get("type")
        if btype == "heading":
            level = int(block.get("level", 2))
            if page_break_level is not None and level <= page_break_level:
                if first_section:
                    if page_break_on_first:
                        pdf.add_page()
                    first_section = False
                else:
                    pdf.add_page()
            if on_heading:
                on_heading(block)
            render_heading(pdf, block.get("text", ""), level)
        elif btype == "paragraph":
            render_paragraph(pdf, block.get("text", ""))
        elif btype == "list":
            render_list(pdf, block.get("items", []))
        elif btype == "table":
            table_renderer.render_table(pdf, block.get("header", []), block.get("rows", []))

