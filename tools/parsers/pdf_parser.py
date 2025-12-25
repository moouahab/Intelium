from typing import List
try:
    import pdfplumber
    HAS_PDF = True
except ImportError:
    HAS_PDF = False


def parse_pdf(content: bytes, conf: dict) -> List[str]:
    if not HAS_PDF:
        return []
    results: List[str] = []
    try:
        with pdfplumber.open(bytes_content=content) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    results.append(text)
    except Exception:
        return []
    return results
