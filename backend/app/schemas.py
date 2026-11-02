import uuid
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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