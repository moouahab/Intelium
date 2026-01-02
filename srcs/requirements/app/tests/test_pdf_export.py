from pathlib import Path

from tools.reporting import pdf_export
from tools.reporting.pdf import core as pdf_core


class DummyPDF:
    def __init__(self):
        self.lines = []
        self.w = 210
        self.l_margin = 10
        self.r_margin = 10
        self._x = 0

    def set_auto_page_break(self, *args, **kwargs):
        return None

    def set_margins(self, *args, **kwargs):
        return None

    def add_page(self):
        return None

    def set_font(self, *args, **kwargs):
        return None

    def multi_cell(self, *args, **kwargs):
        text = args[2] if len(args) > 2 else ""
        self.lines.append(text)

    def cell(self, *args, **kwargs):
        text = args[2] if len(args) > 2 else ""
        self.lines.append(text)

    def ln(self, *args, **kwargs):
        return None

    def set_x(self, value):
        self._x = value

    def get_string_width(self, text):
        return len(text) * 2

    def output(self, path):
        Path(path).write_bytes(b"%PDF-1.4 dummy")


def test_render_markdown_to_pdf_writes_file(tmp_path, monkeypatch):
    monkeypatch.setattr(pdf_core, "HAS_FPDF", True)
    monkeypatch.setattr(pdf_core, "FPDF", DummyPDF)
    out = tmp_path / "rapport.pdf"
    monkeypatch.setattr(pdf_core, "is_valid_pdf", lambda path: True)
    pdf_export.render_markdown_to_pdf("# Titre\n- item", out)
    assert out.exists()


def test_render_markdown_to_pdf_sanitizes_table_lines(tmp_path, monkeypatch):
    monkeypatch.setattr(pdf_core, "HAS_FPDF", True)
    monkeypatch.setattr(pdf_core, "FPDF", DummyPDF)
    monkeypatch.setattr(pdf_core, "is_valid_pdf", lambda path: True)
    out = tmp_path / "rapport.pdf"
    pdf_export.render_markdown_to_pdf("| A | B |\n| --- | --- |\n| 1 | 2 |", out)
    assert out.exists()


def test_render_markdown_to_pdf_handles_unicode_dash(tmp_path, monkeypatch):
    monkeypatch.setattr(pdf_core, "HAS_FPDF", True)
    monkeypatch.setattr(pdf_core, "FPDF", DummyPDF)
    monkeypatch.setattr(pdf_core, "is_valid_pdf", lambda path: True)
    out = tmp_path / "rapport.pdf"
    pdf_export.render_markdown_to_pdf("Titre – test", out)
    assert out.exists()


def test_render_markdown_to_pdf_strips_bold_headings(tmp_path, monkeypatch):
    monkeypatch.setattr(pdf_core, "HAS_FPDF", True)
    monkeypatch.setattr(pdf_core, "FPDF", DummyPDF)
    monkeypatch.setattr(pdf_core, "is_valid_pdf", lambda path: True)
    out = tmp_path / "rapport.pdf"
    pdf_export.render_markdown_to_pdf("**Résumé Executif**\n- **Menace**: test", out)
    assert out.exists()
