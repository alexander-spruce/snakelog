import smtplib
from datetime import date, timedelta
from email.message import EmailMessage

from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.models import Reminder, Snake, User

LABELS = {
    "feeding": "karmienie",
    "weighing": "ważenie",
    "cleaning": "czyszczenie terrarium",
}


def build_message(to: str, snake_name: str, reminder_type: str, due: date) -> EmailMessage:
    label = LABELS.get(reminder_type, reminder_type)
    msg = EmailMessage()
    msg["From"] = "SnakeLog <no-reply@snakelog.local>"
    msg["To"] = to
    msg["Subject"] = f"SnakeLog: {label} ({snake_name})"
    msg.set_content(
        f"Cześć!\n\nPrzypomnienie: {label} dla węża {snake_name}, termin {due:%d.%m.%Y}.\n\n"
        "Pamiętaj o zapisaniu wpisu w dzienniku opieki.\n\nSnakeLog"
    )
    return msg


def run_once(today: date | None = None) -> int:
    today = today or date.today()
    sent = 0
    with SessionLocal() as db:
        rows = db.execute(
            select(Reminder, Snake, User)
            .join(Snake, Reminder.snake_id == Snake.id)
            .join(User, Snake.user_id == User.id)
            .where(
                Reminder.status == "active",
                Reminder.next_due <= today + timedelta(days=1),  # dziś, jutro lub zaległe
                User.is_blocked.is_(False),
            )
        ).all()

        for reminder, snake, user in rows:
            msg = build_message(user.email, snake.name, reminder.type, reminder.next_due)
            try:
                with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                    smtp.send_message(msg)
            except (smtplib.SMTPException, OSError) as exc:
                print(f"[worker] BŁĄD wysyłki do {user.email}: {exc}")
                continue  # termin zostaje, spróbujemy następnego dnia

            reminder.next_due += timedelta(days=reminder.interval_days)
            while reminder.next_due <= today:
                reminder.next_due += timedelta(days=reminder.interval_days)
            db.commit()
            sent += 1
            print(f"[worker] wysłano: {reminder.type} / {snake.name} -> {user.email}")
    print(f"[worker] gotowe, wysłano {sent}")
    return sent


if __name__ == "__main__":
    run_once()