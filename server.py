"""Hello World MCP Server for use with Microsoft Copilot in VS Code."""

import sys

from loguru import logger
from mcp.server.fastmcp import FastMCP

# Configure loguru to write to stderr (required for STDIO transport)
logger.remove()
logger.add(sys.stderr, level="INFO")

mcp = FastMCP("hello-world")


@mcp.tool()
def hello(name: str = "World") -> str:
    """Say hello to someone.

    Args:
        name: The name to greet. Defaults to 'World'.
    """
    logger.info(f"Greeting {name}")
    return f"Hello, {name}!"


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together.

    Args:
        a: First number.
        b: Second number.
    """
    logger.info(f"Adding {a} + {b}")
    return a + b


if __name__ == "__main__":
    mcp.run(transport="stdio")
