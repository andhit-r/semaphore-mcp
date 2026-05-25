"""Project management tools for Semaphore UI.

Covers ``/api/projects``, ``/api/project/{project_id}/``, project users,
and project views endpoints.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def list_projects() -> list[dict[str, Any]]:
    """List all projects accessible to the current user.

    Returns
    -------
    list[dict[str, Any]]
        List of project objects.

    Examples
    --------
    >>> projects = await list_projects()
    """
    client = get_client()
    return await client.get("/api/projects")


async def get_project(project_id: int) -> dict[str, Any]:
    """Fetch a specific project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.

    Returns
    -------
    dict[str, Any]
        Project object with ``id``, ``name``, ``alert``,
        ``max_parallel_tasks``, and ``created`` fields.

    Examples
    --------
    >>> project = await get_project(1)
    """
    client = get_client()
    return await client.get(f"/api/project/{project_id}/")


async def create_project(
    name: str,
    alert: bool = False,
    alert_chat: str = "",
    max_parallel_tasks: int = 0,
) -> dict[str, Any]:
    """Create a new project.

    Parameters
    ----------
    name : str
        Project name.
    alert : bool
        Whether to enable alerts for this project.
    alert_chat : str
        Chat identifier for alert notifications.
    max_parallel_tasks : int
        Maximum number of tasks that can run in parallel (0 = unlimited).

    Returns
    -------
    dict[str, Any]
        The created project object.

    Examples
    --------
    >>> project = await create_project("homelab")
    """
    client = get_client()
    body: dict[str, Any] = {
        "name": name,
        "alert": alert,
        "max_parallel_tasks": max_parallel_tasks,
    }
    if alert_chat:
        body["alert_chat"] = alert_chat
    return await client.post("/api/projects", json=body)


async def update_project(
    project_id: int,
    name: str,
    alert: bool = False,
    alert_chat: str = "",
    max_parallel_tasks: int = 0,
) -> dict[str, str]:
    """Update an existing project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    name : str
        New project name.
    alert : bool
        Whether to enable alerts.
    alert_chat : str
        Chat identifier for alert notifications.
    max_parallel_tasks : int
        Maximum parallel tasks (0 = unlimited).

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    body: dict[str, Any] = {
        "id": project_id,
        "name": name,
        "alert": alert,
        "max_parallel_tasks": max_parallel_tasks,
    }
    if alert_chat:
        body["alert_chat"] = alert_chat
    await client.put(f"/api/project/{project_id}/", json=body)
    return {"status": "ok"}


async def delete_project(project_id: int) -> dict[str, str]:
    """Delete a project and all its resources.

    Parameters
    ----------
    project_id : int
        The numeric project ID.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.delete(f"/api/project/{project_id}/")
    return {"status": "ok"}


async def get_project_role(project_id: int) -> dict[str, Any]:
    """Fetch the current user's role and permissions within a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.

    Returns
    -------
    dict[str, Any]
        Object with ``role`` (``owner`` | ``manager`` | ``task_runner`` |
        ``guest``) and ``permissions`` fields.

    Examples
    --------
    >>> role = await get_project_role(1)
    """
    client = get_client()
    return await client.get(f"/api/project/{project_id}/role")


async def get_project_events(project_id: int) -> list[dict[str, Any]]:
    """Get events related to a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.

    Returns
    -------
    list[dict[str, Any]]
        List of event objects in chronological order.
    """
    client = get_client()
    return await client.get(f"/api/project/{project_id}/events")


async def backup_project(project_id: int) -> dict[str, Any]:
    """Export a full backup of a project (templates, keys, inventories, etc.).

    Parameters
    ----------
    project_id : int
        The numeric project ID.

    Returns
    -------
    dict[str, Any]
        Project backup object.

    Examples
    --------
    >>> backup = await backup_project(1)
    """
    client = get_client()
    return await client.get(f"/api/project/{project_id}/backup")


# ── Project Users ────────────────────────────────────────────────────────────


async def list_project_users(
    project_id: int,
    sort: str = "name",
    order: str = "asc",
) -> list[dict[str, Any]]:
    """List users linked to a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    sort : str
        Sort field: ``name``, ``username``, ``email``, or ``role``.
    order : str
        Sort direction: ``asc`` or ``desc``.

    Returns
    -------
    list[dict[str, Any]]
        List of project user objects (includes ``role`` field).
    """
    client = get_client()
    return await client.get(
        f"/api/project/{project_id}/users",
        params={"sort": sort, "order": order},
    )


async def add_project_user(
    project_id: int,
    user_id: int,
    role: str,
) -> dict[str, str]:
    """Add a user to a project with a specific role.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    user_id : int
        The numeric user ID to add.
    role : str
        User role: ``owner``, ``manager``, ``task_runner``, or ``guest``.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.post(
        f"/api/project/{project_id}/users",
        json={"user_id": user_id, "role": role},
    )
    return {"status": "ok"}


async def remove_project_user(project_id: int, user_id: int) -> dict[str, str]:
    """Remove a user from a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    user_id : int
        The numeric user ID to remove.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.delete(f"/api/project/{project_id}/users/{user_id}")
    return {"status": "ok"}


async def update_project_user_role(
    project_id: int,
    user_id: int,
    role: str,
) -> dict[str, str]:
    """Update a user's role within a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    user_id : int
        The numeric user ID.
    role : str
        New role: ``owner``, ``manager``, ``task_runner``, or ``guest``.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.put(
        f"/api/project/{project_id}/users/{user_id}",
        json={"role": role},
    )
    return {"status": "ok"}


# ── Project Views ─────────────────────────────────────────────────────────────


async def list_project_views(project_id: int) -> list[dict[str, Any]]:
    """List all views in a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.

    Returns
    -------
    list[dict[str, Any]]
        List of view objects.
    """
    client = get_client()
    return await client.get(f"/api/project/{project_id}/views")


async def get_project_view(project_id: int, view_id: int) -> dict[str, Any]:
    """Fetch a specific project view.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    view_id : int
        The numeric view ID.

    Returns
    -------
    dict[str, Any]
        View object.
    """
    client = get_client()
    return await client.get(f"/api/project/{project_id}/views/{view_id}")


async def create_project_view(
    project_id: int,
    title: str,
    position: int = 0,
) -> dict[str, Any]:
    """Create a new view in a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    title : str
        View title.
    position : int
        Display order position (0-based).

    Returns
    -------
    dict[str, Any]
        The created view object.
    """
    client = get_client()
    return await client.post(
        f"/api/project/{project_id}/views",
        json={"title": title, "project_id": project_id, "position": position},
    )


async def update_project_view(
    project_id: int,
    view_id: int,
    title: str,
    position: int = 0,
) -> dict[str, str]:
    """Update a project view.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    view_id : int
        The numeric view ID.
    title : str
        New view title.
    position : int
        New display order position.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.put(
        f"/api/project/{project_id}/views/{view_id}",
        json={
            "id": view_id,
            "title": title,
            "project_id": project_id,
            "position": position,
        },
    )
    return {"status": "ok"}


async def delete_project_view(project_id: int, view_id: int) -> dict[str, str]:
    """Delete a project view.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    view_id : int
        The numeric view ID.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.delete(f"/api/project/{project_id}/views/{view_id}")
    return {"status": "ok"}
