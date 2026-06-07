"""CLI entry point untuk Semaphore UI MCP server.

Pilih transport via environment (MCPSettings):
  - ``stdio`` (default) → MCP client lokal (Claude Desktop / Claude Code stdio).
  - ``http`` / ``sse``  → service / remote (Claude Code remote, Claude Web).

Dijalankan via ``python -m semaphore_mcp`` atau entrypoint script::

    semaphore-mcp

Untuk deployment cloud lewat uvicorn, gunakan ``semaphore_mcp.asgi:app`` (lihat asgi.py).
"""

import logging
import sys


def main() -> None:
    """Konfigurasi logging lalu mulai MCP server sesuai transport yang dikonfigurasi.

    Level logging diambil dari ``MCP_LOG_LEVEL`` (default ``INFO``).
    Transport dan bind address dikontrol via :class:`~semaphore_mcp.config.MCPSettings`.
    """
    from .config import settings

    logging.basicConfig(
        level=getattr(logging, settings.mcp_log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
        stream=sys.stderr,
    )

    from .server import run

    run()


if __name__ == "__main__":
    main()
