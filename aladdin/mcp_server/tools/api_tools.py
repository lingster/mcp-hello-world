import json

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_client: AladdinRestClient | None = None


def _get_client() -> AladdinRestClient:
    global _client
    if _client is None:
        _client = AladdinRestClient(
            default_web_server=server_config.default_web_server,
            oauth_config=server_config.oauth,
        )
    return _client


def register_api_tools(mcp: FastMCP) -> None:
    """Register Aladdin API tools with the MCP server."""

    @mcp.tool()
    def list_available_apis() -> str:
        """List all available Aladdin APIs from bundled swagger specifications.

        Returns a JSON list of APIs with their name, base_path, version and description.
        Use the base_path value when calling other API tools.
        """
        try:
            apis = _get_client().list_apis_from_swagger()
            return json.dumps({"apis": apis}, indent=2)
        except Exception as e:
            logger.error(f"Failed to list APIs: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def list_api_endpoints(base_path: str) -> str:
        """List all available endpoints for an Aladdin API.

        Args:
            base_path: API base path from list_available_apis (e.g. '/api/reference-architecture/demo/train-journey/v1/')
        """
        try:
            endpoints = _get_client().list_endpoints_from_swagger(base_path)
            return json.dumps({
                "base_path": base_path,
                "endpoints": endpoints,
            }, indent=2)
        except Exception as e:
            logger.error(f"Failed to list endpoints for {base_path}: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def get_api_endpoint_details(base_path: str, endpoint_path: str, http_method: str = "get") -> str:
        """Get parameter details for a specific API endpoint from its swagger specification.

        Args:
            base_path: API base path (e.g. '/api/reference-architecture/demo/train-journey/v1/')
            endpoint_path: Endpoint path (e.g. '/trainJourneys:filter')
            http_method: HTTP method (get, post, put, delete, patch)
        """
        try:
            details = _get_client().get_endpoint_details_from_swagger(base_path, endpoint_path, http_method)
            if details is None:
                return json.dumps({"error": f"Endpoint {http_method.upper()} {endpoint_path} not found"})
            return json.dumps(details, indent=2)
        except Exception as e:
            logger.error(f"Failed to get endpoint details: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def call_aladdin_api(
        base_path: str,
        endpoint_path: str,
        http_method: str = "get",
        request_body: dict | None = None,
        params: dict | None = None,
    ) -> str:
        """Call an Aladdin Graph API endpoint directly via REST.

        Use list_available_apis() to discover APIs and list_api_endpoints() to see
        available endpoints.

        Args:
            base_path: API base path (e.g. '/api/reference-architecture/demo/train-journey/v1/')
            endpoint_path: Swagger endpoint path (e.g. '/trainJourneys:filter')
            http_method: HTTP method - get, post, put, delete, patch
            request_body: Request body dict for POST/PUT/PATCH calls
            params: Query parameters dict
        """
        try:
            result = _get_client().call_api(
                base_path=base_path,
                endpoint_path=endpoint_path,
                http_method=http_method,
                request_body=request_body,
                params=params,
            )
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            logger.error(f"API call failed for {http_method.upper()} {base_path}{endpoint_path}: {e}")
            return json.dumps({"error": str(e)})
