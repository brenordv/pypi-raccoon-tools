"""Internal logger abstraction.

Returns an OTEL tracer or a standard logger depending on configuration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from raccoontools_db.pool import PoolConfig

_PACKAGE_LOGGER_NAME = "raccoontools_db"


def _get_logger(config: PoolConfig):
    """Return a logger/tracer based on config.

    Args:
        config: Pool configuration containing OTEL settings.

    Returns:
        - use_otel=False: a standard logging.Logger via simple_log_factory.
        - use_otel=True: an OTEL tracer via simple_log_factory_ext_otel.

    Raises:
        ImportError: If use_otel=True but simple-log-factory-ext-otel is not installed.
    """
    if not config.use_otel:
        from simple_log_factory import log_factory

        return log_factory(_PACKAGE_LOGGER_NAME, unique_handler_types=True)

    try:
        from simple_log_factory_ext_otel import otel_log_factory
    except ImportError as exc:
        raise ImportError(
            "OpenTelemetry support requires the 'simple-log-factory-ext-otel' package. "
            "Install it with: pip install raccoontools-db[otel]"
        ) from exc

    return otel_log_factory(
        service_name=config.otel_service_name,
        otel_exporter_endpoint=config.otel_exporter_endpoint,
        use_http_protocol=config.otel_use_http,
    )
