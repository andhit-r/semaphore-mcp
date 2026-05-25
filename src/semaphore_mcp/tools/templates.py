"""Template management tools for Semaphore UI.

Covers ``/api/project/{project_id}/templates`` endpoints.
Templates define the playbook, inventory, environment, and repository
for a task.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def list_templates(
    project_id: int,
    sort: str = "name",
    order: str = "asc",
) -> list[dict[str, Any]]:
    """List templates in a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    sort : str
        Sort field: ``name``, ``playbook``, ``ssh_key``, ``inventory``,
        ``environment``, or ``repository``.
    order : str
        Sort direction: ``asc`` or ``desc``.

    Returns
    -------
    list[dict[str, Any]]
        List of template objects (each includes ``last_task`` if available).

    Examples
    --------
    >>> templates = await list_templates(1)
    """
    client = get_client()
    return await client.get(
        f"/api/project/{project_id}/templates",
        params={"sort": sort, "order": order},
    )


async def get_template(project_id: int, template_id: int) -> dict[str, Any]:
    """Fetch a specific template.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    template_id : int
        The numeric template ID.

    Returns
    -------
    dict[str, Any]
        Template object.

    Examples
    --------
    >>> tmpl = await get_template(1, 7)
    """
    client = get_client()
    return await client.get(
        f"/api/project/{project_id}/templates/{template_id}"
    )


async def create_template(
    project_id: int,
    name: str,
    playbook: str,
    inventory_id: int,
    repository_id: int,
    environment_id: int,
    ssh_key_id: int = 0,
    template_type: str = "",
    app: str = "ansible",
    description: str = "",
    arguments: str = "[]",
    allow_override_args_in_task: bool = False,
    git_branch: str = "",
    view_id: int = 0,
    autorun: bool = False,
    suppress_success_alerts: bool = False,
) -> dict[str, Any]:
    """Create a new template.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    name : str
        Template name.
    playbook : str
        Playbook file path relative to the repository (e.g. ``site.yml``).
    inventory_id : int
        ID of the inventory to use.
    repository_id : int
        ID of the repository containing the playbook.
    environment_id : int
        ID of the environment (variable group) to use.
    ssh_key_id : int
        ID of the SSH key for host access (0 = none).
    template_type : str
        Template type: ``""`` (default), ``"build"``, or ``"deploy"``.
    app : str
        App type: ``ansible``, ``terraform``, ``tofu``, ``bash``,
        ``powershell``, or ``python``.
    description : str
        Human-readable description.
    arguments : str
        JSON array of extra CLI arguments (e.g. ``'["--tags", "web"]'``).
    allow_override_args_in_task : bool
        Allow per-task argument overrides.
    git_branch : str
        Override the repository's default branch for this template.
    view_id : int
        ID of the view to associate with this template (0 = none).
    autorun : bool
        Automatically run this template when the repository changes.
    suppress_success_alerts : bool
        Do not send alerts on successful task completion.

    Returns
    -------
    dict[str, Any]
        The created template object.

    Examples
    --------
    >>> tmpl = await create_template(1, "Deploy", "deploy.yml", 5, 4, 6)
    """
    client = get_client()
    body: dict[str, Any] = {
        "project_id": project_id,
        "name": name,
        "playbook": playbook,
        "inventory_id": inventory_id,
        "repository_id": repository_id,
        "environment_id": environment_id,
        "app": app,
        "type": template_type,
        "description": description,
        "arguments": arguments,
        "allow_override_args_in_task": allow_override_args_in_task,
        "autorun": autorun,
        "suppress_success_alerts": suppress_success_alerts,
    }
    if ssh_key_id:
        body["ssh_key_id"] = ssh_key_id
    if git_branch:
        body["git_branch"] = git_branch
    if view_id:
        body["view_id"] = view_id
    return await client.post(
        f"/api/project/{project_id}/templates", json=body
    )


async def update_template(
    project_id: int,
    template_id: int,
    name: str,
    playbook: str,
    inventory_id: int,
    repository_id: int,
    environment_id: int,
    ssh_key_id: int = 0,
    template_type: str = "",
    app: str = "ansible",
    description: str = "",
    arguments: str = "[]",
    allow_override_args_in_task: bool = False,
    git_branch: str = "",
    view_id: int = 0,
    autorun: bool = False,
    suppress_success_alerts: bool = False,
) -> dict[str, str]:
    """Update an existing template.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    template_id : int
        The numeric template ID.
    name : str
        New template name.
    playbook : str
        New playbook file path.
    inventory_id : int
        New inventory ID.
    repository_id : int
        New repository ID.
    environment_id : int
        New environment ID.
    ssh_key_id : int
        New SSH key ID (0 = none).
    template_type : str
        Template type: ``""``, ``"build"``, or ``"deploy"``.
    app : str
        App type.
    description : str
        New description.
    arguments : str
        New extra arguments JSON array.
    allow_override_args_in_task : bool
        Allow per-task argument overrides.
    git_branch : str
        New branch override.
    view_id : int
        New view ID (0 = none).
    autorun : bool
        Auto-run on repository changes.
    suppress_success_alerts : bool
        Suppress success alert notifications.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    body: dict[str, Any] = {
        "id": template_id,
        "project_id": project_id,
        "name": name,
        "playbook": playbook,
        "inventory_id": inventory_id,
        "repository_id": repository_id,
        "environment_id": environment_id,
        "app": app,
        "type": template_type,
        "description": description,
        "arguments": arguments,
        "allow_override_args_in_task": allow_override_args_in_task,
        "autorun": autorun,
        "suppress_success_alerts": suppress_success_alerts,
    }
    if ssh_key_id:
        body["ssh_key_id"] = ssh_key_id
    if git_branch:
        body["git_branch"] = git_branch
    if view_id:
        body["view_id"] = view_id
    await client.put(
        f"/api/project/{project_id}/templates/{template_id}", json=body
    )
    return {"status": "ok"}


async def delete_template(project_id: int, template_id: int) -> dict[str, str]:
    """Delete a template.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    template_id : int
        The numeric template ID.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.delete(f"/api/project/{project_id}/templates/{template_id}")
    return {"status": "ok"}


async def stop_all_template_tasks(
    project_id: int, template_id: int, force: bool = False
) -> dict[str, str]:
    """Stop all active tasks for a template.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    template_id : int
        The numeric template ID.
    force : bool
        If ``True``, forcibly kill tasks immediately instead of gracefully
        stopping them.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.

    Examples
    --------
    >>> await stop_all_template_tasks(1, 7, force=True)
    {'status': 'ok'}
    """
    client = get_client()
    await client.post(
        f"/api/project/{project_id}/templates/{template_id}/stop_all_tasks",
        json={"force": force},
    )
    return {"status": "ok"}
