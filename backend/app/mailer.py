import smtplib
from email.message import EmailMessage

from app.config import settings


def send(msg: EmailMessage) -> None:
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        smtp.send_message(msg)


def send_reset_email(to: str, link: str) -> None:
    msg = EmailMessage()
    msg["From"] = "SnakeLog <no-reply@snakelog.local>"
    msg["To"] = to
    msg["Subject"] = "SnakeLog: reset hasła"
    msg.set_content(
        "Cześć!\n\nKtoś poprosił o reset hasła do Twojego konta SnakeLog.\n"
        f"Ustaw nowe hasło tutaj (link działa 30 minut):\n{link}\n\n"
        "Jeśli to nie Ty, zignoruj tę wiadomość. Hasło pozostanie bez zmian.\n\nSnakeLog"
    )
    try:
        send(msg)
    except (smtplib.SMTPException, OSError) as exc:
        print(f"[mailer] BŁĄD wysyłki resetu do {to}: {exc}")