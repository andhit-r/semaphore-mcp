"""Async HTTP client for the Semaphore UI REST API.

Supports two authentication modes:

* **API token** (preferred): set ``SEMAPHORE_API_TOKEN`` — the token is
  sent as ``Authorization: Bearer <token>`` on every request.
* **Session cookie**: set ``SEMAPHORE_USERNAME`` + ``SEMAPHORE_PASSWORD`` —
  the client calls ``POST /api/auth/login`` and the resulting session cookie
  is cached by httpx for all subsequent calls.

A ``401`` or ``403`` response triggers a single re-authentication attempt.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from .config import SemaphoreConfig

logger = logging.getLogger(__name__)


class SemaphoreError(Exception):
    """Base exception for Semaphore API errors.

    Parameters
    ----------
    message : str
        Human-readable error description.
    status_code : int | None
        HTTP status code returned by the API, if available.
    """

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class SemaphoreAuthError(SemaphoreError):
    """Raised when authentication fails (HTTP 401/403)."""


class SemaphoreNotFoundError(SemaphoreError):
    """Raised when a requested resource does not exist (HTTP 404)."""


class SemaphoreClient:
    """Async HTTP client for the Semaphore UI REST API.

    Parameters
    ----------
    config : SemaphoreConfig
        Server connection configuration.

    Examples
    --------
    >>> async with SemaphoreClient(config) as client:
    ...     projects = await client.get("/api/projects")
    """

    def __init__(self, config: SemaphoreConfig) -> None:
        self._config = config
        self._authenticated = False
        self._http = httpx.AsyncClient(
            base_url=config.url,
            timeout=config.timeout,
            verify=config.verify_ssl,
            follow_redirects=True,
        )
        # Pre-configure Bearer token if api_token is set
        if config.api_token:
            self._http.headers.update(
                {"Authorization": f"Bearer {config.api_token.get_secret_value()}"}
            )
            self._authenticated = True

    async def __aenter__(self) -> SemaphoreClient:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.aclose()

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    async def authenticate(self) -> None:
        """Authenticate against the Semaphore server.

        Uses Bearer token auth when ``api_token`` is configured; otherwise
        performs a session login with ``username`` / ``password``.

        Raises
        ------
        SemaphoreAuthError
            If the credentials are rejected.
        """
        if self._config.api_token:
            logger.debug("Using API token authentication")
            self._http.headers.update(
                {"Authorization": (f"Bearer {self._config.api_token.get_secret_value()}")}
            )
            self._authenticated = True
            return

        logger.debug("Authenticating as %s (session)", self._config.username)
        response = await self._http.post(
            "/api/auth/login",
            json={
                "auth": self._config.username,
                "password": self._config.password.get_secret_value(),
            },
        )
        if response.status_code != 204:
            raise SemaphoreAuthError(
                f"Authentication failed ({response.status_code}): {response.text}",
                status_code=response.status_code,
            )
        self._authenticated = True
        logger.debug("Session authentication successful")

    async def logout(self) -> None:
        """Invalidate the current session on the server.

        No-op if the client has not yet authenticated.
        """
        if self._authenticated:
            try:
                await self._http.post("/api/auth/logout")
            except Exception:  # noqa: BLE001
                logger.warning("Logout request failed", exc_info=True)
            finally:
                self._authenticated = False
                self._http.cookies.clear()
                self._http.headers.pop("Authorization", None)

    # ------------------------------------------------------------------
    # Request helpers
    # ------------------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute an authenticated HTTP request.

        Automatically authenticates on first call and retries once on
        ``401``/``403`` responses.

        Parameters
        ----------
        method : str
            HTTP method (``GET``, ``POST``, etc.).
        path : str
            API path (e.g. ``/api/projects``).
        **kwargs : Any
            Forwarded to :meth:`httpx.AsyncClient.request`.

        Returns
        -------
        httpx.Response
            The HTTP response object.

        Raises
        ------
        SemaphoreAuthError
            On persistent 401/403 responses.
        SemaphoreNotFoundError
            On 404 responses.
        SemaphoreError
            On any other 4xx/5xx response.
        """
        if not self._authenticated:
            await self.authenticate()

        response = await self._http.request(method, path, **kwargs)

        if response.status_code in (401, 403):
            logger.debug(
                "Session may be expired (HTTP %s), re-authenticating",
                response.status_code,
            )
            await self.authenticate()
            response = await self._http.request(method, path, **kwargs)

        self._raise_for_status(response)
        return response

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.status_code in (401, 403):
            raise SemaphoreAuthError("Unauthorized", status_code=response.status_code)
        if response.status_code == 404:
            raise SemaphoreNotFoundError("Resource not found", status_code=404)
        if response.status_code >= 400:
            raise SemaphoreError(
                f"API error {response.status_code}: {response.text}",
                status_code=response.status_code,
            )

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    async def get(self, path: str, **kwargs: Any) -> Any:
        """Perform a GET request and return the decoded JSON body.

        Parameters
        ----------
        path : str
            API path.
        **kwargs : Any
            Forwarded to :meth:`_request`.

        Returns
        -------
        Any
            Decoded JSON response (dict or list).
        """
        response = await self._request("GET", path, **kwargs)
        return response.json()

    async def post(self, path: str, **kwargs: Any) -> Any:
        """Perform a POST request and return the decoded JSON body.

        Parameters
        ----------
        path : str
            API path.
        **kwargs : Any
            Forwarded to :meth:`_request`.

        Returns
        -------
        Any
            Decoded JSON response, or ``None`` for 204 responses.
        """
        response = await self._request("POST", path, **kwargs)
        if response.status_code == 204:
            return None
        return response.json()

    async def put(self, path: str, **kwargs: Any) -> None:
        """Perform a PUT request (no response body expected).

        Parameters
        ----------
        path : str
            API path.
        **kwargs : Any
            Forwarded to :meth:`_request`.
        """
        await self._request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> None:
        """Perform a DELETE request (no response body expected).

        Parameters
        ----------
        path : str
            API path.
        **kwargs : Any
            Forwarded to :meth:`_request`.
        """
        await self._request("DELETE", path, **kwargs)
