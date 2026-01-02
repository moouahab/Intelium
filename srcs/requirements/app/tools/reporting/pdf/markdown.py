from __future__ import annotations

from typing import Iterable, List, Dict, Any, Optional
import re


def strip_markdown_inline(text: str) -> str:
    if not text:
        return text
    heading_match = re.match(r"^\s*\*\*(.+?)\*\*\s*$", text)
    if heading_match:
        return f"## {heading_match.group(1).strip()}"
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text


def normalize_markdown_lines(lines: Iterable[str]) -> Iterable[str]:
    table_sep = re.compile(r"^[\s|:-]+$")
    for line in lines:
        raw = line.rstrip()
        if raw.strip().startswith("```"):
            continue
        if raw.strip().startswith("---"):
            continue
        if "|" in raw:
            stripped = raw.strip()
            if table_sep.match(stripped):
                continue
            if stripped.startswith("|") or stripped.endswith("|"):
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                cleaned = []
                for cell in cells:
                    cell = strip_markdown_inline(cell)
                    if cell:
                        cleaned.append(cell)
                if cleaned:
                    yield "- " + "; ".join(cleaned)
                    continue
        yield strip_markdown_inline(raw)


def is_table_separator(line: str) -> bool:
    return bool(re.match(r"^\s*\|?[\s:-]+\|?\s*$", line))


def parse_table_row(line: str) -> List[str]:
    stripped = line.strip().strip("|")
    return [strip_markdown_inline(cell.strip()) for cell in stripped.split("|")]


def is_list_item(line: str) -> bool:
    stripped = line.lstrip()
    return stripped.startswith("- ") or stripped.startswith("* ")


def split_semicolon_row(text: str) -> List[str]:
    return [part.strip() for part in text.split(";")]


def semicolon_table_rows(items: List[str]) -> Optional[List[List[str]]]:
    rows = [split_semicolon_row(item) for item in items]
    counts = {len(row) for row in rows if row}
    if len(counts) != 1:
        return None
    cols = counts.pop() if counts else 0
    if cols < 3:
        return None
    return rows


def parse_markdown_blocks(lines: Iterable[str]) -> List[Dict[str, Any]]:
    blocks: List[Dict[str, Any]] = []
    raw_lines = list(lines)
    in_code = False
    i = 0
    while i < len(raw_lines):
        raw = raw_lines[i].rstrip()
        if raw.strip().startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            i += 1
            continue
        if not raw.strip():
            i += 1
            continue
        line = strip_markdown_inline(raw).strip()
        if not line:
            i += 1
            continue
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            text = line[level:].strip()
            if text:
                blocks.append({"type": "heading", "level": level, "text": text})
            i += 1
            continue
        if "|" in raw and not is_list_item(raw) and i + 1 < len(raw_lines):
            if is_table_separator(raw_lines[i + 1]):
                header = parse_table_row(raw)
                i += 2
                rows: List[List[str]] = []
                while i < len(raw_lines):
                    row_line = raw_lines[i].rstrip()
                    if not row_line.strip():
                        break
                    if is_table_separator(row_line):
                        i += 1
                        continue
                    if "|" not in row_line:
                        break
                    rows.append(parse_table_row(row_line))
                    i += 1
                if header:
                    blocks.append({"type": "table", "header": header, "rows": rows})
                continue
            if "|" in raw_lines[i + 1]:
                header = parse_table_row(raw)
                if len(header) >= 2:
                    i += 1
                    rows = []
                    while i < len(raw_lines):
                        row_line = raw_lines[i].rstrip()
                        if not row_line.strip():
                            break
                        if "|" not in row_line:
                            break
                        rows.append(parse_table_row(row_line))
                        i += 1
                    blocks.append({"type": "table", "header": header, "rows": rows})
                    continue
        if is_list_item(raw):
            items: List[str] = []
            while i < len(raw_lines) and is_list_item(raw_lines[i]):
                item = raw_lines[i].lstrip()[2:].strip()
                item = strip_markdown_inline(item)
                if item:
                    items.append(item)
                i += 1
            if items:
                table_rows = semicolon_table_rows(items)
                if table_rows:
                    header = table_rows[0]
                    rows = table_rows[1:]
                    blocks.append({"type": "table", "header": header, "rows": rows})
                else:
                    blocks.append({"type": "list", "items": items})
            continue
        paragraph: List[str] = [line]
        i += 1
        while i < len(raw_lines):
            peek = raw_lines[i].rstrip()
            if not peek.strip():
                i += 1
                break
            if peek.strip().startswith("```"):
                break
            if is_list_item(peek) or peek.strip().startswith("#"):
                break
            if "|" in peek and i + 1 < len(raw_lines) and is_table_separator(raw_lines[i + 1]):
                break
            paragraph.append(strip_markdown_inline(peek.strip()))
            i += 1
        blocks.append({"type": "paragraph", "text": " ".join(paragraph).strip()})
    return blocks
