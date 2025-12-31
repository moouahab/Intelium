import logging
import json
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict


def setup_logger(logging_conf: dict):
    level_str = logging_conf.get("level", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)
    logger = logging.getLogger("cti")
    logger.setLevel(level)
    logger.handlers = []

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    console = logging_conf.get("console", True)
    if console:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    file_path = logging_conf.get("file")
    if file_path:
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            fh = RotatingFileHandler(file_path, maxBytes=1_000_000, backupCount=3)
            fh.setLevel(level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception as exc:
            # Pas de crash si pas de droits disque : fallback console uniquement
            logger.warning("File logger disabled (%s)", exc)
    return logger


def mask_sensitive_headers(headers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retourne une copie des headers avec masquage des valeurs sensibles.
    Masque les clés contenant authorization, token, api-key (insensible à la casse).
    """
    masked = {}
    for k, v in (headers or {}).items():
        if not isinstance(k, str):
            masked[k] = v
            continue
        lower = k.lower()
        if any(key in lower for key in ["authorization", "token", "api-key", "apikey", "x-api-key"]):
            masked[k] = "***"
        else:
            masked[k] = v
    return masked


def log_structured(logger: logging.Logger, level: int, message: str, **fields):
    """
    Log structuré (JSON) pour l'observabilité.
    """
    payload = {"message": message, **fields}
    try:
        logger.log(level, json.dumps(payload, ensure_ascii=False))
    except Exception:
        logger.log(level, f"{message} | {fields}")
