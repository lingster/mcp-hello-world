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
            lro_config=server_config.lro,
            pagination_config=server_config.pagination,
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

    @mcp.tool()
    def call_aladdin_api_with_pagination(
        base_path: str,
        endpoint_path: str,
        http_method: str = "get",
        request_body: dict | None = None,
        params: dict | None = None,
        page_size: int | None = None,
        max_pages: int | None = None,
    ) -> str:
        """Call an Aladdin Graph API with automatic pagination.

        Automatically follows nextPageToken across multiple pages and returns
        all pages collected. Use this instead of call_aladdin_api when you expect
        large result sets.

        Args:
            base_path: API base path (e.g. '/api/reference-architecture/demo/train-journey/v1/')
            endpoint_path: Swagger endpoint path (e.g. '/trainJourneys:filter')
            http_method: HTTP method - get, post, put, delete, patch
            request_body: Request body dict for POST/PUT/PATCH calls
            params: Query parameters dict
            page_size: Number of results per page (default: 100)
            max_pages: Maximum number of pages to fetch (default: 10)
        """
        try:
            pages = _get_client().call_api_with_pagination(
                base_path=base_path,
                endpoint_path=endpoint_path,
                http_method=http_method,
                request_body=request_body,
                params=params,
                page_size=page_size,
                max_pages=max_pages,
            )
            return json.dumps({
                "total_pages": len(pages),
                "pages": pages,
            }, indent=2, default=str)
        except Exception as e:
            logger.error(f"Paginated API call failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def poll_long_running_operation(
        base_path: str,
        lro_id: str,
        status_endpoint: str = "/longRunningOperations/{id}",
        check_interval: int | None = None,
        timeout: int | None = None,
    ) -> str:
        """Poll a long-running operation (LRO) until it completes.

        Some Aladdin APIs return long-running operations that must be polled
        for completion. Use this tool to wait for an LRO to finish.

        Args:
            base_path: API base path (e.g. '/api/reference-architecture/demo/train-journey/v1/')
            lro_id: The long-running operation ID returned by the initial API call
            status_endpoint: Endpoint template for checking status (must contain {id})
            check_interval: Seconds between status checks (default: 10)
            timeout: Maximum seconds to wait before timing out (default: 300)
        """
        try:
            result = _get_client().poll_lro(
                base_path=base_path,
                lro_id=lro_id,
                status_endpoint=status_endpoint,
                check_interval=check_interval,
                timeout=timeout,
            )
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            logger.error(f"LRO polling failed for {lro_id}: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def start_and_poll_long_running_operation(
        base_path: str,
        start_endpoint: str,
        status_endpoint: str = "/longRunningOperations/{id}",
        http_method: str = "post",
        request_body: dict | None = None,
        params: dict | None = None,
        check_interval: int | None = None,
        timeout: int | None = None,
    ) -> str:
        """Start a long-running operation and automatically poll until completion.

        Combines starting an LRO and polling for its result in a single call.
        The operation is started using the start_endpoint, then automatically
        polled via the status_endpoint until done or timed out.

        Args:
            base_path: API base path (e.g. '/api/reference-architecture/demo/train-journey/v1/')
            start_endpoint: Endpoint to start the LRO (e.g. '/trainJourneys:batchProcess')
            status_endpoint: Endpoint template for checking status (must contain {id})
            http_method: HTTP method for starting the LRO (usually post)
            request_body: Request body for starting the LRO
            params: Query parameters for starting the LRO
            check_interval: Seconds between status checks (default: 10)
            timeout: Maximum seconds to wait before timing out (default: 300)
        """
        try:
            result = _get_client().start_and_poll_lro(
                base_path=base_path,
                start_endpoint=start_endpoint,
                status_endpoint=status_endpoint,
                http_method=http_method,
                request_body=request_body,
                params=params,
                check_interval=check_interval,
                timeout=timeout,
            )
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            logger.error(f"LRO start+poll failed: {e}")
            return json.dumps({"error": str(e)})
