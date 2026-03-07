import os

from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    host: str = Field(default_factory=lambda: os.getenv("MCP_HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("MCP_PORT", "8000")))
    transport: str = Field(default_factory=lambda: os.getenv("MCP_TRANSPORT", "streamable-http"))
    debug: bool = Field(default_factory=lambda: os.getenv("MCP_DEBUG", "false").lower() in ("true", "1"))

    # Aladdin API settings
    default_web_server: str = Field(
        default_factory=lambda: os.getenv("defaultWebServer", ""),
        description="BlackRock client environment default web server",
    )

    # Auth settings
    auth_type: str = Field(
        default_factory=lambda: os.getenv("ASDK_API__AUTH_TYPE", "OAuth"),
        description="API auth type: 'OAuth' or 'Basic Auth'",
    )
    auth_flow_type: str = Field(
        default_factory=lambda: os.getenv("ASDK_API__AUTH_FLOW_TYPE", "refresh_token"),
        description="OAuth flow type: 'refresh_token' or 'client_credentials'",
    )
    oauth_client_id: str | None = Field(
        default_factory=lambda: os.getenv("ASDK_OAUTH__CLIENT_ID"),
    )
    oauth_client_secret: str | None = Field(
        default_factory=lambda: os.getenv("ASDK_OAUTH__CLIENT_SECRET"),
    )
    oauth_refresh_token: str | None = Field(
        default_factory=lambda: os.getenv("ASDK_OAUTH__REFRESH_TOKEN"),
    )
    oauth_access_token: str | None = Field(
        default_factory=lambda: os.getenv("ASDK_OAUTH__ACCESS_TOKEN"),
    )
    oauth_auth_server_url: str | None = Field(
        default_factory=lambda: os.getenv("ASDK_OAUTH__AUTH_SERVER_URL"),
    )
    oauth_auth_server_proxy: str | None = Field(
        default_factory=lambda: os.getenv("ASDK_OAUTH__AUTH_SERVER_PROXY"),
    )
    api_key: str | None = Field(
        default_factory=lambda: os.getenv("ASDK_API__TOKEN"),
    )
    username: str | None = Field(
        default_factory=lambda: os.getenv("ASDK_USER_CREDENTIALS__USERNAME"),
    )
    password: str | None = Field(
        default_factory=lambda: os.getenv("ASDK_USER_CREDENTIALS__PASSWORD"),
    )

    # ADC (Snowflake) settings
    adc_account: str | None = Field(
        default_factory=lambda: os.getenv("ASDK_ADC__CONN__ACCOUNT"),
    )
    adc_role: str | None = Field(
        default_factory=lambda: os.getenv("ASDK_ADC__CONN__ROLE"),
    )
    adc_warehouse: str | None = Field(
        default_factory=lambda: os.getenv("ASDK_ADC__CONN__WAREHOUSE"),
    )
    adc_database: str | None = Field(
        default_factory=lambda: os.getenv("ASDK_ADC__CONN__DATABASE"),
    )
    adc_schema: str | None = Field(
        default_factory=lambda: os.getenv("ASDK_ADC__CONN__SCHEMA"),
    )


server_config = ServerConfig()
