from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.core.config import settings
from app.db import init_db, seed_dummy_data

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    seed_dummy_data()


@app.get("/")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
