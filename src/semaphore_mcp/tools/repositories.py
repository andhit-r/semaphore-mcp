"""Repository management tools for Semaphore UI.

Covers ``/api/project/{project_id}/repositories`` endpoints.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def list_repositories(
    project_id: int,
    sort: str = "name",
    order: str = "asc",
) -> list[dict[str, Any]]:
    """List repositories linked to a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    sort : str
        Sort field: ``name``, ``git_url``, or ``ssh_key``.
    order : str
        Sort direction: ``asc`` or ``desc``.

    Returns
    -------
    list[dict[str, Any]]
        List of repository objects.

    Examples
    --------
    >>> repos = await list_repositories(1)
    """
    client = get_client()
    return await client.get(
        f"/api/project/{project_id}/repositories",
        params={"sort": sort, "order": order},
    )


async def get_repository(project_id: int, repository_id: int) -> dict[str, Any]:
    """Fetch a specific repository.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    repository_id : int
        The numeric repository ID.

    Returns
    -------
    dict[str, Any]
        Repository object.

    Examples
    --------
    >>> repo = await get_repository(1, 2)
    """
    client = get_client()
    return await client.get(
        f"/api/project/{project_id}/repositories/{repository_id}"
    )


async def create_repository(
    project_id: int,
    name: str,
    git_url: str,
    git_branch: str,
    ssh_key_id: int,
) -> dict[str, Any]:
    """Add a repository to a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    name : str
        Repository name.
    git_url : str
        Git clone URL (e.g. ``git@github.com:org/repo.git``).
    git_branch : str
        Default branch name.
    ssh_key_id : int
        ID of the SSH access key used for cloning.

    Returns
    -------
    dict[str, Any]
        The created repository object.

    Examples
    --------
    >>> repo = await create_repository(1, "demo", "git@github.com:org/demo.git",
    ...                                "main", 3)
    """
    client = get_client()
    return await client.post(
        f"/api/project/{project_id}/repositories",
        json={
            "name": name,
            "project_id": project_id,
            "git_url": git_url,
            "git_branch": git_branch,
            "ssh_key_id": ssh_key_id,
        },
    )


async def update_repository(
    project_id: int,
    repository_id: int,
    name: str,
    git_url: str,
    git_branch: str,
    ssh_key_id: int,
) -> dict[str, str]:
    """Update a repository.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    repository_id : int
        The numeric repository ID.
    name : str
        New repository name.
    git_url : str
        New Git clone URL.
    git_branch : str
        New default branch name.
    ssh_key_id : int
        New SSH key ID.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.put(
        f"/api/project/{project_id}/repositories/{repository_id}",
        json={
            "id": repository_id,
            "name": name,
            "project_id": project_id,
            "git_url": git_url,
            "git_branch": git_branch,
            "ssh_key_id": ssh_key_id,
        },
    )
    return {"status": "ok"}


async def delete_repository(project_id: int, repository_id: int) -> dict[str, str]:
    """Remove a repository from a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    repository_id : int
        The numeric repository ID.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.delete(
        f"/api/project/{project_id}/repositories/{repository_id}"
    )
    return {"status": "ok"}
