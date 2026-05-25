"""Task management tools for Semaphore UI.

Covers ``/api/project/{project_id}/tasks`` endpoints including starting,
stopping, and retrieving output for tasks.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def list_tasks(project_id: int) -> list[dict[str, Any]]:
    """List all tasks for a project in chronological order.

    Parameters
    ----------
    project_id : int
        The numeric project ID.

    Returns
    -------
    list[dict[str, Any]]
        List of task objects.

    Examples
    --------
    >>> tasks = await list_tasks(1)
    """
    client = get_client()
    return await client.get(f"/api/project/{project_id}/tasks")


async def list_last_tasks(project_id: int) -> list[dict[str, Any]]:
    """List the last 200 tasks for a project.

    Parameters
    ----------
    project_id : int
        The numeric project ID.

    Returns
    -------
    list[dict[str, Any]]
        List of the most recent task objects (up to 200).

    Examples
    --------
    >>> tasks = await list_last_tasks(1)
    """
    client = get_client()
    return await client.get(f"/api/project/{project_id}/tasks/last")


async def get_task(project_id: int, task_id: int) -> dict[str, Any]:
    """Fetch details of a single task.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    task_id : int
        The numeric task ID.

    Returns
    -------
    dict[str, Any]
        Task object with ``id``, ``status``, ``template_id``, ``playbook``,
        ``git_branch``, ``message``, and ``environment`` fields.

    Examples
    --------
    >>> task = await get_task(1, 23)
    """
    client = get_client()
    return await client.get(f"/api/project/{project_id}/tasks/{task_id}")


async def start_task(
    project_id: int,
    template_id: int,
    debug: bool = False,
    dry_run: bool = False,
    diff: bool = False,
    playbook: str = "",
    environment: str = "",
    limit: str = "",
    git_branch: str = "",
    message: str = "",
    arguments: str = "",
    inventory_id: int = 0,
) -> dict[str, Any]:
    """Start a new task (run a template).

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    template_id : int
        ID of the template to execute.
    debug : bool
        Enable verbose/debug output.
    dry_run : bool
        Run in check mode (no changes made).
    diff : bool
        Show diff output for changed files.
    playbook : str
        Override the template's default playbook.
    environment : str
        JSON string of extra environment variables to merge.
    limit : str
        Ansible limit pattern (e.g. ``"webservers"``).
    git_branch : str
        Override the repository branch to use.
    message : str
        Human-readable description for this task run.
    arguments : str
        Override extra playbook arguments JSON array.
    inventory_id : int
        Override the template's inventory (0 = use template default).

    Returns
    -------
    dict[str, Any]
        The queued task object.

    Examples
    --------
    >>> task = await start_task(1, 7, message="manual deploy")
    """
    client = get_client()
    body: dict[str, Any] = {
        "template_id": template_id,
        "debug": debug,
        "dry_run": dry_run,
        "diff": diff,
    }
    if playbook:
        body["playbook"] = playbook
    if environment:
        body["environment"] = environment
    if limit:
        body["limit"] = limit
    if git_branch:
        body["git_branch"] = git_branch
    if message:
        body["message"] = message
    if arguments:
        body["arguments"] = arguments
    if inventory_id:
        body["inventory_id"] = inventory_id
    return await client.post(f"/api/project/{project_id}/tasks", json=body)


async def stop_task(
    project_id: int, task_id: int, force: bool = False
) -> dict[str, str]:
    """Stop a running task.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    task_id : int
        The numeric task ID to stop.
    force : bool
        If ``True``, forcibly kill the task immediately.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.

    Examples
    --------
    >>> await stop_task(1, 23)
    {'status': 'ok'}
    """
    client = get_client()
    await client.post(
        f"/api/project/{project_id}/tasks/{task_id}/stop",
        json={"force": force},
    )
    return {"status": "ok"}


async def delete_task(project_id: int, task_id: int) -> dict[str, str]:
    """Delete a task and its output from Semaphore.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    task_id : int
        The numeric task ID.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.delete(f"/api/project/{project_id}/tasks/{task_id}")
    return {"status": "ok"}


async def get_task_output(project_id: int, task_id: int) -> list[dict[str, Any]]:
    """Retrieve the output lines for a task.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    task_id : int
        The numeric task ID.

    Returns
    -------
    list[dict[str, Any]]
        List of output objects, each with ``task_id``, ``time``,
        and ``output`` fields.

    Examples
    --------
    >>> output = await get_task_output(1, 23)
    >>> for line in output:
    ...     print(line["output"])
    """
    client = get_client()
    return await client.get(f"/api/project/{project_id}/tasks/{task_id}/output")
