"""Unit tests for :mod:`semaphore_mcp.tools.repositories`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import semaphore_mcp.state as state
from semaphore_mcp.tools import repositories


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestListRepositories:
    async def test_returns_repository_list(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [{"id": 1, "name": "demo"}]
        result = await repositories.list_repositories(1)

        mock_client.get.assert_called_once_with(
            "/api/project/1/repositories",
            params={"sort": "name", "order": "asc"},
        )
        assert result[0]["name"] == "demo"


class TestGetRepository:
    async def test_returns_repository(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"id": 2, "name": "demo"}
        result = await repositories.get_repository(1, 2)

        mock_client.get.assert_called_once_with(
            "/api/project/1/repositories/2"
        )
        assert result["id"] == 2


class TestCreateRepository:
    async def test_creates_repository(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"id": 3, "name": "myrepo"}
        result = await repositories.create_repository(
            project_id=1,
            name="myrepo",
            git_url="git@github.com:org/myrepo.git",
            git_branch="main",
            ssh_key_id=2,
        )

        mock_client.post.assert_called_once_with(
            "/api/project/1/repositories",
            json={
                "name": "myrepo",
                "project_id": 1,
                "git_url": "git@github.com:org/myrepo.git",
                "git_branch": "main",
                "ssh_key_id": 2,
            },
        )
        assert result["name"] == "myrepo"


class TestUpdateRepository:
    async def test_updates_repository(self, mock_client: AsyncMock) -> None:
        result = await repositories.update_repository(
            1, 3, "myrepo-updated", "git@github.com:org/myrepo.git", "develop", 2
        )

        call_kwargs = mock_client.put.call_args.kwargs["json"]
        assert call_kwargs["id"] == 3
        assert call_kwargs["git_branch"] == "develop"
        assert result == {"status": "ok"}


class TestDeleteRepository:
    async def test_deletes_repository(self, mock_client: AsyncMock) -> None:
        result = await repositories.delete_repository(1, 3)

        mock_client.delete.assert_called_once_with(
            "/api/project/1/repositories/3"
        )
        assert result == {"status": "ok"}
