from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import AlertRule, User
from app.schemas import AlertRuleOut, AlertRuleUpdate

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/alert-rules", response_model=list[AlertRuleOut])
def list_rules(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.scalars(select(AlertRule).order_by(AlertRule.id)).all()


@router.patch("/alert-rules/{rule_id}", response_model=AlertRuleOut)
def update_rule(
    rule_id: int,
    data: AlertRuleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    rule = db.get(AlertRule, rule_id)
    if rule is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie znaleziono reguły")
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(rule, field, value)
    db.commit()
    db.refresh(rule)
    return rule