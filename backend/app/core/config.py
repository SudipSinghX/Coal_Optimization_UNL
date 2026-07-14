"""Centralized application settings loaded from environment variables (.env).

Database URL normalization
--------------------------
Render (and many PaaS providers) inject a ``DATABASE_URL`` environment variable
whose scheme is ``postgres://`` or ``postgresql://``.  psycopg3 (our driver)
requires the scheme ``postgresql+psycopg://``.

Resolution order for the database connection string:
  1. ``DATABASE_URL`` env var  (Render's standard name)
  2. ``database_url`` env var  (our legacy/local name)
  3. Hardcoded development default (localhost)

The scheme is normalised automatically at load time so the caller never needs
to worry about ``postgres://`` vs ``postgresql+psycopg://``.
"""

import logging
import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("codsp.config")


def _normalize_db_url(url: str) -> str:
    """Rewrite scheme so psycopg3 can handle any common PostgreSQL URL format."""
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Application
    app_name: str = "UPRVUNL CODSP Backend"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173,https://coal-optimization-unl.vercel.app"
    cors_origins: str | None = None

    # Database
    # Pydantic-settings will read `database_url` from the env var DATABASE_URL
    # (it maps snake_case field names to UPPER_CASE env vars automatically).
    # Render injects DATABASE_URL so this field is populated in production.
    database_url: str = "postgresql+psycopg://codsp_user:change_me@localhost:5432/codsp_db"

    # Storage
    document_storage_path: str = "./storage/documents"
    document_max_upload_size_bytes: int = 35 * 1024 * 1024

    # Daily stock validation
    stock_reconciliation_tolerance_mt: float = 0.01

    # Optimization
    optimization_fallback_landed_cost: float = 0.0
    optimization_market_topup_multiplier: float = 1.20
    optimization_demand_horizon_days: int = 30

    # UPSLDC Scheduler (legacy ingestion config)
    upsldc_source_url: str = "https://upsldc.org/variable-cost"
    upsldc_max_pdfs_per_run: int = 10
    scheduler_enabled: bool = False
    scheduler_cron_hour: int = 6
    scheduler_cron_minute: int = 0
    scheduler_timezone: str = "Asia/Kolkata"
    scheduler_document_check_hour: int = 6
    scheduler_document_check_minute: int = 0

    # UPSLDC MOD Reports Monitor (Milestone 9B)
    upsldc_mod_reports_url: str = "https://www.upsldc.org/schmod"
    upsldc_monitor_enabled: bool = False
    upsldc_monitor_top_n: int = 10
    upsldc_monitor_timeout_seconds: int = 20
    upsldc_monitor_user_agent: str = "CODSP-UPSLDC-Monitor/1.0"
    upsldc_monitor_schedule_days: str = "2,16"
    upsldc_monitor_hour: int = 9
    upsldc_monitor_minute: int = 0

    # Whole-site Access Password Gate
    site_access_password: str | None = None


@lru_cache
def get_settings() -> Settings:
    raw = Settings()
    # Normalize the database URL scheme for psycopg3 compatibility.
    # pydantic-settings reads DATABASE_URL → database_url automatically,
    # but Render sends postgres:// or postgresql:// which psycopg3 rejects.
    normalized = _normalize_db_url(raw.database_url)
    if normalized != raw.database_url:
        # Re-construct with the corrected URL (override via env-like mutation)
        raw = raw.model_copy(update={"database_url": normalized})
        logger.info("[config] Normalized DATABASE_URL scheme to postgresql+psycopg://")
    logger.info(
        "[config] database_url = %s",
        raw.database_url.split("@")[-1] if "@" in raw.database_url else "<no-auth-url>",
    )
    return raw
