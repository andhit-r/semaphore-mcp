"""Unit tests for :mod:`semaphore_mcp.tools.environment`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import semaphore_mcp.state as state
from semaphore_mcp.tools import environment


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestListEnvironments:
    async def test_returns_environment_list(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [{"id": 1, "name": "Empty"}]
        result = await environment.list_environments(1)

        mock_client.get.assert_called_once_with(
            "/api/project/1/environment",
            params={"sort": "name", "order": "asc"},
        )
        assert result[0]["name"] == "Empty"


class TestGetEnvironment:
    async def test_returns_environment(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"id": 6, "name": "Empty", "json": "{}"}
        result = await environment.get_environment(1, 6)

        mock_client.get.assert_called_once_with("/api/project/1/environment/6")
        assert result["id"] == 6


class TestCreateEnvironment:
    async def test_creates_environment(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"id": 7, "name": "prod"}
        result = await environment.create_environment(
            project_id=1,
            name="prod",
            env_json='{"DEPLOY_ENV": "production"}',
        )

        mock_client.post.assert_called_once_with(
            "/api/project/1/environment",
            json={
                "name": "prod",
                "project_id": 1,
                "json": '{"DEPLOY_ENV": "production"}',
                "env": "",
                "password": "",
            },
        )
        assert result["name"] == "prod"


class TestUpdateEnvironment:
    async def test_updates_environment(self, mock_client: AsyncMock) -> None:
        result = await environment.update_environment(
            project_id=1,
            environment_id=7,
            name="prod-updated",
            env_json="{}",
        )

        call_kwargs = mock_client.put.call_args.kwargs["json"]
        assert call_kwargs["id"] == 7
        assert call_kwargs["name"] == "prod-updated"
        assert result == {"status": "ok"}


class TestDeleteEnvironment:
    async def test_deletes_environment(self, mock_client: AsyncMock) -> None:
        result = await environment.delete_environment(1, 7)

        mock_client.delete.assert_called_once_with("/api/project/1/environment/7")
        assert result == {"status": "ok"}
