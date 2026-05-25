"""Authentication tools for Semaphore UI.

Covers session login/logout and API token management via
``/api/auth/login``, ``/api/auth/logout``, and ``/api/user/tokens``.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def login() -> dict[str, str]:
    """Authenticate against the Semaphore server.

    Uses the credentials configured via environment variables
    (``SEMAPHORE_API_TOKEN`` for Bearer auth, or ``SEMAPHORE_USERNAME`` +
    ``SEMAPHORE_PASSWORD`` for session auth).  The session is cached by
    the client for all subsequent tool calls.

    Returns
    -------
    dict[str, str]
        ``{"status": "authenticated"}`` on success.

    Raises
    ------
    semaphore_mcp.client.SemaphoreAuthError
        If the credentials are rejected.

    Examples
    --------
    >>> await login()
    {'status': 'authenticated'}
    """
    client = get_client()
    await client.authenticate()
    return {"status": "authenticated"}


async def logout() -> dict[str, str]:
    """Invalidate the current session on the server.

    After calling this the next tool call will automatically re-authenticate.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.

    Examples
    --------
    >>> await logout()
    {'status': 'ok'}
    """
    client = get_client()
    await client.logout()
    return {"status": "ok"}


async def list_tokens() -> list[dict[str, Any]]:
    """List all API tokens for the currently authenticated user.

    Returns
    -------
    list[dict[str, Any]]
        List of API token objects with ``id``, ``created``, ``expired``,
        ``user_id``, and ``name`` fields.

    Examples
    --------
    >>> tokens = await list_tokens()
    """
    client = get_client()
    return await client.get("/api/user/tokens")


async def create_token(name: str = "") -> dict[str, Any]:
    """Create a new API token for the currently authenticated user.

    Parameters
    ----------
    name : str
        Optional label for the token (e.g. ``"my CI token"``).

    Returns
    -------
    dict[str, Any]
        The created API token object.

    Examples
    --------
    >>> token = await create_token(name="ci-pipeline")
    """
    client = get_client()
    body: dict[str, Any] = {}
    if name:
        body["name"] = name
    return await client.post("/api/user/tokens", json=body)


async def delete_token(api_token_id: str) -> dict[str, str]:
    """Expire (delete) an API token.

    Parameters
    ----------
    api_token_id : str
        The token ID to expire.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.

    Examples
    --------
    >>> await delete_token("kwofd61g93-yuqvex8efmhjkgnbxlo8mp1tin6spyhu=")
    {'status': 'ok'}
    """
    client = get_client()
    await client.delete(f"/api/user/tokens/{api_token_id}")
    return {"status": "ok"}
