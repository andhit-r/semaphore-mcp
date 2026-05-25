"""Configuration management for the Semaphore MCP server.

All settings are read from environment variables with the ``SEMAPHORE_``
prefix (and ``SEMAPHORE_TRANSPORT`` / ``SEMAPHORE_HOST`` / ``SEMAPHORE_PORT``
for server transport).
"""

import logging

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class SemaphoreConfig(BaseSettings):
    """Runtime configuration loaded from environment variables.

    Parameters
    ----------
    url : str
        Base URL of the Semaphore web application (e.g. ``http://localhost:3000``).
    api_token : SecretStr | None
        API token for Bearer authentication.  When set, username/password
        are ignored.
    username : str
        Administrator username used for session-based authentication.
    password : SecretStr
        Administrator password (never logged).
    timeout : float
        HTTP request timeout in seconds.
    verify_ssl : bool
        Whether to verify TLS certificates for the Semaphore server.
    transport : str
        MCP transport mode: ``stdio`` (default) or ``sse``.
    host : str
        Bind host when ``transport=sse``.
    port : int
        Bind port when ``transport=sse``.
    """

    url: str = "http://localhost:3000"
    api_token: SecretStr | None = None
    username: str = "admin"
    password: SecretStr = SecretStr("changeme")
    timeout: float = 30.0
    verify_ssl: bool = True
    transport: str = "stdio"
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_prefix="SEMAPHORE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


_config: SemaphoreConfig | None = None


def get_config() -> SemaphoreConfig:
    """Return the singleton :class:`SemaphoreConfig` instance.

    The instance is lazily created on first call and cached for the lifetime
    of the process.

    Returns
    -------
    SemaphoreConfig
        The active configuration object.
    """
    global _config
    if _config is None:
        _config = SemaphoreConfig()
    return _config


def reset_config() -> None:
    """Reset the cached config singleton (useful in tests)."""
    global _config
    _config = None
