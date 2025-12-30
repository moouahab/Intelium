"""
Validation dédiée de la configuration chargée (yaml fusionné).
Retourne (errors, warnings) pour une utilisation centralisée/loggable.
"""
from __future__ import annotations

from typing import Tuple, List

from tools.validators import validate_auth, validate_crawler, validate_output


def validate_config(config: dict) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    errors.extend(validate_auth(config.get("authentication", {})))
    errors.extend(validate_crawler(config.get("crawler", {})))
    errors.extend(validate_output(config.get("output", {})))
    return errors, warnings
