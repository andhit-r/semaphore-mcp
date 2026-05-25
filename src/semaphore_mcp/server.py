"""FastMCP server for Semaphore UI.

Registers all tool functions and exposes a :func:`run` entry point that
honours the ``SEMAPHORE_TRANSPORT``, ``SEMAPHORE_HOST``, and
``SEMAPHORE_PORT`` environment variables for choosing between stdio and
SSE transports.
"""

from __future__ import annotations

import logging

from fastmcp import FastMCP

from .tools import (
    auth,
    environment,
    inventory,
    keys,
    projects,
    repositories,
    schedules,
    system,
    tasks,
    templates,
    users,
)

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "Semaphore UI MCP",
    instructions=(
        "MCP server for managing Semaphore UI via its REST API. "
        "Provides tools for creating and managing projects, templates, "
        "tasks, inventories, repositories, access keys, environments, "
        "schedules, and users. "
        "Configure the server via environment variables: SEMAPHORE_URL, "
        "SEMAPHORE_API_TOKEN (or SEMAPHORE_USERNAME + SEMAPHORE_PASSWORD)."
    ),
)

# ── System / Health ──────────────────────────────────────────────────────────
mcp.tool()(system.ping)
mcp.tool()(system.get_info)
mcp.tool()(system.list_events)
mcp.tool()(system.list_last_events)
mcp.tool()(system.list_apps)

# ── Authentication ───────────────────────────────────────────────────────────
mcp.tool()(auth.login)
mcp.tool()(auth.logout)
mcp.tool()(auth.list_tokens)
mcp.tool()(auth.create_token)
mcp.tool()(auth.delete_token)

# ── Users ────────────────────────────────────────────────────────────────────
mcp.tool()(users.get_current_user)
mcp.tool()(users.list_users)
mcp.tool()(users.get_user)
mcp.tool()(users.create_user)
mcp.tool()(users.update_user)
mcp.tool()(users.delete_user)
mcp.tool()(users.update_user_password)

# ── Projects ─────────────────────────────────────────────────────────────────
mcp.tool()(projects.list_projects)
mcp.tool()(projects.get_project)
mcp.tool()(projects.create_project)
mcp.tool()(projects.update_project)
mcp.tool()(projects.delete_project)
mcp.tool()(projects.get_project_role)
mcp.tool()(projects.get_project_events)
mcp.tool()(projects.backup_project)

# ── Project Users ─────────────────────────────────────────────────────────────
mcp.tool()(projects.list_project_users)
mcp.tool()(projects.add_project_user)
mcp.tool()(projects.remove_project_user)
mcp.tool()(projects.update_project_user_role)

# ── Project Views ─────────────────────────────────────────────────────────────
mcp.tool()(projects.list_project_views)
mcp.tool()(projects.get_project_view)
mcp.tool()(projects.create_project_view)
mcp.tool()(projects.update_project_view)
mcp.tool()(projects.delete_project_view)

# ── Access Keys ──────────────────────────────────────────────────────────────
mcp.tool()(keys.list_keys)
mcp.tool()(keys.create_key)
mcp.tool()(keys.update_key)
mcp.tool()(keys.delete_key)

# ── Repositories ─────────────────────────────────────────────────────────────
mcp.tool()(repositories.list_repositories)
mcp.tool()(repositories.get_repository)
mcp.tool()(repositories.create_repository)
mcp.tool()(repositories.update_repository)
mcp.tool()(repositories.delete_repository)

# ── Inventory ────────────────────────────────────────────────────────────────
mcp.tool()(inventory.list_inventory)
mcp.tool()(inventory.get_inventory)
mcp.tool()(inventory.create_inventory)
mcp.tool()(inventory.update_inventory)
mcp.tool()(inventory.delete_inventory)

# ── Environments ─────────────────────────────────────────────────────────────
mcp.tool()(environment.list_environments)
mcp.tool()(environment.get_environment)
mcp.tool()(environment.create_environment)
mcp.tool()(environment.update_environment)
mcp.tool()(environment.delete_environment)

# ── Templates ────────────────────────────────────────────────────────────────
mcp.tool()(templates.list_templates)
mcp.tool()(templates.get_template)
mcp.tool()(templates.create_template)
mcp.tool()(templates.update_template)
mcp.tool()(templates.delete_template)
mcp.tool()(templates.stop_all_template_tasks)

# ── Schedules ────────────────────────────────────────────────────────────────
mcp.tool()(schedules.get_schedule)
mcp.tool()(schedules.create_schedule)
mcp.tool()(schedules.update_schedule)
mcp.tool()(schedules.delete_schedule)

# ── Tasks ────────────────────────────────────────────────────────────────────
mcp.tool()(tasks.list_tasks)
mcp.tool()(tasks.list_last_tasks)
mcp.tool()(tasks.get_task)
mcp.tool()(tasks.start_task)
mcp.tool()(tasks.stop_task)
mcp.tool()(tasks.delete_task)
mcp.tool()(tasks.get_task_output)


def run() -> None:
    """Start the MCP server using the configured transport.

    Transport is controlled by the ``SEMAPHORE_TRANSPORT`` environment
    variable (``stdio`` or ``sse``).  When ``sse`` is chosen the server
    binds to ``SEMAPHORE_HOST``/``SEMAPHORE_PORT``
    (default ``0.0.0.0:8000``).
    """
    from .config import get_config

    config = get_config()
    transport = config.transport.lower()

    if transport == "sse":
        logger.info("Starting SSE server on %s:%d", config.host, config.port)
        mcp.run(transport="sse", host=config.host, port=config.port)
    else:
        logger.info("Starting stdio server")
        mcp.run(transport="stdio")
