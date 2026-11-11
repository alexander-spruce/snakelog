import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import HealthAlert, Snake, User
from app.schemas import AlertOut, UnreadCount

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


def _out(alert: HealthAlert, snake_name: str) -> AlertOut:
    return AlertOut(
        id=alert.id, snake_id=alert.snake_id, snake_name=snake_name, type=alert.type,
        message=alert.message, is_read=alert.is_read, created_at=alert.created_at,
    )


@router.get("", response_model=list[AlertOut])
def list_alerts(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = (
        select(HealthAlert, Snake.name)
        .join(Snake, HealthAlert.snake_id == Snake.id)
        .where(Snake.user_id == user.id)
    )
    if unread_only:
        query = query.where(HealthAlert.is_read.is_(False))
    rows = db.execute(query.order_by(HealthAlert.created_at.desc())).all()
    return [_out(alert, name) for alert, name in rows]


@router.get("/unread-count", response_model=UnreadCount)
def unread_count(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    count = db.scalar(
        select(func.count())
        .select_from(HealthAlert)
        .join(Snake, HealthAlert.snake_id == Snake.id)
        .where(Snake.user_id == user.id, HealthAlert.is_read.is_(False))
    )
    return UnreadCount(count=count or 0)


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
def read_all(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    own_snakes = select(Snake.id).where(Snake.user_id == user.id)
    db.execute(
        update(HealthAlert)
        .where(HealthAlert.snake_id.in_(own_snakes), HealthAlert.is_read.is_(False))
        .values(is_read=True)
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{alert_id}/read", response_model=AlertOut)
def mark_read(
    alert_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = db.execute(
        select(HealthAlert, Snake.name)
        .join(Snake, HealthAlert.snake_id == Snake.id)
        .where(HealthAlert.id == alert_id, Snake.user_id == user.id)
    ).first()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie znaleziono alertu")
    alert, name = row
    alert.is_read = True
    db.commit()
    db.refresh(alert)
    return _out(alert, name)