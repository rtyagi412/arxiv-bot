import asyncio
import logging

import psycopg

from app.config import Settings

logger = logging.getLogger(__name__)


async def check_database(settings: Settings) -> bool:
    """Return True if a real connection can run SELECT 1 within the timeout.

    Any failure returns False. Exception text is deliberately not logged or returned:
    it can contain the host, user or other connection details (FR-13).
    """
    timeout = settings.db_connect_timeout_seconds
    try:
        async with asyncio.timeout(timeout):
            async with await psycopg.AsyncConnection.connect(
                host=settings.db_host,
                port=settings.db_port,
                user=settings.db_user,
                password=settings.db_password.get_secret_value(),
                dbname=settings.db_name,
                connect_timeout=max(1, int(timeout)),
            ) as conn:
                await conn.execute("SELECT 1")
    except Exception:
        logger.warning("database health check failed")
        return False
    return True
