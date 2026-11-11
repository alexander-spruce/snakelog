from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AlertRule, CareEvent, HealthAlert, Snake, User

COOLDOWN_DAYS = 7  # nie powtarzamy alertu tego samego typu częściej niż raz na tydzień
DISCLAIMER = "To wskazówka pomocnicza, nie diagnoza. W razie wątpliwości skontaktuj się z lekarzem weterynarii."


def _weighings(db: Session, snake_id, since: date | None = None) -> list[CareEvent]:
    query = select(CareEvent).where(CareEvent.snake_id == snake_id, CareEvent.type == "weighing")
    if since:
        query = query.where(CareEvent.event_date >= since)
    return list(db.scalars(query.order_by(CareEvent.event_date.asc())))


def check_weight_drop(db: Session, snake: Snake, rule: AlertRule, today: date) -> str | None:
    weighings = _weighings(db, snake.id)
    if len(weighings) < 2:
        return None
    last = weighings[-1]
    if (today - last.event_date).days > rule.window_days:
        return None  # ostatnie ważenie jest zbyt stare, żeby alarmować
    since = last.event_date - timedelta(days=rule.window_days)
    earlier = [w for w in weighings[:-1] if w.event_date >= since]
    if not earlier:
        return None
    peak = max(earlier, key=lambda w: float(w.weight_g))
    drop = (float(peak.weight_g) - float(last.weight_g)) / float(peak.weight_g) * 100
    if drop < float(rule.threshold):
        return None
    return (
        f"Waga spadła o {drop:.1f}% (z {float(peak.weight_g):g} g, {peak.event_date:%d.%m.%Y}, "
        f"do {float(last.weight_g):g} g, {last.event_date:%d.%m.%Y}). {DISCLAIMER}"
    )


def check_no_growth_young(db: Session, snake: Snake, rule: AlertRule, today: date) -> str | None:
    if snake.birth_date is None:
        return None
    if (today - snake.birth_date).days > float(rule.threshold):
        return None  # wąż nie jest już "młody"
    weighings = _weighings(db, snake.id, since=today - timedelta(days=rule.window_days))
    if len(weighings) < 2:
        return None
    first, last = weighings[0], weighings[-1]
    gain = float(last.weight_g) - float(first.weight_g)
    if gain > 0:
        return None
    return (
        f"Młody wąż nie przybiera na wadze od {rule.window_days} dni "
        f"({float(first.weight_g):g} g → {float(last.weight_g):g} g). {DISCLAIMER}"
    )


def check_feeding_refusal(db: Session, snake: Snake, rule: AlertRule, today: date) -> str | None:
    if snake.status == "rest":
        return None  # w okresie spoczynku odmowa jedzenia bywa normalna
    feedings = list(
        db.scalars(
            select(CareEvent)
            .where(CareEvent.snake_id == snake.id, CareEvent.type == "feeding")
            .order_by(CareEvent.event_date.asc())
        )
    )
    eaten = [f for f in feedings if f.eaten]
    last_eaten = eaten[-1].event_date if eaten else None
    refusals = [f for f in feedings if not f.eaten and (last_eaten is None or f.event_date > last_eaten)]
    if len(refusals) < float(rule.threshold):
        return None
    start = last_eaten or refusals[0].event_date
    days = (today - start).days
    if days < rule.window_days:
        return None
    return (
        f"Wąż odmawia jedzenia: {len(refusals)} odmowy z rzędu, od {days} dni "
        f"bez zjedzonego posiłku. {DISCLAIMER}"
    )


CHECKS = {
    "weight_drop": check_weight_drop,
    "no_growth_young": check_no_growth_young,
    "feeding_refusal": check_feeding_refusal,
}


def generate_alerts(db: Session, today: date | None = None) -> list[tuple[str, str, str, str]]:
    """Analizuje każdego węża według włączonych reguł i zapisuje nowe alerty.

    Zwraca listę (wiadomość, e-mail właściciela, imię węża, typ) do powiadomień.
    """
    today = today or date.today()
    cutoff = datetime.now(timezone.utc) - timedelta(days=COOLDOWN_DAYS)
    rules = db.scalars(select(AlertRule).where(AlertRule.enabled.is_(True))).all()
    rows = db.execute(
        select(Snake, User).join(User, Snake.user_id == User.id).where(User.is_blocked.is_(False))
    ).all()

    created: list[tuple[str, str, str, str]] = []
    for snake, user in rows:
        for rule in rules:
            check = CHECKS.get(rule.type)
            if check is None:
                continue
            recent = db.scalar(
                select(HealthAlert.id)
                .where(
                    HealthAlert.snake_id == snake.id,
                    HealthAlert.type == rule.type,
                    HealthAlert.created_at >= cutoff,
                )
                .limit(1)
            )
            if recent:
                continue
            message = check(db, snake, rule, today)
            if message:
                db.add(HealthAlert(snake_id=snake.id, rule_id=rule.id, type=rule.type, message=message))
                created.append((message, user.email, snake.name, rule.type))
    db.commit()
    return created