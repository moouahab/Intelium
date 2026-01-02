from pathlib import Path

from tools.reporting.email_report import send_report_email


class DummySMTP:
    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sent = None
        self.starttls_called = False
        self.login_called = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def starttls(self):
        self.starttls_called = True

    def login(self, user, password):
        self.login_called = True

    def send_message(self, msg):
        self.sent = msg


def test_send_report_email_attaches_pdf(tmp_path, monkeypatch):
    report = tmp_path / "rapport.md"
    report.write_text("# Rapport\nContenu")
    pdf = tmp_path / "rapport.pdf"
    pdf.write_bytes(b"%PDF-1.4 dummy")

    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "25")
    monkeypatch.setenv("ALERT_EMAIL_FROM", "from@example.com")
    monkeypatch.setenv("ALERT_EMAIL_TO", "to@example.com")

    dummy = DummySMTP("smtp.example.com", 25)
    monkeypatch.setattr("tools.reporting.email_report.smtplib.SMTP", lambda *args, **kwargs: dummy)

    ok = send_report_email(
        report,
        {"email_report": {"enabled": True, "attach_pdf": True, "pdf_path": str(pdf)}},
        scheduling_conf={},
        run_meta={"run_id": "abc"},
    )
    assert ok is True
    assert dummy.sent is not None
    assert dummy.sent.is_multipart()


def test_send_report_email_uses_summary_source(tmp_path, monkeypatch):
    report = tmp_path / "rapport.md"
    report.write_text("# Rapport\nContenu")
    summary = tmp_path / "summary.md"
    summary.write_text("# Resume\nCourt")

    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "25")
    monkeypatch.setenv("ALERT_EMAIL_FROM", "from@example.com")
    monkeypatch.setenv("ALERT_EMAIL_TO", "to@example.com")

    dummy = DummySMTP("smtp.example.com", 25)
    monkeypatch.setattr("tools.reporting.email_report.smtplib.SMTP", lambda *args, **kwargs: dummy)
    monkeypatch.setattr("tools.reporting.email_report.HAS_FPDF", True)

    def fake_render(text, path, title=None, **kwargs):
        path.write_bytes(b"%PDF-1.4\n%%EOF")
        return path

    monkeypatch.setattr("tools.reporting.email_report.render_report_pdf", fake_render)

    ok = send_report_email(
        report,
        {
            "email_report": {"enabled": True, "attach_pdf": True, "pdf_source": "summary"},
            "exports": {"executive_summary": str(summary)},
        },
        scheduling_conf={},
        run_meta={"run_id": "abc"},
    )
    assert ok is True
    assert (tmp_path / "summary.pdf").exists()


def test_send_report_email_regenerates_invalid_pdf(tmp_path, monkeypatch):
    report = tmp_path / "rapport.md"
    report.write_text("# Rapport\nContenu")
    bad_pdf = tmp_path / "rapport.pdf"
    bad_pdf.write_bytes(b"corrupt")

    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "25")
    monkeypatch.setenv("ALERT_EMAIL_FROM", "from@example.com")
    monkeypatch.setenv("ALERT_EMAIL_TO", "to@example.com")

    dummy = DummySMTP("smtp.example.com", 25)
    monkeypatch.setattr("tools.reporting.email_report.smtplib.SMTP", lambda *args, **kwargs: dummy)
    monkeypatch.setattr("tools.reporting.email_report.HAS_FPDF", True)
    monkeypatch.setattr("tools.reporting.email_report.is_valid_pdf", lambda path: False)

    def fake_render(text, path, title=None, **kwargs):
        path.write_bytes(b"%PDF-1.4\n%%EOF")
        return path

    monkeypatch.setattr("tools.reporting.email_report.render_report_pdf", fake_render)

    ok = send_report_email(
        report,
        {"email_report": {"enabled": True, "attach_pdf": True, "pdf_path": str(bad_pdf)}},
        scheduling_conf={},
        run_meta={"run_id": "abc"},
    )
    assert ok is True
    assert bad_pdf.read_bytes().startswith(b"%PDF")


def test_send_report_email_forces_pdf_regenerate(tmp_path, monkeypatch):
    report = tmp_path / "rapport.md"
    report.write_text("# Rapport\nContenu")
    pdf = tmp_path / "rapport.pdf"
    original = b"%PDF-1.4\nOLD\n%%EOF"
    pdf.write_bytes(original)

    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "25")
    monkeypatch.setenv("ALERT_EMAIL_FROM", "from@example.com")
    monkeypatch.setenv("ALERT_EMAIL_TO", "to@example.com")

    dummy = DummySMTP("smtp.example.com", 25)
    monkeypatch.setattr("tools.reporting.email_report.smtplib.SMTP", lambda *args, **kwargs: dummy)
    monkeypatch.setattr("tools.reporting.email_report.HAS_FPDF", True)

    def fake_render(text, path, title=None, **kwargs):
        path.write_bytes(b"%PDF-1.4\nNEW\n%%EOF")
        return path

    monkeypatch.setattr("tools.reporting.email_report.render_report_pdf", fake_render)

    ok = send_report_email(
        report,
        {"email_report": {"enabled": True, "attach_pdf": True, "pdf_path": str(pdf), "pdf_regenerate": True}},
        scheduling_conf={},
        run_meta={"run_id": "abc"},
    )
    assert ok is True
    assert pdf.read_bytes() != original
