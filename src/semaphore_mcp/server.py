"""FastMCP server untuk Semaphore UI.

Auth pintu depan dipilih berdasarkan konfigurasi (lihat config.py):
  - Authentik OAuth (Claude.ai): aktif bila AUTHENTIK_* + MCP_BASE_URL diisi.
    Pengguna login via Authentik; AUTHENTIK_ALLOWED_USERNAMES membatasi (kosong=semua).
  - API Key (VS Code/CLI): aktif bila MCP_API_KEY diisi (Authorization: Bearer <key>).
  - Keduanya bisa aktif bersamaan via MultiAuth.
  - Tanpa konfigurasi: tanpa auth (hanya untuk stdio / jaringan lokal).

Mendaftarkan semua fungsi tool Semaphore dan mengekspos fungsi :func:`run`
yang menghormati ``MCP_TRANSPORT``, ``MCP_HOST``, dan ``MCP_PORT``.
"""

from __future__ import annotations

import logging

from fastmcp import FastMCP

from .config import settings
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

# ── Pemilihan auth pintu depan ────────────────────────────────────────────────
_auth = None
_authentik_aktif = bool(
    settings.authentik_base_url
    and settings.authentik_app_slug
    and settings.authentik_client_id
    and settings.authentik_client_secret
    and settings.mcp_base_url
)

if _authentik_aktif:
    from fastmcp.server.auth import MultiAuth

    from .auth_provider import AuthentikProvider, BearerApiKeyVerifier

    logger.info("OAuth Authentik AKTIF — slug: %s", settings.authentik_app_slug)
    _provider = AuthentikProvider(
        authentik_base_url=settings.authentik_base_url,
        application_slug=settings.authentik_app_slug,
        client_id=settings.authentik_client_id,
        client_secret=settings.authentik_client_secret,
        base_url=settings.mcp_base_url,
        allowed_usernames=settings.authentik_allowed_usernames,
        require_authorization_consent="external",
    )
    if settings.mcp_api_key:
        logger.info("API Key AKTIF (MultiAuth: Authentik OAuth + API Key)")
        _auth = MultiAuth(
            server=_provider,
            verifiers=[BearerApiKeyVerifier(api_key=settings.mcp_api_key)],
        )
    else:
        _auth = _provider

elif settings.mcp_api_key:
    from fastmcp.server.auth import MultiAuth

    from .auth_provider import BearerApiKeyVerifier

    logger.info("API Key AKTIF (tanpa OAuth)")
    _auth = MultiAuth(verifiers=[BearerApiKeyVerifier(api_key=settings.mcp_api_key)])

else:
    logger.warning(
        "Tidak ada auth dikonfigurasi — server terbuka. Isi AUTHENTIK_* + MCP_BASE_URL "
        "untuk deployment Claude Web."
    )

mcp = FastMCP(
    name=settings.mcp_server_name,
    auth=_auth,
    instructions=(
        "MCP server untuk mengelola Semaphore UI via REST API. "
        "Menyediakan tools untuk membuat dan mengelola projects, templates, "
        "tasks, inventories, repositories, access keys, environments, "
        "schedules, dan users. "
        "Konfigurasi koneksi via env: SEMAPHORE_URL, "
        "SEMAPHORE_API_TOKEN (atau SEMAPHORE_USERNAME + SEMAPHORE_PASSWORD)."
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
    """Start the MCP server menggunakan transport yang dikonfigurasi.

    Transport dikontrol via ``MCP_TRANSPORT`` (``stdio`` default, atau ``http``/``sse``).
    Untuk deployment cloud via uvicorn, gunakan ``semaphore_mcp.asgi:app``.
    """
    if settings.mcp_transport == "stdio":
        logger.info("Starting stdio server")
        mcp.run()
    else:
        logger.info(
            "Starting %s server pada %s:%d",
            settings.mcp_transport,
            settings.mcp_host,
            settings.mcp_port,
        )
        mcp.run(
            transport=settings.mcp_transport,
            host=settings.mcp_host,
            port=settings.mcp_port,
        )
