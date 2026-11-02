from fastapi import FastAPI

app = FastAPI(title="SnakeLog API")


@app.get("/health")
def health():
    return {"status": "ok"}