from typing import Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.config import get_settings
from app.db import check_database

Status = Literal["ok", "degraded"]

router = APIRouter()


class Services(BaseModel):
    api: Status
    database: Status


class HealthResponse(BaseModel):
    status: Status
    services: Services


def aggregate_status(services: dict[str, Status]) -> Status:
    return "ok" if all(s == "ok" for s in services.values()) else "degraded"


@router.get("/health", response_model=HealthResponse, responses={503: {"model": HealthResponse}})
async def health() -> JSONResponse:
    services: dict[str, Status] = {
        "api": "ok",
        "database": "ok" if await check_database(get_settings()) else "degraded",
    }
    overall = aggregate_status(services)
    body = HealthResponse(status=overall, services=Services(**services))
    return JSONResponse(body.model_dump(), status_code=200 if overall == "ok" else 503)
