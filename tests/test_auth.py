"""Unit tests for :mod:`semaphore_mcp.tools.auth`."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import semaphore_mcp.state as state
from semaphore_mcp.tools import auth


@pytest.fixture(autouse=True)
def inject_mock_client(mock_client: AsyncMock) -> None:
    state.set_client(mock_client)
    yield
    state.set_client(None)


class TestLogin:
    async def test_calls_authenticate_on_client(
        self, mock_client: AsyncMock
    ) -> None:
        result = await auth.login()

        mock_client.authenticate.assert_called_once()
        assert result == {"status": "authenticated"}


class TestLogout:
    async def test_calls_logout_on_client(self, mock_client: AsyncMock) -> None:
        result = await auth.logout()

        mock_client.logout.assert_called_once()
        assert result == {"status": "ok"}


class TestListTokens:
    async def test_get_user_tokens(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = [{"id": "tok123", "expired": False}]
        result = await auth.list_tokens()

        mock_client.get.assert_called_once_with("/api/user/tokens")
        assert result[0]["id"] == "tok123"


class TestCreateToken:
    async def test_create_token_with_name(self, mock_client: AsyncMock) -> None:
        mock_client.post.return_value = {"id": "newtok", "name": "ci"}
        result = await auth.create_token(name="ci")

        mock_client.post.assert_called_once_with(
            "/api/user/tokens", json={"name": "ci"}
        )
        assert result["id"] == "newtok"

    async def test_create_token_without_name(
        self, mock_client: AsyncMock
    ) -> None:
        mock_client.post.return_value = {"id": "newtok"}
        result = await auth.create_token()

        mock_client.post.assert_called_once_with("/api/user/tokens", json={})
        assert result["id"] == "newtok"


class TestDeleteToken:
    async def test_delete_token(self, mock_client: AsyncMock) -> None:
        result = await auth.delete_token("tok123")

        mock_client.delete.assert_called_once_with("/api/user/tokens/tok123")
        assert result == {"status": "ok"}
