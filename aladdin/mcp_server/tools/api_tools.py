import json

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server import rest_client


def register_api_tools(mcp: FastMCP) -> None:
    """Register Aladdin API tools with the MCP server."""

    @mcp.tool()
    def list_available_apis() -> str:
        """List all available Aladdin APIs registered in the server.

        Returns a JSON list of API names that can be used with the other API tools.
        """
        try:
            api_names = rest_client.list_api_names()
            return json.dumps({"apis": api_names}, indent=2)
        except Exception as e:
            logger.error(f"Failed to list APIs: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def list_api_endpoints(api_name: str) -> str:
        """List all available endpoint paths for a given Aladdin API.

        Args:
            api_name: Name of the API (e.g. 'TrainJourneyAPI', 'TokenAPI')
        """
        try:
            endpoints = rest_client.get_api_endpoints(api_name)
            base_url = rest_client.get_api_base_url(api_name)
            return json.dumps({
                "api_name": api_name,
                "base_url": base_url,
                "endpoints": endpoints,
            }, indent=2)
        except Exception as e:
            logger.error(f"Failed to list endpoints for {api_name}: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def get_api_endpoint_schema(api_name: str, endpoint_path: str, http_method: str = "get") -> str:
        """Get the schema for a specific API endpoint, showing parameters and response shape.

        Args:
            api_name: Name of the API (e.g. 'TrainJourneyAPI')
            endpoint_path: Swagger path (e.g. '/trainJourneys:filter')
            http_method: HTTP method - get, post, put, delete, patch
        """
        try:
            schema = rest_client.get_endpoint_schema(api_name, endpoint_path, http_method)
            return json.dumps({
                "api_name": api_name,
                "endpoint": endpoint_path,
                "method": http_method,
                "schema": schema,
            }, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to get schema for {api_name} {endpoint_path}: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def call_aladdin_api(
        api_name: str,
        endpoint: str,
        http_method: str = "GET",
        request_body: dict | None = None,
        query_params: dict | None = None,
    ) -> str:
        """Call an Aladdin Graph API endpoint via direct REST.

        Use list_available_apis() to discover APIs, list_api_endpoints() to see
        available endpoints, and get_api_endpoint_schema() to see parameters.

        Args:
            api_name: Name of the API (e.g. 'TrainJourneyAPI')
            endpoint: Swagger path (e.g. '/trainJourneys:filter')
            http_method: HTTP method - GET, POST, PUT, DELETE, PATCH
            request_body: Request body dict for POST/PUT/PATCH calls
            query_params: Query parameters for the API call
        """
        try:
            result = rest_client.call_api(
                api_name=api_name,
                endpoint_path=endpoint,
                http_method=http_method,
                request_body=request_body,
                query_params=query_params,
            )
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            logger.error(f"API call failed for {api_name}{endpoint}: {e}")
            return json.dumps({"error": str(e)})
