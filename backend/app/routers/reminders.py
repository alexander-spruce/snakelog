import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Reminder, User
from app.reminder_service import compute_next_due
from app.routers.snakes import get_own_snake
from app.schemas import ReminderCreate, ReminderOut, ReminderUpdate

router = APIRouter(prefix="/api/snakes/{snake_id}/reminders", tags=["reminders"])


def get_own_reminder(db: Session, snake_id: uuid.UUID, reminder_id: uuid.UUID, user: User) -> Reminder:
    get_own_snake(db, snake_id, user)
    reminder = db.get(Reminder, reminder_id)
    if reminder is None or reminder.snake_id != snake_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie znaleziono przypomnienia")
    return reminder


@router.get("", response_model=list[ReminderOut])
def list_reminders(
    snake_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    get_own_snake(db, snake_id, user)
    return db.scalars(
        select(Reminder).where(Reminder.snake_id == snake_id).order_by(Reminder.next_due)
    ).all()


@router.post("", response_model=ReminderOut, status_code=status.HTTP_201_CREATED)
def create_reminder(
    snake_id: uuid.UUID,
    data: ReminderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    get_own_snake(db, snake_id, user)
    exists = db.scalar(
        select(Reminder).where(Reminder.snake_id == snake_id, Reminder.type == data.type)
    )
    if exists:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Ten wąż ma już przypomnienie tego typu"
        )
    next_due = data.next_due or compute_next_due(db, snake_id, data.type, data.interval_days)
    reminder = Reminder(
        snake_id=snake_id, type=data.type, interval_days=data.interval_days,
        next_due=next_due, channel="email", status="active",
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.patch("/{reminder_id}", response_model=ReminderOut)
def update_reminder(
    snake_id: uuid.UUID,
    reminder_id: uuid.UUID,
    data: ReminderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    reminder = get_own_reminder(db, snake_id, reminder_id, user)
    changes = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
    for field, value in changes.items():
        setattr(reminder, field, value)
    if "interval_days" in changes and "next_due" not in changes:
        reminder.next_due = compute_next_due(db, snake_id, reminder.type, reminder.interval_days)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(
    snake_id: uuid.UUID,
    reminder_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    reminder = get_own_reminder(db, snake_id, reminder_id, user)
    db.delete(reminder)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)