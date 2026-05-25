"""Unit tests for :mod:`semaphore_mcp.tools.tasks`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import semaphore_mcp.state as state
from semaphore_mcp.tools import tasks


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestListTasks:
    async def test_returns_task_list(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [{"id": 23, "status": "success"}]
        result = await tasks.list_tasks(1)

        mock_client.get.assert_called_once_with("/api/project/1/tasks")
        assert result[0]["id"] == 23


class TestListLastTasks:
    async def test_returns_last_200_tasks(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [{"id": 23}]
        result = await tasks.list_last_tasks(1)

        mock_client.get.assert_called_once_with("/api/project/1/tasks/last")
        assert len(result) == 1


class TestGetTask:
    async def test_returns_task(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"id": 23, "status": "running"}
        result = await tasks.get_task(1, 23)

        mock_client.get.assert_called_once_with("/api/project/1/tasks/23")
        assert result["status"] == "running"


class TestStartTask:
    async def test_starts_task_minimal(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"id": 24, "status": "waiting"}
        result = await tasks.start_task(project_id=1, template_id=7)

        mock_client.post.assert_called_once_with(
            "/api/project/1/tasks",
            json={
                "template_id": 7,
                "debug": False,
                "dry_run": False,
                "diff": False,
            },
        )
        assert result["id"] == 24

    async def test_starts_task_with_options(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"id": 25}
        await tasks.start_task(
            project_id=1,
            template_id=7,
            debug=True,
            limit="webservers",
            message="manual deploy",
            git_branch="hotfix",
        )

        call_kwargs = mock_client.post.call_args.kwargs["json"]
        assert call_kwargs["debug"] is True
        assert call_kwargs["limit"] == "webservers"
        assert call_kwargs["message"] == "manual deploy"
        assert call_kwargs["git_branch"] == "hotfix"

    async def test_empty_optional_fields_omitted(
        self, mock_client: AsyncMock
    ) -> None:
        mock_client.post.return_value = {"id": 26}
        await tasks.start_task(project_id=1, template_id=7)

        call_kwargs = mock_client.post.call_args.kwargs["json"]
        assert "limit" not in call_kwargs
        assert "git_branch" not in call_kwargs


class TestStopTask:
    async def test_stops_task(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = None
        result = await tasks.stop_task(1, 23)

        mock_client.post.assert_called_once_with(
            "/api/project/1/tasks/23/stop",
            json={"force": False},
        )
        assert result == {"status": "ok"}

    async def test_force_stop_task(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = None
        result = await tasks.stop_task(1, 23, force=True)

        call_kwargs = mock_client.post.call_args.kwargs["json"]
        assert call_kwargs["force"] is True
        assert result == {"status": "ok"}


class TestDeleteTask:
    async def test_deletes_task(self, mock_client: AsyncMock) -> None:
        result = await tasks.delete_task(1, 23)

        mock_client.delete.assert_called_once_with("/api/project/1/tasks/23")
        assert result == {"status": "ok"}


class TestGetTaskOutput:
    async def test_returns_output(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [
            {"task_id": 23, "time": "2024-01-01T00:00:00Z", "output": "ok"}
        ]
        result = await tasks.get_task_output(1, 23)

        mock_client.get.assert_called_once_with(
            "/api/project/1/tasks/23/output"
        )
        assert result[0]["output"] == "ok"
