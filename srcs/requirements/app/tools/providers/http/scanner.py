"""
Scan basique de fichiers téléchargés via une commande externe (AV/YARA, etc.).
La commande peut inclure le placeholder {file} qui sera remplacé par le chemin du fichier.
"""
from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Optional


def run_scan(file_path: Path, command: str, timeout: int = 60, scanner: Optional[str] = None) -> Optional[str]:
    if not command:
        return None
    try:
        cmd_list = [arg.replace("{file}", str(file_path)) for arg in shlex.split(command)]
        if not cmd_list:
            return "Commande de scan vide"
        proc = subprocess.run(cmd_list, capture_output=True, text=True, timeout=timeout)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        return f"Scanner indisponible ou en échec: {exc}"
    if proc.returncode != 0:
        return proc.stderr.strip() or f"Scan failed (rc={proc.returncode})"
    if (scanner == "yara" or Path(cmd_list[0]).name in {"yara", "yara.exe"}) and proc.stdout.strip():
        return "Détection YARA : fichier rejeté"
    return None
