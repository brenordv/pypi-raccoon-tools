"""Managed PostgreSQL connection pool with opt-in FastAPI and OTEL integrations."""

from raccoontools_db.pool import PoolConfig, close_pool, create_pool, get_pool

__all__ = ["PoolConfig", "create_pool", "get_pool", "close_pool"]