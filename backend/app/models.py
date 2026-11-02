import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Integer,
    Numeric, String, Text, Uuid, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('user','moderator','admin')", name="ck_users_role"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16), default="user")
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Species(Base):
    __tablename__ = "species"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    feed_interval_days: Mapped[int] = mapped_column(Integer)
    care_notes: Mapped[str | None] = mapped_column(Text)


class Snake(Base):
    __tablename__ = "snakes"
    __table_args__ = (
        CheckConstraint("status IN ('active','quarantine','rest')", name="ck_snakes_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    species_id: Mapped[int] = mapped_column(ForeignKey("species.id"))
    name: Mapped[str] = mapped_column(String(80))
    photo_url: Mapped[str | None] = mapped_column(Text)
    birth_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(16), default="active")


class CareEvent(Base):
    __tablename__ = "care_events"
    __table_args__ = (
        CheckConstraint("type IN ('weighing','feeding','shed','other')", name="ck_care_events_type"),
        CheckConstraint("type <> 'weighing' OR weight_g > 0", name="ck_care_events_weight"),
        Index("ix_care_events_snake_date", "snake_id", "event_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    snake_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("snakes.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(16))
    event_date: Mapped[date] = mapped_column(Date)
    weight_g: Mapped[float | None] = mapped_column(Numeric(8, 1))
    food_type: Mapped[str | None] = mapped_column(String(80))
    eaten: Mapped[bool | None] = mapped_column(Boolean)
    note_category: Mapped[str | None] = mapped_column(String(32))
    note: Mapped[str | None] = mapped_column(Text)


class Reminder(Base):
    __tablename__ = "reminders"
    __table_args__ = (
        CheckConstraint("status IN ('active','paused')", name="ck_reminders_status"),
        Index("ix_reminders_next_due", "next_due"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    snake_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("snakes.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(16))
    next_due: Mapped[date] = mapped_column(Date)
    interval_days: Mapped[int] = mapped_column(Integer)
    channel: Mapped[str] = mapped_column(String(16), default="email")
    status: Mapped[str] = mapped_column(String(16), default="active")