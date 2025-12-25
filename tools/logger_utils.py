import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


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
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        fh = RotatingFileHandler(file_path, maxBytes=1_000_000, backupCount=3)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger
