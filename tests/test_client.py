"""Unit tests for :class:`~semaphore_mcp.client.SemaphoreClient`."""

from __future__ import annotations

import httpx
import pytest
import respx

from semaphore_mcp.client import (
    SemaphoreAuthError,
    SemaphoreClient,
    SemaphoreError,
    SemaphoreNotFoundError,
)
from semaphore_mcp.config import SemaphoreConfig

BASE_URL = "http://semaphore-test:3000"


@pytest.fixture()
def api_token_config() -> SemaphoreConfig:
    return SemaphoreConfig(
        url=BASE_URL,
        api_token="test-api-token",  # type: ignore[arg-type]
        timeout=5.0,
        verify_ssl=False,
        transport="stdio",
    )


@pytest.fixture()
def session_config() -> SemaphoreConfig:
    return SemaphoreConfig(
        url=BASE_URL,
        username="admin",
        password="changeme",  # type: ignore[arg-type]
        timeout=5.0,
        verify_ssl=False,
        transport="stdio",
    )


class TestApiTokenAuth:
    def test_bearer_header_set_on_init(self, api_token_config: SemaphoreConfig) -> None:
        client = SemaphoreClient(api_token_config)
        assert client._http.headers.get("Authorization") == "Bearer test-api-token"
        assert client._authenticated is True

    async def test_authenticate_refreshes_header(self, api_token_config: SemaphoreConfig) -> None:
        client = SemaphoreClient(api_token_config)
        await client.authenticate()
        assert "Bearer test-api-token" in client._http.headers.get("Authorization", "")


class TestSessionAuth:
    async def test_authenticate_posts_to_login(self, session_config: SemaphoreConfig) -> None:
        with respx.mock(base_url=BASE_URL) as router:
            router.post("/api/auth/login").mock(return_value=httpx.Response(204))
            client = SemaphoreClient(session_config)
            await client.authenticate()
            assert client._authenticated is True

    async def test_authenticate_raises_on_failure(self, session_config: SemaphoreConfig) -> None:
        with respx.mock(base_url=BASE_URL) as router:
            router.post("/api/auth/login").mock(
                return_value=httpx.Response(400, json={"error": "invalid credentials"})
            )
            client = SemaphoreClient(session_config)
            with pytest.raises(SemaphoreAuthError):
                await client.authenticate()


class TestRequestHelpers:
    async def test_get_returns_json(self, api_token_config: SemaphoreConfig) -> None:
        with respx.mock(base_url=BASE_URL) as router:
            router.get("/api/projects").mock(return_value=httpx.Response(200, json=[{"id": 1}]))
            client = SemaphoreClient(api_token_config)
            result = await client.get("/api/projects")
            assert result == [{"id": 1}]

    async def test_post_returns_json(self, api_token_config: SemaphoreConfig) -> None:
        with respx.mock(base_url=BASE_URL) as router:
            router.post("/api/projects").mock(
                return_value=httpx.Response(201, json={"id": 2, "name": "test"})
            )
            client = SemaphoreClient(api_token_config)
            result = await client.post("/api/projects", json={"name": "test"})
            assert result == {"id": 2, "name": "test"}

    async def test_post_returns_none_on_204(self, api_token_config: SemaphoreConfig) -> None:
        with respx.mock(base_url=BASE_URL) as router:
            router.post("/api/auth/logout").mock(return_value=httpx.Response(204))
            client = SemaphoreClient(api_token_config)
            result = await client.post("/api/auth/logout")
            assert result is None

    async def test_delete_raises_not_found_on_404(self, api_token_config: SemaphoreConfig) -> None:
        with respx.mock(base_url=BASE_URL) as router:
            router.delete("/api/project/99/").mock(return_value=httpx.Response(404))
            client = SemaphoreClient(api_token_config)
            with pytest.raises(SemaphoreNotFoundError):
                await client.delete("/api/project/99/")

    async def test_raises_semaphore_error_on_500(self, api_token_config: SemaphoreConfig) -> None:
        with respx.mock(base_url=BASE_URL) as router:
            router.get("/api/projects").mock(
                return_value=httpx.Response(500, text="Internal Server Error")
            )
            client = SemaphoreClient(api_token_config)
            with pytest.raises(SemaphoreError) as exc_info:
                await client.get("/api/projects")
            assert exc_info.value.status_code == 500

    async def test_reauth_on_401(self, api_token_config: SemaphoreConfig) -> None:
        call_count = 0

        with respx.mock(base_url=BASE_URL) as router:

            def side_effect(request: httpx.Request) -> httpx.Response:
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return httpx.Response(401)
                return httpx.Response(200, json=[])

            router.get("/api/projects").mock(side_effect=side_effect)
            client = SemaphoreClient(api_token_config)
            result = await client.get("/api/projects")
            assert result == []
            assert call_count == 2


class TestLogout:
    async def test_logout_clears_auth_state(self, session_config: SemaphoreConfig) -> None:
        with respx.mock(base_url=BASE_URL) as router:
            router.post("/api/auth/login").mock(return_value=httpx.Response(204))
            router.post("/api/auth/logout").mock(return_value=httpx.Response(204))
            client = SemaphoreClient(session_config)
            await client.authenticate()
            assert client._authenticated is True
            await client.logout()
            assert client._authenticated is False

    async def test_logout_noop_when_not_authenticated(
        self, session_config: SemaphoreConfig
    ) -> None:
        client = SemaphoreClient(session_config)
        assert client._authenticated is False
        # Should not raise
        await client.logout()
