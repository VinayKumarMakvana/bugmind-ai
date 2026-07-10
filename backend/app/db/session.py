from __future__ import annotations

import logging

import certifi
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)

from ..core.config import settings

logger = logging.getLogger(__name__)

# =========================================================
# DATABASE NAME
# =========================================================

def get_database_name(uri: str) -> str:
    """
    Extract database name from MongoDB URI.
    """

    try:

        database = (
            uri.rsplit("/", 1)[-1]
            .split("?")[0]
            .strip()
        )

        return database or "bugmind"

    except Exception:

        return "bugmind"


# =========================================================
# MONGO CLIENT
# =========================================================

client = AsyncIOMotorClient(
    settings.DATABASE_URL,
    tlsCAFile=certifi.where(),
)

DATABASE_NAME = get_database_name(
    settings.DATABASE_URL
)

db: AsyncIOMotorDatabase = client[
    DATABASE_NAME
]


# =========================================================
# DATABASE DEPENDENCY
# =========================================================

async def get_db():
    """
    FastAPI dependency.
    """

    yield db


# =========================================================
# HEALTH CHECK
# =========================================================

async def ping_database() -> bool:
    """
    Check MongoDB connection.
    """

    try:

        await client.admin.command("ping")

        logger.info(
            "MongoDB Connected."
        )

        return True

    except Exception:

        logger.exception(
            "MongoDB Connection Failed."
        )

        return False


# =========================================================
# CLOSE CONNECTION
# =========================================================

async def close_database() -> None:
    """
    Close MongoDB client.
    """

    client.close()

    logger.info(
        "MongoDB Connection Closed."
    )


__all__ = [
    "client",
    "db",
    "get_db",
    "ping_database",
    "close_database",
]