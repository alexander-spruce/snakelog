from sqlalchemy import select

from app.database import SessionLocal
from app.models import AlertRule, Species

SPECIES = [
    ("Pyton królewski", 10),
    ("Wąż zbożowy", 7),
    ("Wąż mleczny", 7),
    ("Boa dusiciel", 14),
    ("Pyton siatkowy", 14),
]

# (typ, threshold, window_days)
RULES = [
    ("weight_drop", 5, 30),
    ("no_growth_young", 730, 60),
    ("feeding_refusal", 2, 14),
]


def run():
    with SessionLocal() as db:
        for name, interval in SPECIES:
            if not db.scalar(select(Species).where(Species.name == name)):
                db.add(Species(name=name, feed_interval_days=interval))
        for type_, threshold, window in RULES:
            if not db.scalar(select(AlertRule).where(AlertRule.type == type_)):
                db.add(AlertRule(type=type_, threshold=threshold, window_days=window, enabled=True))
        db.commit()


if __name__ == "__main__":
    run()