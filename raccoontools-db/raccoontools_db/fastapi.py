"""FastAPI integration module.

Provides a lifespan context manager that ties the connection pool
to FastAPI's startup/shutdown lifecycle.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from raccoontools_db.pool import PoolConfig, close_pool, create_pool


def create_lifespan(config: PoolConfig):
    """Create a FastAPI lifespan context manager.

    Opens the connection pool on startup and closes it on shutdown.

    Args:
        config: Pool configuration.

    Returns:
        An async context manager compatible with FastAPI's lifespan protocol.

    Usage::

        from raccoontools_db.fastapi import create_lifespan
        from raccoontools_db.pool import PoolConfig

        config = PoolConfig(conn_info="postgresql://user:pass@host/db")
        app = FastAPI(lifespan=create_lifespan(config))
    """

    @asynccontextmanager
    async def _lifespan(app: Any) -> AsyncGenerator[None]:
        create_pool(config)
        try:
            yield
        finally:
            close_pool()

    return _lifespan
