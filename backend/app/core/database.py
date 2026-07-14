"""SQLAlchemy engine, session factory, and declarative base."""

import logging
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

logger = logging.getLogger("codsp.database")

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """Base class for all ORM models."""


def probe_database() -> bool:
    """Attempt a cheap SELECT 1 probe and return True on success.

    Call this once at startup to surface connection problems immediately
    rather than waiting for the first API request to fail.
    """
    host = settings.database_url.split("@")[-1] if "@" in settings.database_url else "unknown"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("[database] Connected to PostgreSQL at %s", host)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "[database] CANNOT connect to PostgreSQL at %s — %s: %s",
            host,
            type(exc).__name__,
            exc,
        )
        return False


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
