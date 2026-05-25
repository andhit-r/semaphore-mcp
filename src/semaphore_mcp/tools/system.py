"""System-level tools for Semaphore UI.

Covers ``/api/ping``, ``/api/info``, ``/api/events``, and ``/api/apps``
endpoints.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def ping() -> str:
    """Ping the Semaphore server.

    Returns
    -------
    str
        ``"pong"`` on success.

    Examples
    --------
    >>> await ping()
    'pong'
    """
    client = get_client()
    return await client.get("/api/ping")


async def get_info() -> dict[str, Any]:
    """Fetch information about the Semaphore instance.

    Returns
    -------
    dict[str, Any]
        Info object with ``version``, ``ansible``, ``web_host``,
        ``use_remote_runner``, and ``features`` fields.

    Examples
    --------
    >>> info = await get_info()
    """
    client = get_client()
    return await client.get("/api/info")


async def list_events() -> list[dict[str, Any]]:
    """Get all events related to Semaphore and the user's projects.

    Returns
    -------
    list[dict[str, Any]]
        List of event objects in chronological order.
    """
    client = get_client()
    return await client.get("/api/events")


async def list_last_events() -> list[dict[str, Any]]:
    """Get the last 200 events related to Semaphore and the user's projects.

    Returns
    -------
    list[dict[str, Any]]
        List of the most recent event objects (up to 200).
    """
    client = get_client()
    return await client.get("/api/events/last")


async def list_apps() -> list[dict[str, Any]]:
    """List available app types (runners) supported by this Semaphore instance.

    Returns
    -------
    list[dict[str, Any]]
        List of app objects.

    Examples
    --------
    >>> apps = await list_apps()
    """
    client = get_client()
    return await client.get("/api/apps")
