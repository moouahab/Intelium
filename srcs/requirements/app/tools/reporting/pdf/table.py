from __future__ import annotations

from typing import List, Optional
import re
import unicodedata

from tools.reporting.pdf import core
from tools.reporting.pdf import markdown
from tools.reporting.pdf import styles


def _normalize_header_cell(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    stripped = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", stripped.lower()).strip()


def _table_weights(header: List[str]) -> Optional[List[float]]:
    if not header:
        return None
    normalized = [_normalize_header_cell(cell) for cell in header]
    joined = " ".join(normalized)
    col_count = len(header)
    if col_count == 6 and "priorite" in joined and "menace" in joined and "impact" in joined:
        return [0.07, 0.18, 0.22, 0.20, 0.23, 0.10]
    if col_count == 6 and "cve" in joined and "produit" in joined and "criticite" in joined:
        return [0.12, 0.20, 0.12, 0.18, 0.18, 0.20]
    if col_count == 4 and "type" in joined and "valeur" in joined and "contexte" in joined:
        return [0.12, 0.28, 0.40, 0.20]
    if col_count == 3 and "technique" in joined and "description" in joined:
        return [0.28, 0.36, 0.36]
    if col_count == 3 and "categorie" in joined and "impact" in joined:
        return [0.22, 0.38, 0.40]
    return None


def _normalize_row_cells(cells: List[str], col_count: int) -> List[str]:
    if col_count <= 0:
        return []
    if len(cells) > col_count:
        merged = " / ".join(cell for cell in cells[col_count - 1 :] if cell)
        return cells[: col_count - 1] + [merged]
    if len(cells) < col_count:
        return cells + [""] * (col_count - len(cells))
    return cells


def _calc_table_widths(pdf: core.FPDF, header: List[str], rows: List[List[str]]) -> List[float]:
    col_count = len(header) if header else max((len(r) for r in rows), default=0)
    if col_count == 0:
        return []
    max_width = pdf.w - pdf.l_margin - pdf.r_margin
    weights = _table_weights(header) if header else None
    if weights and len(weights) == col_count:
        widths = [max_width * weight for weight in weights]
        min_width = max(16.0, max_width / max(col_count * 2, 2))
        widths = [max(min_width, w) for w in widths]
        total = sum(widths)
        if total > max_width:
            scale = max_width / total
            widths = [w * scale for w in widths]
        return widths
    widths = [0.0 for _ in range(col_count)]
    normalized_header = _normalize_row_cells(header, col_count)
    for idx in range(col_count):
        cell = normalized_header[idx]
        widths[idx] = max(widths[idx], pdf.get_string_width(core.safe_text(cell)) + 4)
    for row in rows:
        normalized_row = _normalize_row_cells(row, col_count)
        for idx in range(col_count):
            cell = normalized_row[idx]
            widths[idx] = max(widths[idx], pdf.get_string_width(core.safe_text(cell)) + 4)
    total = sum(widths)
    if total <= 0:
        return [max_width / col_count for _ in range(col_count)]
    if total > max_width:
        scale = max_width / total
        widths = [w * scale for w in widths]
    min_width = max(18.0, max_width / max(col_count * 2, 2))
    widths = [max(min_width, w) for w in widths]
    total = sum(widths)
    if total > max_width and col_count:
        overflow = total - max_width
        widths[-1] = max(min_width, widths[-1] - overflow)
    return widths


def render_table(pdf: core.FPDF, header: List[str], rows: List[List[str]]) -> None:
    if not header and not rows:
        return
    widths = _calc_table_widths(pdf, header, rows)
    if not widths:
        return
    col_count = len(widths)
    line_height = 5
    padding = 1.5

    def render_row(cells: List[str], fill: bool, bold: bool = False) -> None:
        row_cells = _normalize_row_cells(cells, col_count)
        wrapped_rows: List[List[str]] = []
        max_lines = 1
        for idx, cell in enumerate(row_cells):
            cleaned = core.safe_text(markdown.strip_markdown_inline(str(cell)))
            content_width = max(1.0, widths[idx] - 2 * padding)
            lines = core.wrap_to_width(pdf, cleaned, content_width) or [""]
            wrapped_rows.append(lines)
            max_lines = max(max_lines, len(lines))
        row_height = max_lines * line_height + 2 * padding
        if pdf.get_y() + row_height > pdf.page_break_trigger:
            pdf.add_page()
            if header and cells is not header:
                render_row(header, fill=True, bold=True)
        x = pdf.l_margin
        y = pdf.get_y()
        font_size = 9
        if col_count >= 6:
            font_size = 8
        pdf.set_font("Helvetica", "B" if bold else "", size=10 if bold else font_size)
        for idx, lines in enumerate(wrapped_rows):
            w = widths[idx]
            if fill:
                pdf.set_fill_color(*(styles.COLOR_TABLE_HEADER if bold else styles.COLOR_TABLE_ALT))
                pdf.rect(x, y, w, row_height, "F")
            pdf.rect(x, y, w, row_height)
            text_y = y + padding
            for line in lines:
                pdf.set_xy(x + padding, text_y)
                pdf.cell(w - 2 * padding, line_height, line)
                text_y += line_height
            x += w
        pdf.set_y(y + row_height)
        pdf.set_font("Helvetica", size=11)

    pdf.ln(1)
    render_row(header, fill=True, bold=True)
    for idx, row in enumerate(rows):
        render_row(row, fill=(idx % 2 == 0), bold=False)
    pdf.ln(2)
