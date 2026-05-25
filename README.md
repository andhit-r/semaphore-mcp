# Semaphore MCP Server

[![PyPI version](https://badge.fury.io/py/semaphore-mcp.svg)](https://badge.fury.io/py/semaphore-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that wraps
the [Semaphore UI](https://semaphoreui.com/) REST API, allowing AI assistants (Claude,
Copilot, etc.) to manage Semaphore instances — projects, templates, tasks, inventories,
repositories, and more.

---

## Features

- **Projects** — create, read, update, delete, backup, manage users and views
- **Templates** — full CRUD + stop all running tasks
- **Tasks** — start, stop, delete, stream output
- **Schedules** — CRUD for cron-based task triggers
- **Inventories** — static, static-yaml, file, terraform-workspace
- **Repositories** — Git repository references
- **Keys** — SSH, login/password, and keyless access keys
- **Environments** — variable groups for template configuration
- **Users** — CRUD + password management
- **Authentication** — API token or session-cookie auth, auto re-auth on 401
- **System** — ping, server info, event log, app catalog

---

## Installation

```bash
pip install semaphore-mcp
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv pip install semaphore-mcp
```

---

## Configuration

All configuration is via environment variables:

| Variable | Default | Description |
|---|---|---|
| `SEMAPHORE_URL` | `http://localhost:3000` | Base URL of Semaphore |
| `SEMAPHORE_API_TOKEN` | _(unset)_ | API token (preferred over user/pass) |
| `SEMAPHORE_USERNAME` | `admin` | Username for session auth |
| `SEMAPHORE_PASSWORD` | _(required if no token)_ | Password for session auth |
| `SEMAPHORE_TIMEOUT` | `30.0` | HTTP timeout in seconds |
| `SEMAPHORE_VERIFY_SSL` | `true` | Verify TLS certificates |
| `SEMAPHORE_TRANSPORT` | `stdio` | MCP transport: `stdio` or `sse` |
| `SEMAPHORE_HOST` | `0.0.0.0` | SSE bind host |
| `SEMAPHORE_PORT` | `8000` | SSE bind port |

**Authentication priority**: if `SEMAPHORE_API_TOKEN` is set, it is used as a Bearer
token and no login call is made. Otherwise, `SEMAPHORE_USERNAME` +
`SEMAPHORE_PASSWORD` are used for session-cookie auth via `POST /api/auth/login`.

---

## Quickstart

### stdio (default — for Claude Desktop / VS Code)

```jsonc
// claude_desktop_config.json
{
  "mcpServers": {
    "semaphore": {
      "command": "semaphore-mcp",
      "env": {
        "SEMAPHORE_URL": "http://your-semaphore:3000",
        "SEMAPHORE_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

### Docker

```bash
docker run --rm \
  -e SEMAPHORE_URL=http://semaphore:3000 \
  -e SEMAPHORE_API_TOKEN=your-token \
  ghcr.io/andhit-r/semaphore-mcp:latest
```

### SSE transport

```bash
SEMAPHORE_URL=http://semaphore:3000 \
SEMAPHORE_API_TOKEN=your-token \
SEMAPHORE_TRANSPORT=sse \
semaphore-mcp
```

---

## Available Tools

### Authentication
- `login` — Authenticate with Semaphore
- `logout` — End current session
- `list_tokens` — List API tokens for current user
- `create_token` — Create a new API token
- `delete_token` — Delete an API token

### Users
- `get_current_user` — Get currently authenticated user
- `list_users` — List all users (admin only)
- `get_user` — Get a specific user
- `create_user` — Create a user
- `update_user` — Update user attributes
- `delete_user` — Delete a user
- `update_user_password` — Change a user's password

### Projects
- `list_projects` — List all accessible projects
- `get_project` — Get a specific project
- `create_project` — Create a project
- `update_project` — Update a project
- `delete_project` — Delete a project
- `get_project_role` — Get current user's role in a project
- `get_project_events` — List recent project events
- `backup_project` — Export project backup as JSON
- `list_project_users` — List users in a project
- `add_project_user` — Add a user to a project
- `remove_project_user` — Remove a user from a project
- `update_project_user_role` — Change a user's project role
- `list_project_views` — List project views
- `create_project_view` — Create a view
- `update_project_view` — Update a view
- `delete_project_view` — Delete a view

### Keys
- `list_keys` — List access keys in a project
- `create_key` — Create an access key (none/ssh/login_password)
- `update_key` — Update a key
- `delete_key` — Delete a key

### Repositories
- `list_repositories` — List repositories in a project
- `get_repository` — Get a repository
- `create_repository` — Add a repository
- `update_repository` — Update a repository
- `delete_repository` — Remove a repository

### Inventory
- `list_inventory` — List inventories in a project
- `get_inventory` — Get an inventory
- `create_inventory` — Create an inventory
- `update_inventory` — Update an inventory
- `delete_inventory` — Delete an inventory

### Environments
- `list_environments` — List environments in a project
- `get_environment` — Get an environment
- `create_environment` — Create an environment
- `update_environment` — Update an environment
- `delete_environment` — Delete an environment

### Templates
- `list_templates` — List templates in a project
- `get_template` — Get a template
- `create_template` — Create a template
- `update_template` — Update a template
- `delete_template` — Delete a template
- `stop_all_template_tasks` — Stop all running tasks for a template

### Schedules
- `get_schedule` — Get a schedule
- `create_schedule` — Create a cron schedule
- `update_schedule` — Update a schedule
- `delete_schedule` — Delete a schedule

### Tasks
- `list_tasks` — List all tasks in a project
- `list_last_tasks` — List the last 200 tasks per template
- `get_task` — Get a specific task
- `start_task` — Run a template
- `stop_task` — Stop a running task
- `delete_task` — Delete a task
- `get_task_output` — Stream task output lines

### System
- `ping` — Health check
- `get_info` — Semaphore version and runtime info
- `list_events` — Global event log
- `list_last_events` — Last 200 global events
- `list_apps` — List available runner apps

---

## Development

```bash
git clone https://github.com/andhit-r/semaphore-mcp
cd semaphore-mcp
uv pip install -e ".[dev]"
pytest
```

---

## License

MIT — see [LICENSE](LICENSE).
