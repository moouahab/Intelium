from typing import Any, List, Callable

from tools.parsers.html_parser import parse_html
from tools.parsers.json_parser import parse_json
from tools.parsers.xml_parser import parse_xml
from tools.parsers.csv_parser import parse_csv
from tools.parsers.pdf_parser import parse_pdf
from tools.parsers.ocr_parser import parse_image
from tools.parsers.txt_parser import parse_txt
from tools.parsers.text_utils import ensure_text


PARSERS: dict[str, Callable[[Any, dict], List[str]]] = {
    "html": parse_html,
    "api": parse_json,
    "xml": parse_xml,
    "csv": parse_csv,
    "pdf": parse_pdf,
    "image": parse_image,
    "txt": parse_txt,
}


def parse_content(source_type: str, content: Any, scraping_conf: dict) -> List[str]:
    type_conf = scraping_conf.get(source_type, {})
    parser_fn = PARSERS.get(source_type)
    if not parser_fn or content is None:
        return []
    # Normalise l'encodage sur les contenus texte standards
    if source_type in {"api", "xml", "csv", "txt"} and isinstance(content, bytes):
        content = ensure_text(content, encoding=type_conf.get("encoding"))
    try:
        return parser_fn(content, type_conf)
    except Exception:
        return []
