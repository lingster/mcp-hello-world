import sys

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.config import server_config
from mcp_server.tools.adc_tools import register_adc_tools
from mcp_server.tools.api_tools import register_api_tools
from mcp_server.tools.storage_tools import register_storage_tools

logger.remove()
logger.add(sys.stderr, level="DEBUG" if server_config.debug else "INFO")


def create_mcp_server() -> FastMCP:
    """Create and configure the Aladdin MCP server."""
    mcp = FastMCP(
        name="aladdin-mcp",
        instructions=(
            "Aladdin MCP Server provides access to BlackRock's Aladdin platform. "
            "Use API tools to call Aladdin Graph APIs (with pagination and LRO support), "
            "ADC tools to query/write to Aladdin Data Cloud (Snowflake), "
            "and storage tools to manage S3 objects. "
            "Start by listing available APIs with list_available_apis(). "
            "Installed asdk_plugin_* packages are auto-discovered and available."
        ),
        host=server_config.host,
        port=server_config.port,
        streamable_http_path="/mcp",
    )

    register_api_tools(mcp)
    register_adc_tools(mcp)
    register_storage_tools(mcp)

    logger.info(f"Registered MCP tools: {[t.name for t in mcp._tool_manager.list_tools()]}")
    return mcp


mcp = create_mcp_server()


def main() -> None:
    """Run the MCP server with the configured transport."""
    transport = server_config.transport

    if transport == "stdio":
        logger.info("Starting Aladdin MCP server (stdio transport)")
        mcp.run(transport="stdio")
    elif transport in ("streamable-http", "sse"):
        logger.info(
            f"Starting Aladdin MCP server ({transport}) on "
            f"{server_config.host}:{server_config.port}"
        )
        mcp.run(transport=transport)
    else:
        logger.error(f"Unsupported transport: {transport}")
        sys.exit(1)


if __name__ == "__main__":
    main()
