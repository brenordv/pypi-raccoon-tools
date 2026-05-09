"""FastAPI integration module.

Provides a lifespan context manager that ties the connection pool
to FastAPI's startup/shutdown lifecycle.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from raccoontools_db.pool import PoolConfig, close_pool, create_pool


@asynccontextmanager
async def create_lifespan(config: PoolConfig) -> AsyncGenerator:
    """FastAPI lifespan context manager.

    Opens the connection pool on startup and closes it on shutdown.

    Args:
        config: Pool configuration.

    Usage::

        from raccoontools_db.fastapi import create_lifespan
        from raccoontools_db.pool import PoolConfig

        config = PoolConfig(conninfo="postgresql://user:pass@host/db")
        app = FastAPI(lifespan=create_lifespan(config))
    """
    create_pool(config)
    try:
        yield
    finally:
        close_pool()
