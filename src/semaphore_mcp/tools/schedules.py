"""Schedule management tools for Semaphore UI.

Covers ``/api/project/{project_id}/schedules`` endpoints.
Schedules trigger templates automatically on a cron-like schedule.
"""

from __future__ import annotations

import logging
from typing import Any

from ..state import get_client

logger = logging.getLogger(__name__)


async def get_schedule(project_id: int, schedule_id: int) -> dict[str, Any]:
    """Fetch a specific schedule.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    schedule_id : int
        The numeric schedule ID.

    Returns
    -------
    dict[str, Any]
        Schedule object with ``id``, ``cron_format``, ``template_id``,
        ``name``, and ``active`` fields.

    Examples
    --------
    >>> sched = await get_schedule(1, 9)
    """
    client = get_client()
    return await client.get(
        f"/api/project/{project_id}/schedules/{schedule_id}"
    )


async def create_schedule(
    project_id: int,
    template_id: int,
    cron_format: str,
    name: str = "",
    active: bool = True,
) -> dict[str, Any]:
    """Create a cron schedule for a template.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    template_id : int
        The numeric template ID to trigger.
    cron_format : str
        Cron expression (e.g. ``"0 2 * * *"`` for nightly at 02:00).
    name : str
        Optional schedule name.
    active : bool
        Whether the schedule is active.

    Returns
    -------
    dict[str, Any]
        The created schedule object.

    Examples
    --------
    >>> sched = await create_schedule(1, 7, "0 2 * * *", name="nightly")
    """
    client = get_client()
    return await client.post(
        f"/api/project/{project_id}/schedules",
        json={
            "project_id": project_id,
            "template_id": template_id,
            "cron_format": cron_format,
            "name": name,
            "active": active,
        },
    )


async def update_schedule(
    project_id: int,
    schedule_id: int,
    template_id: int,
    cron_format: str,
    name: str = "",
    active: bool = True,
) -> dict[str, str]:
    """Update an existing schedule.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    schedule_id : int
        The numeric schedule ID.
    template_id : int
        The numeric template ID.
    cron_format : str
        New cron expression.
    name : str
        New schedule name.
    active : bool
        Whether the schedule should be active.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.put(
        f"/api/project/{project_id}/schedules/{schedule_id}",
        json={
            "id": schedule_id,
            "project_id": project_id,
            "template_id": template_id,
            "cron_format": cron_format,
            "name": name,
            "active": active,
        },
    )
    return {"status": "ok"}


async def delete_schedule(project_id: int, schedule_id: int) -> dict[str, str]:
    """Delete a schedule.

    Parameters
    ----------
    project_id : int
        The numeric project ID.
    schedule_id : int
        The numeric schedule ID.

    Returns
    -------
    dict[str, str]
        ``{"status": "ok"}`` on success.
    """
    client = get_client()
    await client.delete(
        f"/api/project/{project_id}/schedules/{schedule_id}"
    )
    return {"status": "ok"}
