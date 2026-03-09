"""MCP tools for the Aladdin Valuations API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_VALUATIONS_BASE_PATH = "/api/accounting/workflow/valuations/v1/"

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


def _call_valuations_api(
    endpoint_path: str,
    http_method: str = "get",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Valuations API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_VALUATIONS_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Valuations API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_valuations_tools(mcp: FastMCP) -> None:
    """Register Aladdin Valuations API tools with the MCP server."""

    @mcp.tool()
    def get_valuation(valuation_id: str) -> str:
        """Get a single valuation by its ID.

        Retrieves detailed valuation data including NAV, returns, workflow status,
        and other accounting valuation information.

        Args:
            valuation_id: The unique ID of the valuation to retrieve.
        """
        return _call_valuations_api(
            f"/valuation/{valuation_id}",
            http_method="get",
        )

    @mcp.tool()
    def list_valuation_exceptions(
        parent: str,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """List exceptions for a given valuation.

        Retrieves NAV log exception records associated with a valuation,
        including exception type, status, priority, and NAV impact.

        Args:
            parent: The parent valuation ID to list exceptions for.
            page_size: Maximum number of exceptions to return per page.
            page_token: Token for retrieving the next page of results.
        """
        params: dict[str, Any] = {}
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token is not None:
            params["pageToken"] = page_token

        return _call_valuations_api(
            f"/valuations/{parent}/valuationExceptions",
            http_method="get",
            params=params if params else None,
        )

    @mcp.tool()
    def filter_valuations(
        portfolio_tickers: list[str] | None = None,
        portfolio_ids: list[str] | None = None,
        valuation_ids: list[int] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        process_types: list[str] | None = None,
        nav_statuses: list[str] | None = None,
        workflow_status: str | None = None,
        sort_columns: list[str] | None = None,
        max_record: int | None = None,
        expansion_type: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter and search for valuations across portfolios.

        Retrieves accounting valuations data filtered by portfolio, date range,
        process type, NAV status, and other criteria.

        Args:
            portfolio_tickers: List of portfolio tickers to filter by.
            portfolio_ids: List of portfolio codes to filter by.
            valuation_ids: List of valuation IDs to retrieve (max 5000).
            start_date: Start date filter (YYYY-MM-DD).
            end_date: End date filter (YYYY-MM-DD).
            process_types: List of process types to filter by
                           (see ALPHA_FLAGFINAL decodes table).
            nav_statuses: List of NAV statuses to filter by
                          (see NAV_STATUS decodes table, use cde values).
            workflow_status: Workflow status to filter by
                             (see NAV_STATUS decodes table, use decde values).
            sort_columns: Columns to sort by with optional direction prefix.
                          Format: +col1, -col2, col3 (+ ascending, - descending).
                          Allowed columns: exceptionCount, navId, fund, valueDate,
                          snapTime, flagFinal, startDate, startSnapTime, status,
                          modifyTime, portfolioName.
            max_record: Maximum number of valuations to fetch.
            expansion_type: Ticker expansion type (optional).
            page_size: Maximum number of valuations per page (max 100).
            page_token: Token for retrieving the next page of results.
        """
        query: dict[str, Any] = {}
        if portfolio_tickers is not None:
            query["portfolioTickers"] = portfolio_tickers
        if portfolio_ids is not None:
            query["portfolioIds"] = portfolio_ids
        if valuation_ids is not None:
            query["valuationIds"] = valuation_ids
        if start_date is not None:
            query["startDate"] = start_date
        if end_date is not None:
            query["endDate"] = end_date
        if process_types is not None:
            query["processTypes"] = process_types
        if nav_statuses is not None:
            query["navStatuses"] = nav_statuses
        if workflow_status is not None:
            query["workflowStatus"] = workflow_status
        if sort_columns is not None:
            query["sortColumns"] = sort_columns
        if max_record is not None:
            query["maxRecord"] = max_record
        if expansion_type is not None:
            query["expansionType"] = expansion_type

        body: dict[str, Any] = {}
        if query:
            body["query"] = query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_valuations_api(
            "/valuations:filter",
            http_method="post",
            request_body=body,
        )
