import smtplib
from datetime import date, timedelta
from email.message import EmailMessage

from sqlalchemy import select

from app.alert_service import generate_alerts
from app.config import settings
from app.database import SessionLocal
from app.models import Reminder, Snake, User

from app.mailer import send

LABELS = {
    "feeding": "karmienie",
    "weighing": "ważenie",
    "cleaning": "czyszczenie terrarium",
}
ALERT_LABELS = {
    "weight_drop": "spadek wagi",
    "no_growth_young": "brak wzrostu u młodego węża",
    "feeding_refusal": "długa odmowa jedzenia",
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


def build_alert_message(to: str, snake_name: str, alert_type: str, text: str) -> EmailMessage:
    label = ALERT_LABELS.get(alert_type, alert_type)
    msg = EmailMessage()
    msg["From"] = "SnakeLog <no-reply@snakelog.local>"
    msg["To"] = to
    msg["Subject"] = f"SnakeLog: alert zdrowotny, {label} ({snake_name})"
    msg.set_content(
        f"Cześć!\n\nAlert dla węża {snake_name}: {label}.\n\n{text}\n\n"
        "Szczegóły znajdziesz w zakładce Alerty w aplikacji.\n\nSnakeLog"
    )
    return msg


def run_once(today: date | None = None) -> int:
    """Przypomnienia (P5)."""
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
                send(msg)
            except (smtplib.SMTPException, OSError) as exc:
                print(f"[worker] BŁĄD wysyłki do {user.email}: {exc}")
                continue  # termin zostaje, spróbujemy następnego dnia

            reminder.next_due += timedelta(days=reminder.interval_days)
            while reminder.next_due <= today:
                reminder.next_due += timedelta(days=reminder.interval_days)
            db.commit()
            sent += 1
            print(f"[worker] wysłano: {reminder.type} / {snake.name} -> {user.email}")
    print(f"[worker] przypomnienia gotowe, wysłano {sent}")
    return sent


def run_alerts(today: date | None = None) -> int:
    """Alerty zdrowotne (P4): analiza, zapis i powiadomienie e-mailem."""
    with SessionLocal() as db:
        created = generate_alerts(db, today)
    for text, email, snake_name, alert_type in created:
        try:
            send(build_alert_message(email, snake_name, alert_type, text))
            print(f"[worker] alert {alert_type} / {snake_name} -> {email}")
        except (smtplib.SMTPException, OSError) as exc:
            print(f"[worker] BŁĄD wysyłki alertu do {email}: {exc}")  # alert i tak jest w aplikacji
    print(f"[worker] alerty gotowe, utworzono {len(created)}")
    return len(created)


def run_daily() -> None:
    for job in (run_alerts, run_once):
        try:
            job()
        except Exception as exc:  # błąd jednego zadania nie blokuje drugiego
            print(f"[worker] BŁĄD zadania {job.__name__}: {exc}")


if __name__ == "__main__":
    run_daily()