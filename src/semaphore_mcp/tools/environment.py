"""Environment (variable group) management tools for Semaphore UI.

Covers ``/api/project/{project_id}/environment`` endpoints.
Environments store extra variables and secrets passed to Ansible tasks.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def list_environments(
    project_id: int,
    sort: str = "name",
    order: str = "asc",
) -> list[dict[str, Any]]:
    """List environments (variable groups) in a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    sort : str
        Sort field: ``name``.
    order : str
        Sort direction: ``asc`` or ``desc``.

    Returns
    -------
    list[dict[str, Any]]
        List of environment objects.

    Examples
    --------
    >>> envs = await list_environments(1)
    """
    client = get_client()
    return await client.get(
        f"/api/project/{project_id}/environment",
        params={"sort": sort, "order": order},
    )


async def get_environment(project_id: int, environment_id: int) -> dict[str, Any]:
    """Fetch a specific environment.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    environment_id : int
        The numeric environment ID.

    Returns
    -------
    dict[str, Any]
        Environment object with ``id``, ``name``, ``json``, ``env``,
        and ``secrets`` fields.

    Examples
    --------
    >>> env = await get_environment(1, 6)
    """
    client = get_client()
    return await client.get(f"/api/project/{project_id}/environment/{environment_id}")


async def create_environment(
    project_id: int,
    name: str,
    env_json: str = "{}",
    env_vars: str = "",
    password: str = "",
) -> dict[str, Any]:
    """Create an environment (variable group) in a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    name : str
        Environment name.
    env_json : str
        JSON string of extra variables passed to the playbook
        (e.g. ``'{"key": "value"}'``).
    env_vars : str
        Shell environment variables string
        (e.g. ``'{"ANSIBLE_ROLES_PATH": "/opt/roles"}'``).
    password : str
        Optional vault password for this environment.

    Returns
    -------
    dict[str, Any]
        The created environment object.

    Examples
    --------
    >>> env = await create_environment(1, "Empty")
    """
    client = get_client()
    return await client.post(
        f"/api/project/{project_id}/environment",
        json={
            "name": name,
            "project_id": project_id,
            "json": env_json,
            "env": env_vars,
            "password": password,
        },
    )


async def update_environment(
    project_id: int,
    environment_id: int,
    name: str,
    env_json: str = "{}",
    env_vars: str = "",
    password: str = "",
) -> dict[str, str]:
    """Update an environment.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    environment_id : int
        The numeric environment ID.
    name : str
        New environment name.
    env_json : str
        New JSON variables string.
    env_vars : str
        New shell environment variables string.
    password : str
        New vault password.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.put(
        f"/api/project/{project_id}/environment/{environment_id}",
        json={
            "id": environment_id,
            "name": name,
            "project_id": project_id,
            "json": env_json,
            "env": env_vars,
            "password": password,
        },
    )
    return {"status": "ok"}


async def delete_environment(project_id: int, environment_id: int) -> dict[str, str]:
    """Remove an environment from a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    environment_id : int
        The numeric environment ID.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.delete(f"/api/project/{project_id}/environment/{environment_id}")
    return {"status": "ok"}
