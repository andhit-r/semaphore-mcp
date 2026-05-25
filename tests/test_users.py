"""Unit tests for :mod:`semaphore_mcp.tools.users`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import semaphore_mcp.state as state
from semaphore_mcp.tools import users


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestGetCurrentUser:
    async def test_returns_current_user(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"id": 1, "username": "admin"}
        result = await users.get_current_user()

        mock_client.get.assert_called_once_with("/api/user/")
        assert result["username"] == "admin"


class TestListUsers:
    async def test_returns_user_list(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [{"id": 1}, {"id": 2}]
        result = await users.list_users()

        mock_client.get.assert_called_once_with("/api/users")
        assert len(result) == 2


class TestGetUser:
    async def test_returns_user(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"id": 2, "username": "alice"}
        result = await users.get_user(2)

        mock_client.get.assert_called_once_with("/api/users/2/")
        assert result["username"] == "alice"


class TestCreateUser:
    async def test_creates_user(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"id": 3, "username": "bob"}
        result = await users.create_user(
            name="Bob", username="bob", email="bob@example.com", password="p4ss"
        )

        mock_client.post.assert_called_once_with(
            "/api/users",
            json={
                "name": "Bob",
                "username": "bob",
                "email": "bob@example.com",
                "password": "p4ss",
                "admin": False,
                "alert": False,
            },
        )
        assert result["username"] == "bob"

    async def test_creates_admin_user(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"id": 4, "admin": True}
        await users.create_user(
            name="Admin",
            username="superadmin",
            email="admin@example.com",
            password="s3cret",
            admin=True,
        )

        call_json = mock_client.post.call_args.kwargs["json"]
        assert call_json["admin"] is True


class TestUpdateUser:
    async def test_updates_user(self, mock_client: AsyncMock) -> None:
        result = await users.update_user(
            user_id=3,
            name="Bob Updated",
            username="bob",
            email="bob@example.com",
        )

        mock_client.put.assert_called_once_with(
            "/api/users/3/",
            json={
                "name": "Bob Updated",
                "username": "bob",
                "email": "bob@example.com",
                "admin": False,
                "alert": False,
            },
        )
        assert result == {"status": "ok"}


class TestDeleteUser:
    async def test_deletes_user(self, mock_client: AsyncMock) -> None:
        result = await users.delete_user(3)

        mock_client.delete.assert_called_once_with("/api/users/3/")
        assert result == {"status": "ok"}


class TestUpdateUserPassword:
    async def test_updates_password(self, mock_client: AsyncMock) -> None:
        result = await users.update_user_password(3, "newpassword")

        mock_client.post.assert_called_once_with(
            "/api/users/3/password",
            json={"password": "newpassword"},
        )
        assert result == {"status": "ok"}
