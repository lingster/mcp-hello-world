"""MCP tools for the Aladdin Composite Membership API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_COMPOSITE_MEMBERSHIP_BASE_PATH = "/api/accounting/configuration/composite-membership/v1/"

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


def _call_api(
    endpoint_path: str,
    http_method: str = "get",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Composite Membership API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_COMPOSITE_MEMBERSHIP_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Composite Membership API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_composite_membership_tools(mcp: FastMCP) -> None:
    """Register Aladdin Composite Membership API tools with the MCP server."""

    @mcp.tool()
    def list_composite_memberships(
        parent: str,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Gets membership for a given composite.

        Returns the list of portfolio memberships associated with the specified
        composite ticker, including entry/exit dates, reasons, and comments.

        Args:
            parent: The composite ticker to retrieve memberships for.
            page_size: The maximum number of composite memberships to return.
                       Maximum value is 1000, default is 100.
            page_token: A page token received from a previous ListCompositeMemberships
                        call to retrieve the next page of results.
        """
        params: dict[str, Any] = {}
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token is not None:
            params["pageToken"] = page_token

        return _call_api(
            f"/portfolios/{parent}/compositeMemberships",
            http_method="get",
            params=params if params else None,
        )
