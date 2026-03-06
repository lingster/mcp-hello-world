import os

from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    host: str = Field(default_factory=lambda: os.getenv("MCP_HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("MCP_PORT", "8000")))
    transport: str = Field(default_factory=lambda: os.getenv("MCP_TRANSPORT", "streamable-http"))
    debug: bool = Field(default_factory=lambda: os.getenv("MCP_DEBUG", "false").lower() in ("true", "1"))

    # Aladdin SDK settings
    default_web_server: str = Field(
        default_factory=lambda: os.getenv("defaultWebServer", ""),
        description="BlackRock client environment default web server",
    )


server_config = ServerConfig()
