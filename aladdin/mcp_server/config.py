import os
from typing import Literal

from pydantic import BaseModel, Field


class OAuthConfig(BaseModel):
    auth_type: Literal["OAuth", "Basic Auth"] = Field(
        default_factory=lambda: os.getenv("ASDK_API__AUTH_TYPE", "OAuth"),
    )
    auth_flow_type: Literal["refresh_token", "client_credentials"] = Field(
        default_factory=lambda: os.getenv("ASDK_API__AUTH_FLOW_TYPE", "refresh_token"),
    )
    client_id: str = Field(
        default_factory=lambda: os.getenv("ASDK_API__OAUTH__CLIENT_ID", ""),
    )
    client_secret: str = Field(
        default_factory=lambda: os.getenv("ASDK_API__OAUTH__CLIENT_SECRET", ""),
    )
    refresh_token: str = Field(
        default_factory=lambda: os.getenv("ASDK_API__OAUTH__REFRESH_TOKEN", ""),
    )
    access_token: str = Field(
        default_factory=lambda: os.getenv("ASDK_API__OAUTH__ACCESS_TOKEN", ""),
    )
    auth_server_url: str = Field(
        default_factory=lambda: os.getenv("ASDK_API__OAUTH__AUTH_SERVER_URL", ""),
    )
    auth_server_proxy: str = Field(
        default_factory=lambda: os.getenv("ASDK_API__OAUTH__AUTH_SERVER_PROXY", ""),
    )
    api_key: str = Field(
        default_factory=lambda: os.getenv("ASDK_API__TOKEN", ""),
    )
    username: str = Field(
        default_factory=lambda: os.getenv("ASDK_USER_CREDENTIALS__USERNAME", ""),
    )
    password: str = Field(
        default_factory=lambda: os.getenv("ASDK_USER_CREDENTIALS__PASSWORD", ""),
    )


class AdcConfig(BaseModel):
    account: str = Field(
        default_factory=lambda: os.getenv("ASDK_ADC__CONN__ACCOUNT", ""),
    )
    role: str = Field(
        default_factory=lambda: os.getenv("ASDK_ADC__CONN__ROLE", ""),
    )
    warehouse: str = Field(
        default_factory=lambda: os.getenv("ASDK_ADC__CONN__WAREHOUSE", ""),
    )
    database: str = Field(
        default_factory=lambda: os.getenv("ASDK_ADC__CONN__DATABASE", ""),
    )
    schema_name: str = Field(
        default_factory=lambda: os.getenv("ASDK_ADC__CONN__SCHEMA", ""),
    )
    authenticator: str = Field(
        default_factory=lambda: os.getenv("ASDK_ADC__CONN__AUTHENTICATOR", "oauth"),
    )
    oauth_access_token: str = Field(
        default_factory=lambda: os.getenv("ASDK_ADC__OAUTH__ACCESS_TOKEN", ""),
    )


class ServerConfig(BaseModel):
    host: str = Field(default_factory=lambda: os.getenv("MCP_HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("MCP_PORT", "8000")))
    transport: str = Field(default_factory=lambda: os.getenv("MCP_TRANSPORT", "streamable-http"))
    debug: bool = Field(default_factory=lambda: os.getenv("MCP_DEBUG", "false").lower() in ("true", "1"))

    default_web_server: str = Field(
        default_factory=lambda: os.getenv("defaultWebServer", ""),
        description="BlackRock client environment default web server",
    )

    oauth: OAuthConfig = Field(default_factory=OAuthConfig)
    adc: AdcConfig = Field(default_factory=AdcConfig)


server_config = ServerConfig()
