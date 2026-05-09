"""Tests for raccoontools_db.pool module."""

from unittest.mock import MagicMock

import pytest

from raccoontools_db.pool import PoolConfig, close_pool, create_pool, get_pool


@pytest.fixture(autouse=True)
def reset_pool():
    """Ensure pool state is clean before and after each test."""
    close_pool()
    yield
    close_pool()


@pytest.fixture
def config():
    return PoolConfig(conn_info="postgresql://user:pass@localhost:5432/testdb")


@pytest.fixture
def mock_deps(mocker):
    """Mock both ConnectionPool and _get_logger to isolate pool logic."""
    mock_pool_cls = mocker.patch("raccoontools_db.pool.ConnectionPool")
    mock_get_logger = mocker.patch("raccoontools_db.pool._get_logger")
    mock_get_logger.return_value = MagicMock()
    return mock_pool_cls, mock_get_logger


class TestCreatePool:
    def test_create_pool(self, config, mock_deps):
        mock_pool_cls, _ = mock_deps

        create_pool(config)

        mock_pool_cls.assert_called_once_with(
            conninfo=config.conn_info,
            min_size=config.min_size,
            max_size=config.max_size,
        )
        mock_pool_cls.return_value.open.assert_called_once()

    def test_double_create_raises(self, config, mock_deps):
        create_pool(config)

        with pytest.raises(RuntimeError, match="already exists"):
            create_pool(config)

    def test_create_with_custom_sizes(self, mock_deps):
        mock_pool_cls, _ = mock_deps
        config = PoolConfig(
            conn_info="postgresql://localhost/db",
            min_size=5,
            max_size=20,
        )

        create_pool(config)

        mock_pool_cls.assert_called_once_with(
            conninfo=config.conn_info,
            min_size=5,
            max_size=20,
        )


class TestGetPool:
    def test_get_pool_before_create_raises(self):
        with pytest.raises(RuntimeError, match="not initialised"):
            get_pool()

    def test_get_pool_returns_pool(self, config, mock_deps):
        mock_pool_cls, _ = mock_deps

        create_pool(config)
        pool = get_pool()

        assert pool is mock_pool_cls.return_value


class TestClosePool:
    def test_close_pool(self, config, mock_deps):
        mock_pool_cls, _ = mock_deps

        create_pool(config)
        close_pool()

        mock_pool_cls.return_value.close.assert_called_once()

        with pytest.raises(RuntimeError, match="not initialised"):
            get_pool()

    def test_close_pool_idempotent(self, config, mock_deps):
        create_pool(config)
        close_pool()
        close_pool()  # Should not raise

    def test_close_pool_when_never_created(self):
        close_pool()  # Should not raise

    def test_create_after_close(self, config, mock_deps):
        mock_pool_cls, _ = mock_deps

        create_pool(config)
        close_pool()
        create_pool(config)

        pool = get_pool()
        assert pool is mock_pool_cls.return_value
