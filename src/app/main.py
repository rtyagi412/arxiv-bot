from fastapi import FastAPI

from app.config import get_settings
from app.health import router as health_router

# Load settings at import so missing required DB settings stop startup (C-5).
get_settings()

app = FastAPI(title="arxiv-bot")
app.include_router(health_router)
