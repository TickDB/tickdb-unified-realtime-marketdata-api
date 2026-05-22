from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # TickDB API key — required; register at https://tickdb.ai to obtain one
    tickdb_api_key: str = ""

    # MCP server access control — empty = open access
    mcp_access_token: str = ""

    # Logging level: DEBUG, INFO, WARNING, ERROR
    log_level: str = "INFO"

    # Log file retention: number of days to keep rotated log files
    log_retain_days: int = 7

    # Transport: "streamable-http" (remote) or "stdio" (local Claude Desktop)
    mcp_transport: str = "streamable-http"
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8000


settings = Settings()
