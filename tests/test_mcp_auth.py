"""Test mekanisme auth pintu depan MCP (tanpa Authentik nyata).

- ``BearerApiKeyVerifier`` diuji langsung.
- ``AuthentikProvider._extract_upstream_claims`` diuji dengan httpx di-mock:
  setiap penolakan auth HARUS memakai ``error_code`` yang valid di token endpoint
  MCP/OAuth. Memakai kode di luar set valid (mis. ``access_denied`` / ``server_error``)
  memicu Pydantic ValidationError sehingga token exchange crash tanpa response.
"""

from unittest.mock import patch

import httpx
import pytest
from mcp.server.auth.provider import TokenError

from semaphore_mcp.auth_provider import AuthentikProvider, BearerApiKeyVerifier

VALID_OAUTH_ERROR_CODES = {
    "invalid_request",
    "invalid_client",
    "invalid_grant",
    "unauthorized_client",
    "unsupported_grant_type",
    "invalid_scope",
}


class TestBearerApiKeyVerifier:
    def test_api_key_kosong_raise(self):
        with pytest.raises(ValueError, match="api_key"):
            BearerApiKeyVerifier(api_key="")

    def test_api_key_spasi_raise(self):
        with pytest.raises(ValueError, match="api_key"):
            BearerApiKeyVerifier(api_key="   ")

    @pytest.mark.asyncio
    async def test_token_cocok(self):
        verifier = BearerApiKeyVerifier(api_key="rahasia")
        result = await verifier.verify_token("rahasia")
        assert result is not None
        assert result.client_id == "api-key-client"

    @pytest.mark.asyncio
    async def test_token_salah(self):
        verifier = BearerApiKeyVerifier(api_key="rahasia")
        assert await verifier.verify_token("salah") is None

    @pytest.mark.asyncio
    async def test_token_kosong(self):
        verifier = BearerApiKeyVerifier(api_key="rahasia")
        assert await verifier.verify_token("") is None


def _provider() -> AuthentikProvider:
    return AuthentikProvider(
        authentik_base_url="https://auth.example.com",
        application_slug="semaphore-mcp",
        client_id="cid",
        client_secret="secret",
        base_url="https://mcp.example.com",
        allowed_usernames=["akadmin"],
    )


class _FakeResp:
    def __init__(self, status_code: int, data: dict) -> None:
        self.status_code = status_code
        self._data = data

    def json(self) -> dict:
        return self._data


class _FakeClient:
    """Pengganti httpx.AsyncClient: balas response palsu atau lempar exception."""

    def __init__(self, *, resp: "_FakeResp | None" = None, raise_exc: Exception | None = None):
        self._resp = resp
        self._raise = raise_exc

    async def __aenter__(self) -> "_FakeClient":
        return self

    async def __aexit__(self, *exc) -> bool:
        return False

    async def get(self, *args, **kwargs) -> "_FakeResp":
        if self._raise:
            raise self._raise
        return self._resp


async def _error_code(idp_tokens: dict, **client_kw):
    """Jalankan ``_extract_upstream_claims`` dengan httpx di-mock; balas ``.error``."""
    provider = _provider()
    with patch.object(httpx, "AsyncClient", lambda *a, **k: _FakeClient(**client_kw)):
        try:
            await provider._extract_upstream_claims(idp_tokens)
            return None
        except TokenError as exc:
            return exc.error


class TestAuthentikTokenErrorCodes:
    """Setiap penolakan auth harus memakai error_code valid (regresi crash token)."""

    @pytest.mark.asyncio
    async def test_access_token_kosong(self):
        assert await _error_code({}) in VALID_OAUTH_ERROR_CODES

    @pytest.mark.asyncio
    async def test_userinfo_tak_terjangkau(self):
        code = await _error_code({"access_token": "x"}, raise_exc=httpx.ConnectError("boom"))
        assert code in VALID_OAUTH_ERROR_CODES

    @pytest.mark.asyncio
    async def test_userinfo_non_200(self):
        code = await _error_code({"access_token": "x"}, resp=_FakeResp(403, {}))
        assert code in VALID_OAUTH_ERROR_CODES

    @pytest.mark.asyncio
    async def test_username_tidak_ada(self):
        code = await _error_code({"access_token": "x"}, resp=_FakeResp(200, {}))
        assert code in VALID_OAUTH_ERROR_CODES

    @pytest.mark.asyncio
    async def test_username_tidak_diizinkan(self):
        code = await _error_code(
            {"access_token": "x"}, resp=_FakeResp(200, {"preferred_username": "intruder"})
        )
        assert code == "unauthorized_client"

    @pytest.mark.asyncio
    async def test_username_diizinkan_lolos(self):
        provider = _provider()
        resp = _FakeResp(200, {"preferred_username": "akadmin", "email": "a@x", "sub": "1"})
        with patch.object(httpx, "AsyncClient", lambda *a, **k: _FakeClient(resp=resp)):
            claims = await provider._extract_upstream_claims({"access_token": "x"})
        assert claims is not None
        assert claims["username"] == "akadmin"
