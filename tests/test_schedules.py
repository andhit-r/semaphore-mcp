"""Unit tests for :mod:`semaphore_mcp.tools.schedules`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import semaphore_mcp.state as state
from semaphore_mcp.tools import schedules


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestGetSchedule:
    async def test_returns_schedule(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {
            "id": 9,
            "cron_format": "0 2 * * *",
            "active": True,
        }
        result = await schedules.get_schedule(1, 9)

        mock_client.get.assert_called_once_with("/api/project/1/schedules/9")
        assert result["cron_format"] == "0 2 * * *"


class TestCreateSchedule:
    async def test_creates_schedule(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"id": 10, "cron_format": "0 2 * * *"}
        result = await schedules.create_schedule(
            project_id=1,
            template_id=7,
            cron_format="0 2 * * *",
            name="nightly",
        )

        mock_client.post.assert_called_once_with(
            "/api/project/1/schedules",
            json={
                "project_id": 1,
                "template_id": 7,
                "cron_format": "0 2 * * *",
                "name": "nightly",
                "active": True,
            },
        )
        assert result["id"] == 10


class TestUpdateSchedule:
    async def test_updates_schedule(self, mock_client: AsyncMock) -> None:
        result = await schedules.update_schedule(
            project_id=1,
            schedule_id=10,
            template_id=7,
            cron_format="0 3 * * *",
            name="nightly-updated",
            active=False,
        )

        mock_client.put.assert_called_once_with(
            "/api/project/1/schedules/10",
            json={
                "id": 10,
                "project_id": 1,
                "template_id": 7,
                "cron_format": "0 3 * * *",
                "name": "nightly-updated",
                "active": False,
            },
        )
        assert result == {"status": "ok"}


class TestDeleteSchedule:
    async def test_deletes_schedule(self, mock_client: AsyncMock) -> None:
        result = await schedules.delete_schedule(1, 10)

        mock_client.delete.assert_called_once_with("/api/project/1/schedules/10")
        assert result == {"status": "ok"}
