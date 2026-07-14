import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

logger = logging.getLogger("codsp.health")

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Reports API liveness and database connectivity.

    Returns HTTP 200 when both the API and the database are reachable.
    Returns HTTP 503 when the database cannot be reached so monitoring
    tools and Render's health checks surface the failure immediately.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:  # noqa: BLE001
        logger.error("[health] Database probe failed: %s: %s", type(exc).__name__, exc)
        db_status = "unavailable"

    payload = {"status": "ok" if db_status == "ok" else "degraded", "database": db_status}
    status_code = 200 if db_status == "ok" else 503
    return JSONResponse(content=payload, status_code=status_code)
