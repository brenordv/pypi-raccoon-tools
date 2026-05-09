"""Tests for raccoontools_db._logger module."""

import sys
from unittest.mock import MagicMock

import pytest

from raccoontools_db.pool import PoolConfig


class TestStandardLogger:
    def test_returns_standard_logger(self, mocker):
        mock_log_factory = mocker.patch(
            "simple_log_factory.log_factory", create=True
        )
        config = PoolConfig(conn_info="postgresql://localhost/db", use_otel=False)

        from raccoontools_db._logger import _get_logger

        result = _get_logger(config)

        mock_log_factory.assert_called_once_with(
            "raccoontools_db", unique_handler_types=True
        )
        assert result is mock_log_factory.return_value


class TestOtelLogger:
    def test_returns_otel_logger(self, mocker):
        mock_module = MagicMock()
        mocker.patch.dict(
            sys.modules, {"simple_log_factory_ext_otel": mock_module}
        )
        config = PoolConfig(
            conn_info="postgresql://localhost/db",
            use_otel=True,
            otel_service_name="my-service",
            otel_exporter_endpoint="http://localhost:4318",
            otel_use_http=True,
        )

        from raccoontools_db._logger import _get_logger

        result = _get_logger(config)

        mock_module.otel_log_factory.assert_called_once_with(
            service_name="my-service",
            otel_exporter_endpoint="http://localhost:4318",
            use_http_protocol=True,
        )
        assert result is mock_module.otel_log_factory.return_value

    def test_otel_missing_raises_import_error(self, mocker):
        # Ensure the module is NOT available
        mocker.patch.dict(
            sys.modules, {"simple_log_factory_ext_otel": None}
        )
        config = PoolConfig(
            conn_info="postgresql://localhost/db",
            use_otel=True,
            otel_service_name="my-service",
            otel_exporter_endpoint="http://localhost:4318",
        )

        from raccoontools_db._logger import _get_logger

        with pytest.raises(ImportError, match="raccoontools-db\\[otel\\]"):
            _get_logger(config)
