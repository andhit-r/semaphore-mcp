"""Unit tests for :mod:`semaphore_mcp.tools.system`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import semaphore_mcp.state as state
from semaphore_mcp.tools import system


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestPing:
    async def test_calls_ping_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = "pong"
        result = await system.ping()

        mock_client.get.assert_called_once_with("/api/ping")
        assert result == "pong"


class TestGetInfo:
    async def test_returns_info(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {
            "version": "2.10.0",
            "ansible": "2.16.0",
        }
        result = await system.get_info()

        mock_client.get.assert_called_once_with("/api/info")
        assert result["version"] == "2.10.0"


class TestListEvents:
    async def test_calls_events_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [{"id": 1, "description": "Project created"}]
        result = await system.list_events()

        mock_client.get.assert_called_once_with("/api/events")
        assert result[0]["description"] == "Project created"

    async def test_returns_empty_list_when_no_events(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = []
        result = await system.list_events()
        assert result == []


class TestListLastEvents:
    async def test_calls_last_events_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [{"id": 99}]
        result = await system.list_last_events()

        mock_client.get.assert_called_once_with("/api/events/last")
        assert result[0]["id"] == 99


class TestListApps:
    async def test_calls_apps_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [
            {"id": "ansible", "title": "Ansible"},
            {"id": "terraform", "title": "Terraform"},
        ]
        result = await system.list_apps()

        mock_client.get.assert_called_once_with("/api/apps")
        assert len(result) == 2
        assert result[0]["id"] == "ansible"
