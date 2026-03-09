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


class S3Config(BaseModel):
    endpoint_url: str = Field(
        default_factory=lambda: os.getenv("ASDK_STORAGE__S3__ENDPOINT_URL", ""),
    )
    access_key_id: str = Field(
        default_factory=lambda: os.getenv("ASDK_STORAGE__S3__ACCESS_KEY_ID", ""),
    )
    secret_access_key: str = Field(
        default_factory=lambda: os.getenv("ASDK_STORAGE__S3__SECRET_ACCESS_KEY", ""),
    )
    bucket_name: str = Field(
        default_factory=lambda: os.getenv("ASDK_STORAGE__S3__BUCKET_NAME", ""),
    )


class LroConfig(BaseModel):
    status_check_interval: int = Field(
        default_factory=lambda: int(os.getenv("ASDK_API__LRO__STATUS_CHECK_INTERVAL", "10")),
    )
    status_check_timeout: int = Field(
        default_factory=lambda: int(os.getenv("ASDK_API__LRO__STATUS_CHECK_TIMEOUT", "300")),
    )


class PaginationConfig(BaseModel):
    max_page_size: int = Field(
        default_factory=lambda: int(os.getenv("ASDK_API__PAGINATION__MAX_PAGE_SIZE", "100")),
    )
    max_pages: int = Field(
        default_factory=lambda: int(os.getenv("ASDK_API__PAGINATION__MAX_PAGES", "10")),
    )
    timeout: int = Field(
        default_factory=lambda: int(os.getenv("ASDK_API__PAGINATION__TIMEOUT", "300")),
    )
    interval: int = Field(
        default_factory=lambda: int(os.getenv("ASDK_API__PAGINATION__INTERVAL", "0")),
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
    s3: S3Config = Field(default_factory=S3Config)
    lro: LroConfig = Field(default_factory=LroConfig)
    pagination: PaginationConfig = Field(default_factory=PaginationConfig)


server_config = ServerConfig()
