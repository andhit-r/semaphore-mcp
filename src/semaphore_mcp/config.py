"""Konfigurasi runtime Semaphore MCP Server.

Dua kelas settings terpisah:

- ``SemaphoreConfig`` — konfigurasi koneksi ke backend Semaphore UI (prefix ``SEMAPHORE_``).
- ``MCPSettings``     — konfigurasi layer MCP: transport, auth Authentik, API key
                        (env vars tanpa prefix: ``MCP_*``, ``AUTHENTIK_*``).

Keduanya dibaca dari environment / file ``.env`` dan diinstansiasi sebagai singleton.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class SemaphoreConfig(BaseSettings):
    """Konfigurasi koneksi ke Semaphore UI REST API.

    Attributes:
        url: Base URL Semaphore (mis. ``http://localhost:3000``).
        api_token: API token Bearer. Bila diisi, username/password diabaikan.
        username: Username admin untuk session-based auth.
        password: Password admin (tidak pernah di-log).
        timeout: Timeout request HTTP ke Semaphore (detik).
        verify_ssl: Verifikasi TLS certificate server Semaphore.
    """

    url: str = "http://localhost:3000"
    api_token: SecretStr | None = None
    username: str = "admin"
    password: SecretStr = SecretStr("changeme")
    timeout: float = 30.0
    verify_ssl: bool = True

    model_config = SettingsConfigDict(
        env_prefix="SEMAPHORE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class MCPSettings(BaseSettings):
    """Konfigurasi layer MCP server: transport, Authentik OAuth, dan API key.

    Attributes:
        mcp_server_name: Nama server yang ditampilkan ke MCP client.
        mcp_log_level: Level logging (DEBUG, INFO, WARNING, ERROR).
        mcp_transport: Transport saat dijalankan via ``python -m semaphore_mcp``
            (``stdio`` default, atau ``http``/``sse``).
        mcp_host: Host bind saat transport http/sse.
        mcp_port: Port saat transport http/sse.
        mcp_base_url: URL publik MCP server. WAJIB diisi agar OAuth Authentik
            (Claude.ai) berfungsi. Contoh: ``https://mcp.example.com``.
        authentik_base_url: URL dasar Authentik, contoh ``https://auth.example.com``.
        authentik_app_slug: Slug OAuth2/OIDC Provider di Authentik.
        authentik_client_id: Client ID dari Authentik OAuth2 Provider.
        authentik_client_secret: Client Secret dari Authentik OAuth2 Provider.
        authentik_allowed_usernames: Daftar ``preferred_username`` yang diizinkan
            (kosong = semua user yang lolos policy Authentik diizinkan). Diterima
            dalam tiga format: JSON array (``["alice","bob"]``),
            comma-separated (``alice,bob``), atau nilai tunggal (``alice``).
        mcp_api_key: API key statis untuk klien non-OAuth (VS Code/CLI).
    """

    mcp_server_name: str = "Semaphore UI MCP"
    mcp_log_level: str = "INFO"

    mcp_transport: str = "stdio"
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8000

    mcp_base_url: str | None = None
    authentik_base_url: str | None = None
    authentik_app_slug: str | None = None
    authentik_client_id: str | None = None
    authentik_client_secret: str | None = None
    authentik_allowed_usernames: list[str] = []

    mcp_api_key: str | None = None

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: Any,
        env_settings: Any,
        dotenv_settings: Any,
        file_secret_settings: Any,
    ) -> tuple:
        """Terima ``authentik_allowed_usernames`` sebagai JSON / comma-separated / tunggal.

        pydantic-settings mencoba ``json.loads()`` pada field ``list[str]`` di level
        source SEBELUM validator berjalan. Tanpa patch ini, plain string seperti
        ``akadmin`` atau ``akadmin,user2`` melempar ``JSONDecodeError`` saat startup.

        PENTING: patch dikenakan ke DUA source — ``env_settings`` (OS environment)
        DAN ``dotenv_settings`` (file ``.env``) — agar alur baku "salin .env.example
        menjadi .env" tidak crash lewat DotEnvSettingsSource.
        """

        def _lenient(source: Any) -> Any:
            """Patch ``decode_complex_value`` pada ``source`` agar toleran string non-JSON."""
            original = source.decode_complex_value

            def decode(field_name: str, field: Any, value: Any) -> Any:
                """Konversi plain string / CSV ke list untuk ``authentik_allowed_usernames``."""
                if field_name == "authentik_allowed_usernames" and isinstance(value, str):
                    v = value.strip()
                    if not v:
                        return []
                    if not v.startswith("["):
                        return [u.strip() for u in v.split(",") if u.strip()]
                return original(field_name, field, value)

            source.decode_complex_value = decode
            return source

        return (
            init_settings,
            _lenient(env_settings),
            _lenient(dotenv_settings),
            file_secret_settings,
        )

    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


_semaphore_config: SemaphoreConfig | None = None
_mcp_settings: MCPSettings | None = None


def get_config() -> SemaphoreConfig:
    """Kembalikan singleton :class:`SemaphoreConfig`, buat bila belum ada.

    Returns:
        Konfigurasi koneksi Semaphore yang sudah diinisialisasi dari env / ``.env``.
    """
    global _semaphore_config
    if _semaphore_config is None:
        _semaphore_config = SemaphoreConfig()
    return _semaphore_config


def get_mcp_settings() -> MCPSettings:
    """Kembalikan singleton :class:`MCPSettings`, buat bila belum ada.

    Returns:
        Konfigurasi layer MCP (transport, auth, API key) yang aktif.
    """
    global _mcp_settings
    if _mcp_settings is None:
        _mcp_settings = MCPSettings()
    return _mcp_settings


def reset_config() -> None:
    """Reset kedua singleton ke ``None`` agar instance baru dibuat di panggilan berikutnya.

    Note:
        Hanya untuk keperluan pengujian. Jangan dipanggil saat runtime produksi.
    """
    global _semaphore_config, _mcp_settings
    _semaphore_config = None
    _mcp_settings = None


# Singleton siap diimpor langsung
settings = MCPSettings()
