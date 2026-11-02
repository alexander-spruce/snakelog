import time
from datetime import datetime, timedelta

from app.worker import run_once

RUN_HOUR = 8  # godzina uruchomienia dziennego (czas kontenera, UTC)


def seconds_until_next_run() -> float:
    now = datetime.now()
    nxt = now.replace(hour=RUN_HOUR, minute=0, second=0, microsecond=0)
    if nxt <= now:
        nxt += timedelta(days=1)
    return (nxt - now).total_seconds()


def safe_run() -> None:
    try:
        run_once()
    except Exception as exc:  # worker ma przeżyć błąd jednego uruchomienia
        print(f"[worker] BŁĄD uruchomienia: {exc}")


if __name__ == "__main__":
    print("[worker] start, pierwsze uruchomienie od razu")
    safe_run()
    while True:
        wait = seconds_until_next_run()
        print(f"[worker] następne uruchomienie za {wait / 3600:.1f} h")
        time.sleep(wait)
        safe_run()