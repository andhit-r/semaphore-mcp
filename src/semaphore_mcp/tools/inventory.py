"""Inventory management tools for Semaphore UI.

Covers ``/api/project/{project_id}/inventory`` endpoints.
Supported inventory types: ``static``, ``static-yaml``, ``file``,
``terraform-workspace``.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def list_inventory(
    project_id: int,
    sort: str = "name",
    order: str = "asc",
) -> list[dict[str, Any]]:
    """List inventories in a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    sort : str
        Sort field: ``name`` or ``type``.
    order : str
        Sort direction: ``asc`` or ``desc``.

    Returns
    -------
    list[dict[str, Any]]
        List of inventory objects.

    Examples
    --------
    >>> inventories = await list_inventory(1)
    """
    client = get_client()
    return await client.get(
        f"/api/project/{project_id}/inventory",
        params={"sort": sort, "order": order},
    )


async def get_inventory(project_id: int, inventory_id: int) -> dict[str, Any]:
    """Fetch a specific inventory.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    inventory_id : int
        The numeric inventory ID.

    Returns
    -------
    dict[str, Any]
        Inventory object.

    Examples
    --------
    >>> inv = await get_inventory(1, 5)
    """
    client = get_client()
    return await client.get(
        f"/api/project/{project_id}/inventory/{inventory_id}"
    )


async def create_inventory(
    project_id: int,
    name: str,
    inventory_type: str,
    inventory: str = "",
    ssh_key_id: int = 0,
    become_key_id: int = 0,
    repository_id: int = 0,
) -> dict[str, Any]:
    """Create an inventory in a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    name : str
        Inventory name.
    inventory_type : str
        Inventory type: ``static``, ``static-yaml``, ``file``, or
        ``terraform-workspace``.
    inventory : str
        Inventory content (for ``static`` / ``static-yaml`` types).
    ssh_key_id : int
        SSH key ID for connecting to inventory hosts (0 = none).
    become_key_id : int
        Key ID for privilege escalation (0 = none).
    repository_id : int
        Repository ID (for ``file`` / ``terraform-workspace`` types; 0 = none).

    Returns
    -------
    dict[str, Any]
        The created inventory object.

    Examples
    --------
    >>> inv = await create_inventory(1, "prod", "static", inventory="[servers]\\n...")
    """
    client = get_client()
    body: dict[str, Any] = {
        "name": name,
        "project_id": project_id,
        "inventory": inventory,
        "type": inventory_type,
    }
    if ssh_key_id:
        body["ssh_key_id"] = ssh_key_id
    if become_key_id:
        body["become_key_id"] = become_key_id
    if repository_id:
        body["repository_id"] = repository_id
    return await client.post(f"/api/project/{project_id}/inventory", json=body)


async def update_inventory(
    project_id: int,
    inventory_id: int,
    name: str,
    inventory_type: str,
    inventory: str = "",
    ssh_key_id: int = 0,
    become_key_id: int = 0,
    repository_id: int = 0,
) -> dict[str, str]:
    """Update an inventory.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    inventory_id : int
        The numeric inventory ID.
    name : str
        New inventory name.
    inventory_type : str
        Inventory type: ``static``, ``static-yaml``, ``file``, or
        ``terraform-workspace``.
    inventory : str
        New inventory content (for ``static`` / ``static-yaml`` types).
    ssh_key_id : int
        SSH key ID (0 = none).
    become_key_id : int
        Privilege escalation key ID (0 = none).
    repository_id : int
        Repository ID (0 = none).

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    body: dict[str, Any] = {
        "id": inventory_id,
        "name": name,
        "project_id": project_id,
        "inventory": inventory,
        "type": inventory_type,
    }
    if ssh_key_id:
        body["ssh_key_id"] = ssh_key_id
    if become_key_id:
        body["become_key_id"] = become_key_id
    if repository_id:
        body["repository_id"] = repository_id
    await client.put(
        f"/api/project/{project_id}/inventory/{inventory_id}", json=body
    )
    return {"status": "ok"}


async def delete_inventory(project_id: int, inventory_id: int) -> dict[str, str]:
    """Remove an inventory from a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    inventory_id : int
        The numeric inventory ID.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.delete(f"/api/project/{project_id}/inventory/{inventory_id}")
    return {"status": "ok"}
