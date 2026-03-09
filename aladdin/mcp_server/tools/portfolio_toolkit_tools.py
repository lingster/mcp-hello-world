"""MCP tools for the Aladdin Portfolio Toolkit API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_PORTFOLIO_TOOLKIT_BASE_PATH = "/api/portfolio/setup/portfolio-toolkit/v1/"

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
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Portfolio Toolkit API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_PORTFOLIO_TOOLKIT_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Portfolio Toolkit API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_portfolio_toolkit_tools(mcp: FastMCP) -> None:
    """Register Aladdin Portfolio Toolkit API tools with the MCP server."""

    @mcp.tool()
    def filter_portfolio_identifiers(
        ids: list[str] | None = None,
        portfolio_id_type: str = "PORTFOLIO_ID_TYPE_UNSPECIFIED",
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter portfolio identifiers based on provided criteria.

        Returns portfolio identifiers matching the given IDs and type.
        Supports up to 20,000 identifiers in a single request.

        Args:
            ids: List of portfolio identifier strings to filter on.
            portfolio_id_type: Type of portfolio identifier. One of:
                PORTFOLIO_ID_TYPE_UNSPECIFIED,
                PORTFOLIO_ID_TYPE_PORTFOLIO_ID,
                PORTFOLIO_ID_TYPE_PORTFOLIO_TICKER,
                PORTFOLIO_ID_TYPE_ASSET_ID,
                PORTFOLIO_ID_TYPE_UUID.
            page_size: Max number of portfolios to return (max 10000, default 10000).
            page_token: Page token from a previous call for pagination.
        """
        query: dict[str, Any] = {"portfolioIdType": portfolio_id_type}
        if ids:
            query["ids"] = ids

        body: dict[str, Any] = {"query": query}
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api("/portfolioIdentifiers:filter", http_method="post", request_body=body)

    @mcp.tool()
    def get_portfolio(
        portfolio_id: str,
        decoded: bool = False,
    ) -> str:
        """Get a portfolio by its ID.

        Args:
            portfolio_id: The unique identifier of the portfolio.
            decoded: Whether to return decoded portfolio data.
        """
        params: dict[str, Any] = {}
        if decoded:
            params["decoded"] = decoded

        return _call_api(
            f"/portfolios/{portfolio_id}",
            http_method="get",
            params=params if params else None,
        )

    @mcp.tool()
    def filter_portfolios(
        portfolio_ids: list[str] | None = None,
        portfolio_group: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter portfolios based on provided criteria.

        Returns portfolios matching the given portfolio IDs or portfolio group.
        Maximum 500 portfolio IDs per request.

        Args:
            portfolio_ids: List of portfolio codes to filter on (max 500).
            portfolio_group: Portfolio group criteria string.
            page_size: Max number of portfolios to return.
            page_token: Page token from a previous call for pagination.
        """
        portfolio_query: dict[str, Any] = {}
        if portfolio_ids:
            portfolio_query["portfolioIds"] = {"portfolioIds": portfolio_ids}
        if portfolio_group is not None:
            portfolio_query["portfolioGroup"] = portfolio_group

        body: dict[str, Any] = {}
        if portfolio_query:
            body["portfolioQuery"] = portfolio_query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api("/portfolios:filter", http_method="post", request_body=body)

    @mcp.tool()
    def get_portfolio_slice(
        portfolio_id: str,
        slice_definition: str | None = None,
        fields: list[str] | None = None,
    ) -> str:
        """Get a portfolio slice, providing a view into a subset of portfolio data.

        A portfolio slice returns specific aspects of the portfolio such as
        summary or dynamic attributes.

        Args:
            portfolio_id: The unique identifier of the portfolio.
            slice_definition: The slice definition to return. One of:
                PORTFOLIO_SLICE_DEFINITION_UNSPECIFIED (defaults to SUMMARY),
                PORTFOLIO_SLICE_DEFINITION_SUMMARY,
                PORTFOLIO_SLICE_DEFINITION_DYNAMIC_ATTRIBUTES.
            fields: List of specific fields to include in the response.
        """
        params: dict[str, Any] = {}
        if slice_definition is not None:
            params["slice"] = slice_definition
        if fields is not None:
            params["fields"] = fields

        return _call_api(
            f"/portfolios/slices/{portfolio_id}",
            http_method="get",
            params=params if params else None,
        )

    @mcp.tool()
    def filter_portfolio_slices(
        portfolio_ids: list[str] | None = None,
        portfolio_group: str | None = None,
        slice_definition: str | None = None,
        fields: list[str] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter portfolio slices based on provided criteria.

        Returns portfolio slices matching the given portfolio IDs or group,
        with optional slice definition and field selection.

        Args:
            portfolio_ids: List of portfolio codes to filter on.
            portfolio_group: Portfolio group criteria string.
            slice_definition: The slice definition to return. One of:
                PORTFOLIO_SLICE_DEFINITION_UNSPECIFIED (defaults to SUMMARY),
                PORTFOLIO_SLICE_DEFINITION_SUMMARY,
                PORTFOLIO_SLICE_DEFINITION_DYNAMIC_ATTRIBUTES.
            fields: List of specific fields to include in the response.
            page_size: Max number of portfolio slices to return (max 500).
            page_token: Page token from a previous call for pagination.
        """
        portfolio_slice_query: dict[str, Any] = {}
        if portfolio_ids:
            portfolio_slice_query["portfolioIds"] = {"portfolioIds": portfolio_ids}
        if portfolio_group is not None:
            portfolio_slice_query["portfolioGroup"] = portfolio_group
        if slice_definition is not None:
            portfolio_slice_query["slice"] = slice_definition
        if fields is not None:
            portfolio_slice_query["fields"] = fields

        body: dict[str, Any] = {}
        if portfolio_slice_query:
            body["portfolioSliceQuery"] = portfolio_slice_query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api("/portfolios/slices:filter", http_method="post", request_body=body)

    @mcp.tool()
    def search_portfolios(
        search_string: str,
        search_type: str = "PORTFOLIO_SLICE_SUMMARY",
        max_rows: int | None = None,
    ) -> str:
        """Search portfolios by a search string.

        Currently supports PORTFOLIO_SLICE_SUMMARY search type only.

        Args:
            search_string: The search query string.
            search_type: The type of search to perform (default: PORTFOLIO_SLICE_SUMMARY).
            max_rows: Maximum number of rows to return.
        """
        params: dict[str, Any] = {
            "searchString": search_string,
            "searchType": search_type,
        }
        if max_rows is not None:
            params["maxRows"] = max_rows

        return _call_api(
            "/portfolios:search",
            http_method="get",
            params=params,
        )
