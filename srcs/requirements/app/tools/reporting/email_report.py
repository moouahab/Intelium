from __future__ import annotations
import datetime as dt
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Dict, List, Optional
from tools.config.config_utils import to_bool, to_int
from tools.secrets import get_secret
from tools.reporting.pdf_export import HAS_FPDF, render_report_pdf, is_valid_pdf


def _normalize_recipients(value: Any) -> List[str]:
    if not value:
        return []
    if isinstance(value, str):
        parts = [item.strip() for item in value.replace(";", ",").split(",")]
        return [item for item in parts if item]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _format_template(template: str, context: Dict[str, Any]) -> str:
    try:
        return template.format(**context)
    except Exception:
        return template


def _resolve_pdf_source(report_path: Path, output_conf: dict, email_conf: dict) -> Path:
    explicit = email_conf.get("pdf_source_path")
    if explicit:
        return Path(explicit)
    source = (email_conf.get("pdf_source") or "report").lower()
    if source == "summary":
        exports = output_conf.get("exports") or {}
        summary_path = exports.get("executive_summary")
        return Path(summary_path) if summary_path else report_path.parent / "summary.md"
    return report_path


def _build_email_config(
    output_conf: dict,
    scheduling_conf: Optional[dict] = None,
    run_meta: Optional[dict] = None,
) -> Optional[Dict[str, Any]]:
    email_conf = (output_conf.get("email_report") or {}) if isinstance(output_conf, dict) else {}
    if not to_bool(email_conf.get("enabled", False), default=False):
        return None
    scheduling_conf = scheduling_conf or {}
    recipients = _normalize_recipients(email_conf.get("to") or scheduling_conf.get("notification_email"))
    if not recipients:
        recipients = _normalize_recipients(get_secret("ALERT_EMAIL_TO"))
    sender = email_conf.get("from") or get_secret("ALERT_EMAIL_FROM") or ""
    if not sender or not recipients:
        return None
    now = dt.datetime.now()
    context = {
        "date": now.strftime("%Y-%m-%d"),
        "datetime": now.strftime("%Y-%m-%d %H:%M"),
        "run_id": (run_meta or {}).get("run_id", ""),
    }
    subject = _format_template(email_conf.get("subject", "[CTI] Rapport quotidien {date}"), context)
    body = _format_template(
        email_conf.get("body", "Bonjour,\n\nVeuillez trouver le rapport CTI en piece jointe.\n"),
        context,
    )
    return {
        "recipients": recipients,
        "sender": sender,
        "subject": subject,
        "body": body,
        "attach_pdf": to_bool(email_conf.get("attach_pdf", True), default=True),
        "pdf_path": Path(email_conf.get("pdf_path", "")) if email_conf.get("pdf_path") else None,
        "pdf_source": email_conf.get("pdf_source"),
        "pdf_source_path": email_conf.get("pdf_source_path"),
        "pdf_style": email_conf.get("pdf_style") or "basic",
        "pdf_regenerate": to_bool(email_conf.get("pdf_regenerate", False), default=False),
        "smtp_host": get_secret("SMTP_HOST") or "",
        "smtp_port": to_int(get_secret("SMTP_PORT"), default=25) or 25,
        "smtp_user": get_secret("SMTP_USER") or "",
        "smtp_pass": get_secret("SMTP_PASS") or "",
        "smtp_ssl": to_bool(email_conf.get("smtp_ssl", False), default=False),
        "smtp_starttls": to_bool(email_conf.get("smtp_starttls", True), default=True),
        "smtp_timeout": to_int(email_conf.get("smtp_timeout"), default=30) or 30,
    }


def _ensure_pdf(
    source_path: Path,
    pdf_path: Path,
    logger=None,
    force_regen: bool = False,
    style: str = "basic",
) -> Optional[Path]:
    if pdf_path.exists():
        if force_regen:
            if logger:
                logger.info("Email rapport: regeneration PDF forcee.")
            try:
                pdf_path.unlink()
            except Exception:
                pass
        elif is_valid_pdf(pdf_path):
            return pdf_path
        else:
            if logger:
                logger.warning("Email rapport: PDF existant invalide, regeneration.")
            try:
                pdf_path.unlink()
            except Exception:
                pass
    if not source_path.exists():
        return None
    if not HAS_FPDF:
        return None
    try:
        text = source_path.read_text()
        return render_report_pdf(text, pdf_path, title="Rapport CTI", style=style)
    except Exception as exc:
        if logger:
            logger.warning("Email rapport: echec generation PDF (%s).", exc)
        return None


def send_report_email(
    report_path: Path,
    output_conf: dict,
    scheduling_conf: Optional[dict] = None,
    run_meta: Optional[dict] = None,
    logger=None,
) -> bool:
    cfg = _build_email_config(output_conf, scheduling_conf=scheduling_conf, run_meta=run_meta)
    if not cfg:
        return False
    if not cfg["smtp_host"] or not cfg["smtp_port"]:
        if logger:
            logger.warning("Email rapport: SMTP_HOST/SMTP_PORT manquants.")
        return False
    msg = EmailMessage()
    msg["Subject"] = cfg["subject"]
    msg["From"] = cfg["sender"]
    msg["To"] = ", ".join(cfg["recipients"])
    msg.set_content(cfg["body"])

    if cfg["attach_pdf"]:
        source_path = _resolve_pdf_source(report_path, output_conf, cfg)
        requested_path = cfg["pdf_path"] or source_path.with_suffix(".pdf")
        pdf_path = _ensure_pdf(
            source_path,
            requested_path,
            logger=logger,
            force_regen=cfg.get("pdf_regenerate", False),
            style=cfg.get("pdf_style", "basic"),
        )
        if pdf_path and pdf_path.exists():
            msg.add_attachment(
                pdf_path.read_bytes(),
                maintype="application",
                subtype="pdf",
                filename=pdf_path.name,
            )
        elif logger:
            logger.warning(
                "Email rapport: PDF indisponible (source=%s, chemin=%s).",
                source_path,
                requested_path,
            )

    smtp_port = int(cfg["smtp_port"])
    use_ssl = cfg["smtp_ssl"] or smtp_port == 465
    smtp_class = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
    with smtp_class(cfg["smtp_host"], smtp_port, timeout=cfg["smtp_timeout"]) as server:
        if not use_ssl and cfg["smtp_starttls"]:
            server.starttls()
        if cfg["smtp_user"] and cfg["smtp_pass"]:
            server.login(cfg["smtp_user"], cfg["smtp_pass"])
        server.send_message(msg)
    if logger:
        logger.info("Email rapport: envoi OK (%s)", ", ".join(cfg["recipients"]))
    return True
