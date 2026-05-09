"""Tests for raccoontools_db.fastapi module."""

from unittest.mock import MagicMock

import pytest

from raccoontools_db.fastapi import create_lifespan
from raccoontools_db.pool import PoolConfig, get_pool


@pytest.fixture(autouse=True)
def reset_pool():
    """Ensure pool state is clean before and after each test."""
    from raccoontools_db.pool import close_pool

    close_pool()
    yield
    close_pool()


@pytest.fixture
def config():
    return PoolConfig(conn_info="postgresql://user:pass@localhost:5432/testdb")


@pytest.fixture
def mock_deps(mocker):
    """Mock pool and logger dependencies."""
    mock_pool_cls = mocker.patch("raccoontools_db.pool.ConnectionPool")
    mock_get_logger = mocker.patch("raccoontools_db.pool._get_logger")
    mock_get_logger.return_value = MagicMock()
    return mock_pool_cls


class TestCreateLifespan:
    def test_returns_callable(self, config):
        lifespan = create_lifespan(config)
        assert callable(lifespan)

    @pytest.mark.asyncio
    async def test_lifespan_opens_and_closes(self, config, mock_deps):
        mock_pool_cls = mock_deps
        lifespan = create_lifespan(config)
        mock_app = MagicMock()

        async with lifespan(mock_app):
            pool = get_pool()
            assert pool is mock_pool_cls.return_value
            mock_pool_cls.return_value.open.assert_called_once()

        # After exiting, pool should be closed
        mock_pool_cls.return_value.close.assert_called_once()
        with pytest.raises(RuntimeError):
            get_pool()

    @pytest.mark.asyncio
    async def test_lifespan_closes_on_error(self, config, mock_deps):
        mock_pool_cls = mock_deps
        lifespan = create_lifespan(config)
        mock_app = MagicMock()

        with pytest.raises(ValueError, match="app error"):
            async with lifespan(mock_app):
                raise ValueError("app error")

        # Pool should still be closed even after error
        mock_pool_cls.return_value.close.assert_called_once()
        with pytest.raises(RuntimeError):
            get_pool()
