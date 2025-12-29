"""
Scan basique de fichiers téléchargés via une commande externe (AV/YARA, etc.).
La commande peut inclure le placeholder {file} qui sera remplacé par le chemin du fichier.
"""
from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Optional


def run_scan(file_path: Path, command: str, timeout: int = 60) -> Optional[str]:
    if not command:
        return None
    file_str = str(file_path)
    cmd_str = command.replace("{file}", file_str)
    cmd_list = shlex.split(cmd_str)
    proc = subprocess.run(cmd_list, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        return proc.stderr.strip() or f"Scan failed (rc={proc.returncode})"
    return None
