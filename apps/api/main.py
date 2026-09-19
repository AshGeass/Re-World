from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from database import init_db

logger = logging.getLogger("reworld")

app = FastAPI(
    title="Re:World API",
    description="Multi-Agent Narrative Framework",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()
    # Seed demo world into in-memory store on startup
    from scripts.seed_demo import seed_demo
    try:
        seed_demo()
        logger.info("Demo world seeded.")
    except Exception as e:
        logger.warning(f"Demo seed skipped: {e}")


# Register routers
from apps.api.routes.stories import router as stories_router  # noqa: E402
from apps.api.routes.characters import router as characters_router  # noqa: E402
from apps.api.routes.chat import router as chat_router  # noqa: E402
from apps.api.routes.timelines import router as timelines_router  # noqa: E402
from apps.api.routes.branches import router as branches_router  # noqa: E402
from apps.api.routes.world_state import router as world_state_router  # noqa: E402

app.include_router(stories_router, prefix="/api")
app.include_router(characters_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(timelines_router, prefix="/api")
app.include_router(branches_router, prefix="/api")
app.include_router(world_state_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok", "service": "reworld"}