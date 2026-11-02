import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.reminder_service import recalc_for_snake

from app.database import get_db
from app.deps import get_current_user
from app.models import CareEvent, User
from app.routers.snakes import get_own_snake
from app.schemas import (
    CareEventCreate, CareEventOut, EventType, SnakeCard, SnakeOut, WeightPoint,
)

router = APIRouter(prefix="/api/snakes/{snake_id}", tags=["carelog"])


def get_own_event(db: Session, snake_id: uuid.UUID, event_id: uuid.UUID, user: User) -> CareEvent:
    get_own_snake(db, snake_id, user)  # 404, jeśli wąż nie jest użytkownika
    event = db.get(CareEvent, event_id)
    if event is None or event.snake_id != snake_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie znaleziono wpisu")
    return event


def _latest(db: Session, snake_id: uuid.UUID, type_: str, limit: int = 1) -> list[CareEvent]:
    return list(
        db.scalars(
            select(CareEvent)
            .where(CareEvent.snake_id == snake_id, CareEvent.type == type_)
            .order_by(CareEvent.event_date.desc())
            .limit(limit)
        )
    )


@router.post("/events", response_model=CareEventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    snake_id: uuid.UUID,
    data: CareEventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    get_own_snake(db, snake_id, user)
    event = CareEvent(snake_id=snake_id, **data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    recalc_for_snake(db, snake_id)
    return event


@router.get("/events", response_model=list[CareEventOut])
def list_events(
    snake_id: uuid.UUID,
    type: EventType | None = Query(default=None),
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    get_own_snake(db, snake_id, user)
    query = select(CareEvent).where(CareEvent.snake_id == snake_id)
    if type:
        query = query.where(CareEvent.type == type)
    if date_from:
        query = query.where(CareEvent.event_date >= date_from)
    if date_to:
        query = query.where(CareEvent.event_date <= date_to)
    return db.scalars(query.order_by(CareEvent.event_date.desc())).all()


@router.put("/events/{event_id}", response_model=CareEventOut)
def update_event(
    snake_id: uuid.UUID,
    event_id: uuid.UUID,
    data: CareEventCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    event = get_own_event(db, snake_id, event_id, user)
    for field, value in data.model_dump().items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    recalc_for_snake(db, snake_id)
    return event


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    snake_id: uuid.UUID,
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    event = get_own_event(db, snake_id, event_id, user)
    db.delete(event)
    db.commit()
    recalc_for_snake(db, snake_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/card", response_model=SnakeCard)
def snake_card(
    snake_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    snake = get_own_snake(db, snake_id, user)
    card = SnakeCard(snake=SnakeOut.model_validate(snake))

    weighings = _latest(db, snake_id, "weighing", limit=2)
    if weighings:
        card.last_weighing_date = weighings[0].event_date
        card.last_weight_g = float(weighings[0].weight_g)
        if len(weighings) == 2:
            card.weight_change_g = round(
                float(weighings[0].weight_g) - float(weighings[1].weight_g), 1
            )

    feedings = _latest(db, snake_id, "feeding")
    if feedings:
        card.last_feeding_date = feedings[0].event_date
        card.last_feeding_eaten = feedings[0].eaten

    sheds = _latest(db, snake_id, "shed")
    if sheds:
        card.last_shed_date = sheds[0].event_date

    return card


@router.get("/weights", response_model=list[WeightPoint])
def weight_chart(
    snake_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    get_own_snake(db, snake_id, user)
    rows = db.execute(
        select(CareEvent.event_date, CareEvent.weight_g)
        .where(CareEvent.snake_id == snake_id, CareEvent.type == "weighing")
        .order_by(CareEvent.event_date.asc())
    ).all()
    return [WeightPoint(date=d, weight_g=float(w)) for d, w in rows]