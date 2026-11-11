import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SpeciesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    feed_interval_days: int
    care_notes: str | None = None


SnakeStatus = Literal["active", "quarantine", "rest"]


class SnakeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    species_id: int
    birth_date: date | None = None
    photo_url: str | None = None
    status: SnakeStatus = "active"


class SnakeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    species_id: int | None = None
    birth_date: date | None = None
    photo_url: str | None = None
    status: SnakeStatus | None = None


class SnakeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    species_id: int
    birth_date: date | None
    photo_url: str | None
    status: str

EventType = Literal["weighing", "feeding", "shed", "other"]
SHED_CATEGORIES = {"complete", "incomplete"}
OTHER_CATEGORIES = {"equipment", "cleaning", "medication", "rest", "quarantine"}


class CareEventCreate(BaseModel):
    type: EventType
    event_date: date
    weight_g: float | None = Field(default=None, gt=0)
    food_type: str | None = Field(default=None, max_length=80)
    eaten: bool | None = None
    note_category: str | None = Field(default=None, max_length=32)
    note: str | None = None

    @model_validator(mode="after")
    def check_by_type(self):
        if self.event_date > date.today():
            raise ValueError("Data nie może być z przyszłości")
        if self.type == "weighing" and self.weight_g is None:
            raise ValueError("Ważenie wymaga wagi w gramach")
        if self.type == "feeding" and self.eaten is None:
            raise ValueError("Karmienie wymaga informacji, czy wąż zjadł")
        if self.type == "shed" and self.note_category not in SHED_CATEGORIES:
            raise ValueError("Wylinka: note_category to 'complete' lub 'incomplete'")
        if self.type == "other" and self.note_category not in OTHER_CATEGORIES:
            raise ValueError(f"Inne: note_category to jedno z {sorted(OTHER_CATEGORIES)}")
        return self


class CareEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    snake_id: uuid.UUID
    type: str
    event_date: date
    weight_g: float | None
    food_type: str | None
    eaten: bool | None
    note_category: str | None
    note: str | None


class SnakeCard(BaseModel):
    snake: SnakeOut
    last_weighing_date: date | None = None
    last_weight_g: float | None = None
    weight_change_g: float | None = None  # różnica względem poprzedniego ważenia
    last_feeding_date: date | None = None
    last_feeding_eaten: bool | None = None
    last_shed_date: date | None = None


class WeightPoint(BaseModel):
    date: date
    weight_g: float

ReminderType = Literal["feeding", "weighing", "cleaning"]
ReminderStatus = Literal["active", "paused"]


class ReminderCreate(BaseModel):
    type: ReminderType
    interval_days: int = Field(ge=1, le=365)
    next_due: date | None = None  # puste = ostatni wpis + interwał


class ReminderUpdate(BaseModel):
    interval_days: int | None = Field(default=None, ge=1, le=365)
    next_due: date | None = None
    status: ReminderStatus | None = None


class ReminderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    snake_id: uuid.UUID
    type: str
    next_due: date
    interval_days: int
    channel: str
    status: str

class AlertOut(BaseModel):
    id: uuid.UUID
    snake_id: uuid.UUID
    snake_name: str
    type: str
    message: str
    is_read: bool
    created_at: datetime


class UnreadCount(BaseModel):
    count: int


class AlertRuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    threshold: float
    window_days: int
    enabled: bool


class AlertRuleUpdate(BaseModel):
    threshold: float | None = Field(default=None, gt=0)
    window_days: int | None = Field(default=None, ge=1, le=365)
    enabled: bool | None = None