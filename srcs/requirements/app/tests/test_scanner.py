from pathlib import Path
from tools.providers.http.scanner import run_scan


def test_run_scan_success(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("ok")
    err = run_scan(f, "echo ok {file}")
    assert err is None


def test_run_scan_failure(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("ok")
    # commande qui échoue
    err = run_scan(f, "sh -c 'exit 1'")
    assert err
