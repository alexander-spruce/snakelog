from sqlalchemy import select

from app.database import SessionLocal
from app.models import Species

SPECIES = [
    ("Pyton królewski", 10),
    ("Wąż zbożowy", 7),
    ("Wąż mleczny", 7),
    ("Boa dusiciel", 14),
    ("Pyton siatkowy", 14),
]


def run():
    with SessionLocal() as db:
        for name, interval in SPECIES:
            if not db.scalar(select(Species).where(Species.name == name)):
                db.add(Species(name=name, feed_interval_days=interval))
        db.commit()


if __name__ == "__main__":
    run()