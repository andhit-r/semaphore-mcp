"""User management tools for Semaphore UI.

Covers ``/api/user/``, ``/api/users``, and ``/api/users/{user_id}``
endpoints including CRUD operations and password changes.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def get_current_user() -> dict[str, Any]:
    """Fetch the currently authenticated user's profile.

    Returns
    -------
    dict[str, Any]
        User object with ``id``, ``name``, ``username``, ``email``,
        ``admin``, and ``created`` fields.

    Examples
    --------
    >>> user = await get_current_user()
    """
    client = get_client()
    return await client.get("/api/user/")


async def list_users() -> list[dict[str, Any]]:
    """Fetch all users in the Semaphore instance.

    Returns
    -------
    list[dict[str, Any]]
        List of user objects.

    Examples
    --------
    >>> users = await list_users()
    """
    client = get_client()
    return await client.get("/api/users")


async def get_user(user_id: int) -> dict[str, Any]:
    """Fetch a specific user's profile.

    Parameters
    ----------
    user_id : int
        The numeric user ID.

    Returns
    -------
    dict[str, Any]
        User object.

    Examples
    --------
    >>> user = await get_user(1)
    """
    client = get_client()
    return await client.get(f"/api/users/{user_id}/")


async def create_user(
    name: str,
    username: str,
    email: str,
    password: str,
    admin: bool = False,
    alert: bool = False,
) -> dict[str, Any]:
    """Create a new Semaphore user.

    Parameters
    ----------
    name : str
        Display name of the user.
    username : str
        Login username.
    email : str
        Email address.
    password : str
        Initial password.
    admin : bool
        Whether the user has admin privileges.
    alert : bool
        Whether the user should receive alert emails.

    Returns
    -------
    dict[str, Any]
        The created user object.

    Examples
    --------
    >>> user = await create_user("Alice", "alice", "alice@example.com", "s3cr3t")
    """
    client = get_client()
    return await client.post(
        "/api/users",
        json={
            "name": name,
            "username": username,
            "email": email,
            "password": password,
            "admin": admin,
            "alert": alert,
        },
    )


async def update_user(
    user_id: int,
    name: str,
    username: str,
    email: str,
    admin: bool = False,
    alert: bool = False,
) -> dict[str, str]:
    """Update a user's profile details.

    Parameters
    ----------
    user_id : int
        The numeric user ID.
    name : str
        New display name.
    username : str
        New username.
    email : str
        New email address.
    admin : bool
        Admin privileges flag.
    alert : bool
        Alert emails flag.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.put(
        f"/api/users/{user_id}/",
        json={
            "name": name,
            "username": username,
            "email": email,
            "admin": admin,
            "alert": alert,
        },
    )
    return {"status": "ok"}


async def delete_user(user_id: int) -> dict[str, str]:
    """Delete a user from Semaphore.

    Parameters
    ----------
    user_id : int
        The numeric user ID.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.delete(f"/api/users/{user_id}/")
    return {"status": "ok"}


async def update_user_password(user_id: int, password: str) -> dict[str, str]:
    """Update a user's password.

    Parameters
    ----------
    user_id : int
        The numeric user ID.
    password : str
        The new password.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.post(
        f"/api/users/{user_id}/password",
        json={"password": password},
    )
    return {"status": "ok"}
