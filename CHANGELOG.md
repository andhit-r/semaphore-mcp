# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-01

### Added

- Initial release of `semaphore-mcp`
- MCP server wrapping the Semaphore UI REST API
- Dual authentication: API token (Bearer) or session-cookie (username/password)
- Auto re-authentication on 401/403 responses
- **Authentication tools**: `login`, `logout`, `list_tokens`, `create_token`, `delete_token`
- **User tools**: `get_current_user`, `list_users`, `get_user`, `create_user`, `update_user`, `delete_user`, `update_user_password`
- **Project tools**: `list_projects`, `get_project`, `create_project`, `update_project`, `delete_project`, `get_project_role`, `get_project_events`, `backup_project`, `list_project_users`, `add_project_user`, `remove_project_user`, `update_project_user_role`, `list_project_views`, `get_project_view`, `create_project_view`, `update_project_view`, `delete_project_view`
- **Key tools**: `list_keys`, `create_key`, `update_key`, `delete_key`
- **Repository tools**: `list_repositories`, `get_repository`, `create_repository`, `update_repository`, `delete_repository`
- **Inventory tools**: `list_inventory`, `get_inventory`, `create_inventory`, `update_inventory`, `delete_inventory`
- **Environment tools**: `list_environments`, `get_environment`, `create_environment`, `update_environment`, `delete_environment`
- **Template tools**: `list_templates`, `get_template`, `create_template`, `update_template`, `delete_template`, `stop_all_template_tasks`
- **Schedule tools**: `get_schedule`, `create_schedule`, `update_schedule`, `delete_schedule`
- **Task tools**: `list_tasks`, `list_last_tasks`, `get_task`, `start_task`, `stop_task`, `delete_task`, `get_task_output`
- **System tools**: `ping`, `get_info`, `list_events`, `list_last_events`, `list_apps`
- stdio and SSE transport support
- Docker image with multi-stage build
