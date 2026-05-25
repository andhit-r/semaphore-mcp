"""Unit tests for :mod:`semaphore_mcp.tools.keys`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import semaphore_mcp.state as state
from semaphore_mcp.tools import keys


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestListKeys:
    async def test_returns_key_list(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [{"id": 1, "name": "None", "type": "none"}]
        result = await keys.list_keys(1)

        mock_client.get.assert_called_once_with(
            "/api/project/1/keys",
            params={"sort": "name", "order": "asc"},
        )
        assert result[0]["type"] == "none"


class TestCreateKey:
    async def test_creates_none_key(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"id": 2, "name": "Empty", "type": "none"}
        result = await keys.create_key(1, "Empty", "none")

        mock_client.post.assert_called_once_with(
            "/api/project/1/keys",
            json={"name": "Empty", "type": "none", "project_id": 1},
        )
        assert result["type"] == "none"

    async def test_creates_ssh_key(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"id": 3, "type": "ssh"}
        result = await keys.create_key(
            1, "deploy", "ssh", login="ubuntu", private_key="-----BEGIN"
        )

        call_kwargs = mock_client.post.call_args.kwargs["json"]
        assert call_kwargs["type"] == "ssh"
        assert call_kwargs["ssh"]["login"] == "ubuntu"
        assert result["type"] == "ssh"

    async def test_creates_login_password_key(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"id": 4, "type": "login_password"}
        result = await keys.create_key(
            1, "vault", "login_password", login="user", password="secret"
        )

        call_kwargs = mock_client.post.call_args.kwargs["json"]
        assert call_kwargs["login_password"]["login"] == "user"
        assert result["type"] == "login_password"


class TestUpdateKey:
    async def test_updates_key(self, mock_client: AsyncMock) -> None:
        result = await keys.update_key(1, 2, "Empty-Renamed", "none")

        mock_client.put.assert_called_once_with(
            "/api/project/1/keys/2",
            json={"id": 2, "name": "Empty-Renamed", "type": "none", "project_id": 1},
        )
        assert result == {"status": "ok"}


class TestDeleteKey:
    async def test_deletes_key(self, mock_client: AsyncMock) -> None:
        result = await keys.delete_key(1, 2)

        mock_client.delete.assert_called_once_with("/api/project/1/keys/2")
        assert result == {"status": "ok"}
