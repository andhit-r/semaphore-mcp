"""Singleton accessor for the shared :class:`~semaphore_mcp.client.SemaphoreClient`.

All tool modules call :func:`get_client` to obtain the shared client
instance, which is created lazily from the current configuration.
:func:`set_client` is provided for dependency injection in tests.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import SemaphoreClient

_client: SemaphoreClient | None = None


def get_client() -> SemaphoreClient:
    """Return the process-level :class:`~semaphore_mcp.client.SemaphoreClient`.

    Creates the client on first call using :func:`~semaphore_mcp.config.get_config`.

    Returns
    -------
    SemaphoreClient
        The shared HTTP client instance.
    """
    global _client
    if _client is None:
        from .client import SemaphoreClient
        from .config import get_config

        _client = SemaphoreClient(get_config())
    return _client


def set_client(client: SemaphoreClient | None) -> None:
    """Replace the singleton client (used in tests).

    Parameters
    ----------
    client : SemaphoreClient | None
        New client instance, or ``None`` to reset.
    """
    global _client
    _client = client
