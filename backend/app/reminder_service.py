from datetime import date, timedelta
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import CareEvent, Reminder

# typ przypomnienia -> (typ wpisu w dzienniku, wymagana kategoria)
SOURCE = {
    "feeding": ("feeding", None),
    "weighing": ("weighing", None),
    "cleaning": ("other", "cleaning"),
}


def last_event_date(db: Session, snake_id: uuid.UUID, reminder_type: str) -> date | None:
    event_type, category = SOURCE[reminder_type]
    query = select(func.max(CareEvent.event_date)).where(
        CareEvent.snake_id == snake_id, CareEvent.type == event_type
    )
    if category:
        query = query.where(CareEvent.note_category == category)
    return db.scalar(query)


def compute_next_due(db: Session, snake_id: uuid.UUID, reminder_type: str, interval_days: int) -> date:
    base = last_event_date(db, snake_id, reminder_type) or date.today()
    return base + timedelta(days=interval_days)


def recalc_for_snake(db: Session, snake_id: uuid.UUID) -> None:
    """Przelicza terminy aktywnych przypomnień po dodaniu, edycji lub usunięciu wpisu."""
    reminders = db.scalars(
        select(Reminder).where(Reminder.snake_id == snake_id, Reminder.status == "active")
    ).all()
    for reminder in reminders:
        last = last_event_date(db, snake_id, reminder.type)
        if last is not None:
            reminder.next_due = last + timedelta(days=reminder.interval_days)
    db.commit()