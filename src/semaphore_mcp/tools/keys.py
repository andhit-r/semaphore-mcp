"""Access key management tools for Semaphore UI.

Covers ``/api/project/{project_id}/keys`` endpoints.
Supported key types: ``none``, ``ssh``, ``login_password``.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def list_keys(
    project_id: int,
    key_type: str = "",
    sort: str = "name",
    order: str = "asc",
) -> list[dict[str, Any]]:
    """List access keys linked to a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    key_type : str
        Optional filter by type: ``none``, ``ssh``, or ``login_password``.
    sort : str
        Sort field: ``name`` or ``type``.
    order : str
        Sort direction: ``asc`` or ``desc``.

    Returns
    -------
    list[dict[str, Any]]
        List of access key objects.

    Examples
    --------
    >>> keys = await list_keys(1)
    """
    client = get_client()
    params: dict[str, Any] = {"sort": sort, "order": order}
    if key_type:
        params["key_type"] = key_type
    return await client.get(f"/api/project/{project_id}/keys", params=params)


async def create_key(
    project_id: int,
    name: str,
    key_type: str,
    login: str = "",
    password: str = "",
    private_key: str = "",
    passphrase: str = "",
) -> dict[str, Any]:
    """Add an access key to a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    name : str
        Key name.
    key_type : str
        Key type: ``none``, ``ssh``, or ``login_password``.
    login : str
        Username (for ``ssh`` or ``login_password`` types).
    password : str
        Password (for ``login_password`` type).
    private_key : str
        SSH private key content (for ``ssh`` type).
    passphrase : str
        SSH private key passphrase (for ``ssh`` type).

    Returns
    -------
    dict[str, Any]
        The created access key object.

    Examples
    --------
    >>> key = await create_key(1, "deploy-key", "ssh", login="deploy",
    ...                        private_key="-----BEGIN RSA...")
    """
    client = get_client()
    body: dict[str, Any] = {
        "name": name,
        "type": key_type,
        "project_id": project_id,
    }
    if key_type == "login_password":
        body["login_password"] = {"login": login, "password": password}
    elif key_type == "ssh":
        body["ssh"] = {
            "login": login,
            "private_key": private_key,
            "passphrase": passphrase,
        }
    return await client.post(f"/api/project/{project_id}/keys", json=body)


async def update_key(
    project_id: int,
    key_id: int,
    name: str,
    key_type: str,
    login: str = "",
    password: str = "",
    private_key: str = "",
    passphrase: str = "",
) -> dict[str, str]:
    """Update an access key.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    key_id : int
        The numeric key ID.
    name : str
        New key name.
    key_type : str
        Key type: ``none``, ``ssh``, or ``login_password``.
    login : str
        Username (for ``ssh`` or ``login_password`` types).
    password : str
        Password (for ``login_password`` type).
    private_key : str
        SSH private key content (for ``ssh`` type).
    passphrase : str
        SSH private key passphrase (for ``ssh`` type).

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    body: dict[str, Any] = {
        "id": key_id,
        "name": name,
        "type": key_type,
        "project_id": project_id,
    }
    if key_type == "login_password":
        body["login_password"] = {"login": login, "password": password}
    elif key_type == "ssh":
        body["ssh"] = {
            "login": login,
            "private_key": private_key,
            "passphrase": passphrase,
        }
    await client.put(f"/api/project/{project_id}/keys/{key_id}", json=body)
    return {"status": "ok"}


async def delete_key(project_id: int, key_id: int) -> dict[str, str]:
    """Remove an access key from a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    key_id : int
        The numeric key ID.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.delete(f"/api/project/{project_id}/keys/{key_id}")
    return {"status": "ok"}
