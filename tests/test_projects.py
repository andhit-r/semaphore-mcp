"""Unit tests for :mod:`semaphore_mcp.tools.projects`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import semaphore_mcp.state as state
from semaphore_mcp.tools import projects


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestListProjects:
    async def test_returns_project_list(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [{"id": 1, "name": "homelab"}]
        result = await projects.list_projects()

        mock_client.get.assert_called_once_with("/api/projects")
        assert result[0]["name"] == "homelab"


class TestGetProject:
    async def test_returns_project(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"id": 1, "name": "homelab"}
        result = await projects.get_project(1)

        mock_client.get.assert_called_once_with("/api/project/1/")
        assert result["id"] == 1


class TestCreateProject:
    async def test_creates_project(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"id": 2, "name": "dev"}
        result = await projects.create_project("dev")

        mock_client.post.assert_called_once_with(
            "/api/projects",
            json={"name": "dev", "alert": False, "max_parallel_tasks": 0},
        )
        assert result["name"] == "dev"


class TestUpdateProject:
    async def test_updates_project(self, mock_client: AsyncMock) -> None:
        result = await projects.update_project(1, "homelab-updated")

        mock_client.put.assert_called_once_with(
            "/api/project/1/",
            json={
                "id": 1,
                "name": "homelab-updated",
                "alert": False,
                "max_parallel_tasks": 0,
            },
        )
        assert result == {"status": "ok"}


class TestDeleteProject:
    async def test_deletes_project(self, mock_client: AsyncMock) -> None:
        result = await projects.delete_project(1)

        mock_client.delete.assert_called_once_with("/api/project/1/")
        assert result == {"status": "ok"}


class TestGetProjectRole:
    async def test_returns_role(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"role": "owner", "permissions": 255}
        result = await projects.get_project_role(1)

        mock_client.get.assert_called_once_with("/api/project/1/role")
        assert result["role"] == "owner"


class TestListProjectUsers:
    async def test_returns_users(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [{"id": 1, "role": "owner"}]
        result = await projects.list_project_users(1)

        mock_client.get.assert_called_once_with(
            "/api/project/1/users",
            params={"sort": "name", "order": "asc"},
        )
        assert result[0]["role"] == "owner"


class TestAddProjectUser:
    async def test_adds_user(self, mock_client: AsyncMock) -> None:
        result = await projects.add_project_user(1, 2, "manager")

        mock_client.post.assert_called_once_with(
            "/api/project/1/users",
            json={"user_id": 2, "role": "manager"},
        )
        assert result == {"status": "ok"}


class TestRemoveProjectUser:
    async def test_removes_user(self, mock_client: AsyncMock) -> None:
        result = await projects.remove_project_user(1, 2)

        mock_client.delete.assert_called_once_with("/api/project/1/users/2")
        assert result == {"status": "ok"}


class TestUpdateProjectUserRole:
    async def test_updates_role(self, mock_client: AsyncMock) -> None:
        result = await projects.update_project_user_role(1, 2, "task_runner")

        mock_client.put.assert_called_once_with(
            "/api/project/1/users/2",
            json={"role": "task_runner"},
        )
        assert result == {"status": "ok"}


class TestProjectViews:
    async def test_list_views(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [{"id": 10, "title": "Build"}]
        result = await projects.list_project_views(1)

        mock_client.get.assert_called_once_with("/api/project/1/views")
        assert result[0]["title"] == "Build"

    async def test_create_view(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"id": 11, "title": "Deploy"}
        result = await projects.create_project_view(1, "Deploy")

        mock_client.post.assert_called_once_with(
            "/api/project/1/views",
            json={"title": "Deploy", "project_id": 1, "position": 0},
        )
        assert result["title"] == "Deploy"

    async def test_delete_view(self, mock_client: AsyncMock) -> None:
        result = await projects.delete_project_view(1, 10)

        mock_client.delete.assert_called_once_with("/api/project/1/views/10")
        assert result == {"status": "ok"}
