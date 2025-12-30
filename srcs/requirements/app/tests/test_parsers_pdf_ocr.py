import types
from io import BytesIO

from PIL import Image, ImageDraw

from tools.parsers import pdf_parser, ocr_parser


def _png_with_text() -> bytes:
    img = Image.new("RGB", (80, 30), "white")
    draw = ImageDraw.Draw(img)
    draw.text((2, 10), "text", fill="black")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_parse_pdf_extracts_text_and_images(monkeypatch):
    class DummyPage:
        def __init__(self, text):
            self._text = text
            self.images = [{"width": 120, "height": 64}]

        def extract_text(self):
            return self._text

    class DummyPdf:
        def __init__(self, pages):
            self.pages = pages

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    dummy_pdf = DummyPdf([DummyPage("Hello PDF"), DummyPage("Skipped page")])

    def fake_open(*args, **kwargs):
        return dummy_pdf

    monkeypatch.setattr(pdf_parser, "HAS_PDF", True)
    monkeypatch.setattr(pdf_parser, "pdfplumber", types.SimpleNamespace(open=fake_open))

    res = pdf_parser.parse_pdf(
        b"%PDF-1.4",
        {"extract_text": True, "max_pages": 1, "max_chars": 12, "keep_images": True},
    )
    assert any("Hello PDF" in item for item in res)
    assert any("image" in item for item in res)
    assert all("Skipped" not in item for item in res)


def test_parse_pdf_gracefully_handles_missing_library(monkeypatch):
    monkeypatch.setattr(pdf_parser, "HAS_PDF", False)
    assert pdf_parser.parse_pdf(b"%PDF-1.4", {}) == []


def test_parse_image_uses_languages_and_limits(monkeypatch):
    calls = {}

    def fake_ocr(img, lang=None):
        calls["lang"] = lang
        return " OCR result "

    monkeypatch.setattr(ocr_parser, "HAS_OCR", True)
    monkeypatch.setattr(ocr_parser, "pytesseract", types.SimpleNamespace(image_to_string=fake_ocr))

    res = ocr_parser.parse_image(_png_with_text(), {"languages": ["eng", "fra"], "max_chars": 5})
    assert res == ["OCR r"]
    assert calls["lang"] == "eng+fra"


def test_parse_image_handles_missing_binary(monkeypatch):
    class DummyPytesseract:
        class TesseractNotFoundError(Exception):
            pass

        def image_to_string(self, img, lang=None):
            raise self.TesseractNotFoundError("not installed")

    monkeypatch.setattr(ocr_parser, "HAS_OCR", True)
    monkeypatch.setattr(ocr_parser, "pytesseract", DummyPytesseract())
    monkeypatch.setattr(ocr_parser, "TesseractNotFoundError", DummyPytesseract.TesseractNotFoundError)

    res = ocr_parser.parse_image(_png_with_text(), {"errors": "log"})
    assert res == []
