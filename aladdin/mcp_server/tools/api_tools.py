import json

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.config import server_config


def register_api_tools(mcp: FastMCP) -> None:
    """Register Aladdin API tools with the MCP server."""

    @mcp.tool()
    def list_available_apis() -> str:
        """List all available Aladdin APIs registered in the SDK.

        Returns a JSON list of API names that can be used with the other API tools.
        """
        from aladdinsdk.api.registry import get_api_names

        try:
            api_names = get_api_names()
            return json.dumps({"apis": api_names}, indent=2)
        except Exception as e:
            logger.error(f"Failed to list APIs: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def list_api_endpoints(api_name: str) -> str:
        """List all available endpoint methods for a given Aladdin API.

        Args:
            api_name: Name of the API (e.g. 'TrainJourneyAPI', 'TokenAPI')
        """
        from aladdinsdk.api.client import AladdinAPI

        try:
            api = AladdinAPI(api_name, default_web_server=server_config.default_web_server)
            methods = api.get_api_endpoint_methods()
            paths = api.get_api_endpoint_path_tuples()
            return json.dumps({
                "api_name": api_name,
                "endpoint_methods": methods,
                "endpoint_paths": [{"path": p[0], "method": p[1]} for p in paths],
            }, indent=2)
        except Exception as e:
            logger.error(f"Failed to list endpoints for {api_name}: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def get_api_endpoint_signature(api_name: str, endpoint_method: str) -> str:
        """Get the method signature for a specific API endpoint, showing required and optional parameters.

        Args:
            api_name: Name of the API (e.g. 'TrainJourneyAPI')
            endpoint_method: Name of the endpoint method (e.g. 'filter_train_journeys')
        """
        from aladdinsdk.api.client import AladdinAPI

        try:
            api = AladdinAPI(api_name, default_web_server=server_config.default_web_server)
            sig = api.get_api_endpoint_signature(endpoint_method)
            return json.dumps({
                "api_name": api_name,
                "endpoint": endpoint_method,
                "signature": str(sig),
            }, indent=2)
        except Exception as e:
            logger.error(f"Failed to get signature for {api_name}.{endpoint_method}: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def call_aladdin_api(
        api_name: str,
        endpoint: str,
        http_method: str = "get",
        request_body: dict | None = None,
        params: dict | None = None,
    ) -> str:
        """Call an Aladdin Graph API endpoint.

        Use list_available_apis() to discover APIs, list_api_endpoints() to see
        available endpoints, and get_api_endpoint_signature() to see parameters.

        Args:
            api_name: Name of the API (e.g. 'TrainJourneyAPI')
            endpoint: Endpoint method name (e.g. 'filter_train_journeys') or swagger path (e.g. '/train-journeys:filter')
            http_method: HTTP method - get, post, put, delete, patch. Only needed when using swagger path.
            request_body: Request body dict for POST/PUT/PATCH calls
            params: Additional keyword parameters for the API call
        """
        from aladdinsdk.api.client import AladdinAPI

        if params is None:
            params = {}

        try:
            api = AladdinAPI(api_name, default_web_server=server_config.default_web_server)

            # Determine how to call the endpoint
            if endpoint.startswith("/"):
                api_endpoint = (endpoint, http_method)
            else:
                api_endpoint = endpoint

            result = api.call_api(
                api_endpoint,
                request_body=request_body,
                _deserialize_to_object=False,
                **params,
            )

            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            logger.error(f"API call failed for {api_name}/{endpoint}: {e}")
            return json.dumps({"error": str(e)})
