"""Public pool management module.

Provides a module-level singleton connection pool with create/get/close lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass

from psycopg_pool import ConnectionPool

from raccoontools_db._logger import _get_logger

_pool: ConnectionPool | None = None
_logger = None


@dataclass(frozen=True, slots=True)
class PoolConfig:
    """Configuration for the connection pool."""

    conn_info: str
    """PostgreSQL connection string."""

    min_size: int = 2
    """Minimum connections in pool."""

    max_size: int = 10
    """Maximum connections in pool."""

    use_otel: bool = False
    """Enable OpenTelemetry tracing."""

    otel_service_name: str = ""
    """Required when use_otel=True."""

    otel_exporter_endpoint: str = ""
    """Required when use_otel=True."""

    otel_use_http: bool = True
    """OTLP protocol (HTTP vs gRPC)."""

    def __post_init__(self):
        if self.use_otel and not self.otel_service_name:
            raise ValueError("otel_service_name is required when use_otel=True")

        if self.use_otel and not self.otel_exporter_endpoint:
            raise ValueError("otel_exporter_endpoint is required when use_otel=True")


def create_pool(config: PoolConfig) -> None:
    """Create and open the global connection pool.

    Args:
        config: Pool configuration.

    Raises:
        RuntimeError: If a pool already exists (call close_pool() first).
        ImportError: If use_otel=True but the OTEL package is not installed.
    """
    global _pool, _logger

    if _pool is not None:
        raise RuntimeError(
            "Connection pool already exists. Call close_pool() before creating a new one."
        )

    _logger = _get_logger(config)
    _logger.info("Creating database connection pool")

    _pool = ConnectionPool(
        conninfo=config.conn_info,
        min_size=config.min_size,
        max_size=config.max_size,
    )
    _pool.open()

    _logger.info("Database connection pool opened")


def get_pool() -> ConnectionPool:
    """Return the active connection pool.

    Returns:
        The active ConnectionPool instance.

    Raises:
        RuntimeError: If the pool has not been created yet.
    """
    if _pool is None:
        raise RuntimeError(
            "Database pool is not initialised. Call create_pool() first."
        )
    return _pool


def close_pool() -> None:
    """Close the global pool and reset state.

    Safe to call if the pool is already closed or was never created.
    """
    global _pool, _logger

    if _pool is None:
        return

    if _logger is not None:
        _logger.info("Closing database connection pool")

    _pool.close()
    _pool = None
    _logger = None
