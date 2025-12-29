"""
Smoke test : lance un mini-run de tests critiques pour vérifier l'environnement.
Usage : PYTHONPATH=. python scripts/smoke.py
"""
import subprocess
import sys


def main():
    cmds = [
        ["python", "-m", "pytest", "tests/test_http_client.py", "tests/test_e2e_report.py"],
    ]
    for cmd in cmds:
        print(f"Running: {' '.join(cmd)}")
        proc = subprocess.run(cmd)
        if proc.returncode != 0:
            sys.exit(proc.returncode)
    print("Smoke tests OK")


if __name__ == "__main__":
    main()
