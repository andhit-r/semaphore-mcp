"""Unit tests for :mod:`semaphore_mcp.tools.inventory`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import semaphore_mcp.state as state
from semaphore_mcp.tools import inventory


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestListInventory:
    async def test_returns_inventory_list(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [{"id": 1, "name": "prod", "type": "static"}]
        result = await inventory.list_inventory(1)

        mock_client.get.assert_called_once_with(
            "/api/project/1/inventory",
            params={"sort": "name", "order": "asc"},
        )
        assert result[0]["name"] == "prod"


class TestGetInventory:
    async def test_returns_inventory(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"id": 5, "name": "prod"}
        result = await inventory.get_inventory(1, 5)

        mock_client.get.assert_called_once_with("/api/project/1/inventory/5")
        assert result["id"] == 5


class TestCreateInventory:
    async def test_creates_static_inventory(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"id": 6, "name": "prod", "type": "static"}
        result = await inventory.create_inventory(
            project_id=1,
            name="prod",
            inventory_type="static",
            inventory="[servers]\n192.168.1.1",
            ssh_key_id=3,
        )

        call_kwargs = mock_client.post.call_args.kwargs["json"]
        assert call_kwargs["type"] == "static"
        assert call_kwargs["ssh_key_id"] == 3
        assert result["type"] == "static"

    async def test_creates_file_inventory_without_optional_ids(
        self, mock_client: AsyncMock
    ) -> None:
        mock_client.post.return_value = {"id": 7, "type": "file"}
        result = await inventory.create_inventory(
            project_id=1, name="dev", inventory_type="file"
        )

        call_kwargs = mock_client.post.call_args.kwargs["json"]
        assert "ssh_key_id" not in call_kwargs
        assert result["type"] == "file"


class TestUpdateInventory:
    async def test_updates_inventory(self, mock_client: AsyncMock) -> None:
        result = await inventory.update_inventory(
            project_id=1,
            inventory_id=5,
            name="prod-updated",
            inventory_type="static",
            inventory="[servers]\n10.0.0.1",
            ssh_key_id=3,
        )

        call_kwargs = mock_client.put.call_args.kwargs["json"]
        assert call_kwargs["id"] == 5
        assert call_kwargs["name"] == "prod-updated"
        assert call_kwargs["ssh_key_id"] == 3
        assert result == {"status": "ok"}

    async def test_update_inventory_without_keys(self, mock_client: AsyncMock) -> None:
        await inventory.update_inventory(
            project_id=1,
            inventory_id=5,
            name="dev",
            inventory_type="file",
        )

        call_kwargs = mock_client.put.call_args.kwargs["json"]
        assert "ssh_key_id" not in call_kwargs
        assert "become_key_id" not in call_kwargs


class TestDeleteInventory:
    async def test_deletes_inventory(self, mock_client: AsyncMock) -> None:
        result = await inventory.delete_inventory(1, 5)

        mock_client.delete.assert_called_once_with("/api/project/1/inventory/5")
        assert result == {"status": "ok"}
