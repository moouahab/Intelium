#!/usr/bin/env python3
"""
Résumé santé à partir de data/health.json.
Usage : python scripts/health_summary.py [--file data/health.json] [--prometheus]
"""
from __future__ import annotations

from tools.observability.health_summary import main


if __name__ == "__main__":
    main()
