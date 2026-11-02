from datetime import date, timedelta

from sqlalchemy import select

from app.database import SessionLocal
from app.models import CareEvent, Reminder, Snake, Species, User
from app.security import hash_password

DEMO_EMAIL = "demo@snakelog.pl"
DEMO_PASSWORD = "haslo1234"


def species_id(db, name: str) -> int:
    sp = db.scalar(select(Species).where(Species.name == name))
    if sp is None:
        raise SystemExit(f"Brak gatunku '{name}'. Najpierw uruchom: python -m app.seed")
    return sp.id


def add(db, snake_id, type_, day, **kw):
    db.add(CareEvent(snake_id=snake_id, type=type_, event_date=day, **kw))


def run():
    today = date.today()
    with SessionLocal() as db:
        old = db.scalar(select(User).where(User.email == DEMO_EMAIL))
        if old:
            db.delete(old)  # CASCADE usuwa węże, wpisy i przypomnienia
            db.commit()

        user = User(email=DEMO_EMAIL, password_hash=hash_password(DEMO_PASSWORD))
        db.add(user)
        db.flush()

        # --- Wąż 1: Kaa, pyton królewski, aktywny, 14 ważeń co 10 dni ---
        kaa = Snake(
            user_id=user.id, name="Kaa", status="active",
            species_id=species_id(db, "Pyton królewski"),
            birth_date=today - timedelta(days=700),
        )
        db.add(kaa)
        db.flush()

        wobble = [0, 8, -5, 6, -8, 10, 0, 7, -6, 9, -4, 8, 0, 6]
        for i in range(14):
            day = today - timedelta(days=10 * (14 - i))
            add(db, kaa.id, "weighing", day, weight_g=900 + i * 35 + wobble[i])
            refused = i == 6
            add(db, kaa.id, "feeding", day, food_type="szczur M", eaten=not refused)
        add(db, kaa.id, "shed", today - timedelta(days=45), note_category="complete")
        add(db, kaa.id, "shed", today - timedelta(days=100), note_category="incomplete")
        add(db, kaa.id, "other", today - timedelta(days=20), note_category="cleaning",
            note="Pełne czyszczenie terrarium")
        add(db, kaa.id, "other", today - timedelta(days=60), note_category="equipment",
            note="Wymiana żarówki UVB")
        db.add(Reminder(snake_id=kaa.id, type="feeding", interval_days=10,
                        next_due=today, channel="email", status="active"))
        db.add(Reminder(snake_id=kaa.id, type="cleaning", interval_days=30,
                        next_due=today + timedelta(days=10), channel="email", status="active"))

        # --- Wąż 2: Nagini, wąż zbożowy, kwarantanna, spadek wagi na końcu ---
        nagini = Snake(
            user_id=user.id, name="Nagini", status="quarantine",
            species_id=species_id(db, "Wąż zbożowy"),
            birth_date=today - timedelta(days=300),
        )
        db.add(nagini)
        db.flush()

        weights = [420, 438, 455, 470, 488, 495, 482, 461]
        for i, w in enumerate(weights):
            day = today - timedelta(days=14 * (len(weights) - i))
            add(db, nagini.id, "weighing", day, weight_g=w)
        add(db, nagini.id, "feeding", today - timedelta(days=14), food_type="mysz S", eaten=False)
        add(db, nagini.id, "feeding", today - timedelta(days=7), food_type="mysz S", eaten=False)
        add(db, nagini.id, "other", today - timedelta(days=21), note_category="quarantine",
            note="Nowy wąż, kwarantanna 90 dni")
        db.add(Reminder(snake_id=nagini.id, type="weighing", interval_days=14,
                        next_due=today, channel="email", status="active"))

        db.commit()
        print(f"Dane demo gotowe. Login: {DEMO_EMAIL}  Hasło: {DEMO_PASSWORD}")


if __name__ == "__main__":
    run()