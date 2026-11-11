from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import admin, alerts, auth, carelog, reminders, snakes

app = FastAPI(title="SnakeLog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(snakes.router)
app.include_router(carelog.router)
app.include_router(reminders.router)
app.include_router(alerts.router)
app.include_router(admin.router)
@app.get("/health")
def health():
    return {"status": "ok"}