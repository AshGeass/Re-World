from fastapi import FastAPI

from database import init_db
from .routes import (
    branches_router,
    characters_router,
    chat_router,
    stories_router,
    timelines_router,
    world_state_router,
)

app = FastAPI(
    title="Re:World API",
    version="0.1.0",
)


@app.on_event("startup")
def startup():
    init_db()


app.include_router(stories_router)
app.include_router(characters_router)
app.include_router(chat_router)
app.include_router(timelines_router)
app.include_router(branches_router)
app.include_router(world_state_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "reworld"}