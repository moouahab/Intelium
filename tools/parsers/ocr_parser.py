from typing import List
try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False


def parse_image(content: bytes, conf: dict) -> List[str]:
    if not HAS_OCR:
        return []
    try:
        from io import BytesIO
        img = Image.open(BytesIO(content))
        text = pytesseract.image_to_string(img)
        return [text] if text else []
    except Exception:
        return []
