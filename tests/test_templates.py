"""Unit tests for :mod:`semaphore_mcp.tools.templates`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import semaphore_mcp.state as state
from semaphore_mcp.tools import templates


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestListTemplates:
    async def test_returns_template_list(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [{"id": 7, "name": "Deploy"}]
        result = await templates.list_templates(1)

        mock_client.get.assert_called_once_with(
            "/api/project/1/templates",
            params={"sort": "name", "order": "asc"},
        )
        assert result[0]["name"] == "Deploy"


class TestGetTemplate:
    async def test_returns_template(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"id": 7, "playbook": "deploy.yml"}
        result = await templates.get_template(1, 7)

        mock_client.get.assert_called_once_with("/api/project/1/templates/7")
        assert result["playbook"] == "deploy.yml"


class TestCreateTemplate:
    async def test_creates_template(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"id": 8, "name": "Deploy"}
        result = await templates.create_template(
            project_id=1,
            name="Deploy",
            playbook="deploy.yml",
            inventory_id=5,
            repository_id=4,
            environment_id=6,
        )

        call_kwargs = mock_client.post.call_args.kwargs["json"]
        assert call_kwargs["playbook"] == "deploy.yml"
        assert call_kwargs["inventory_id"] == 5
        assert call_kwargs["app"] == "ansible"
        assert result["name"] == "Deploy"

    async def test_creates_template_with_ssh_key(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"id": 9}
        await templates.create_template(
            project_id=1,
            name="Secure",
            playbook="site.yml",
            inventory_id=5,
            repository_id=4,
            environment_id=6,
            ssh_key_id=3,
        )

        call_kwargs = mock_client.post.call_args.kwargs["json"]
        assert call_kwargs["ssh_key_id"] == 3

    async def test_optional_ssh_key_omitted_when_zero(
        self, mock_client: AsyncMock
    ) -> None:
        mock_client.post.return_value = {"id": 10}
        await templates.create_template(
            project_id=1,
            name="Basic",
            playbook="site.yml",
            inventory_id=5,
            repository_id=4,
            environment_id=6,
        )

        call_kwargs = mock_client.post.call_args.kwargs["json"]
        assert "ssh_key_id" not in call_kwargs


class TestDeleteTemplate:
    async def test_deletes_template(self, mock_client: AsyncMock) -> None:
        result = await templates.delete_template(1, 7)

        mock_client.delete.assert_called_once_with("/api/project/1/templates/7")
        assert result == {"status": "ok"}


class TestStopAllTemplateTasks:
    async def test_stops_all_tasks(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = None
        result = await templates.stop_all_template_tasks(1, 7)

        mock_client.post.assert_called_once_with(
            "/api/project/1/templates/7/stop_all_tasks",
            json={"force": False},
        )
        assert result == {"status": "ok"}

    async def test_force_stop(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = None
        result = await templates.stop_all_template_tasks(1, 7, force=True)

        call_kwargs = mock_client.post.call_args.kwargs["json"]
        assert call_kwargs["force"] is True
        assert result == {"status": "ok"}
