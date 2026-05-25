"""Shared pytest fixtures for semaphore-mcp tests."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
import respx

from semaphore_mcp.client import SemaphoreClient
from semaphore_mcp.config import SemaphoreConfig

BASE_URL = "http://semaphore-test:3000"


@pytest.fixture()
def semaphore_config() -> SemaphoreConfig:
    """Minimal :class:`SemaphoreConfig` pointed at the test URL."""
    return SemaphoreConfig(
        url=BASE_URL,
        api_token="test-api-token",  # type: ignore[arg-type]
        username="admin",
        password="changeme",  # type: ignore[arg-type]
        timeout=5.0,
        verify_ssl=False,
        transport="stdio",
    )


@pytest.fixture()
def real_client(semaphore_config: SemaphoreConfig) -> SemaphoreClient:
    """A :class:`SemaphoreClient` wired to the test config (no mocks)."""
    return SemaphoreClient(semaphore_config)


@pytest.fixture()
def mock_client() -> AsyncMock:
    """AsyncMock replacement for :class:`SemaphoreClient`.

    Inject this via :func:`semaphore_mcp.state.set_client` inside each
    test that exercises a tool function.
    """
    client = AsyncMock(spec=SemaphoreClient)
    client.get.return_value = {}
    client.post.return_value = {}
    client.put.return_value = None
    client.delete.return_value = None
    return client


@pytest.fixture()
def respx_mock() -> respx.MockRouter:
    """Active respx mock router for httpx-level mocking."""
    with respx.mock(base_url=BASE_URL, assert_all_called=False) as router:
        yield router
