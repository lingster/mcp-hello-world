"""MCP tools for the Aladdin Portfolio Configuration API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_PORTFOLIO_CONFIGURATION_BASE_PATH = "/api/accounting/configuration/attribute/portfolio/records/v1/"

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
    """Helper to call a Portfolio Configuration API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_PORTFOLIO_CONFIGURATION_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Portfolio Configuration API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_portfolio_configuration_tools(mcp: FastMCP) -> None:
    """Register Aladdin Portfolio Configuration API tools with the MCP server."""

    @mcp.tool()
    def get_long_running_portfolio_configuration_record_status(
        request_id: str,
    ) -> str:
        """Retrieve the status and output from a long running configuration filter request.

        Use this to poll the result of a previously submitted long running
        configuration filter request by providing the request ID returned from
        submit_portfolio_configuration_records_request.

        Args:
            request_id: The ID of the long running operation to check status for.
        """
        return _call_api(
            f"/configurations/{request_id}:longRunningPortfolioConfigurationRecordStatus",
            http_method="get",
        )

    @mcp.tool()
    def filter_portfolio_configuration_records(
        tickers: list[str],
        process_codes: list[str],
        accounting_attribute_names: list[str] | None = None,
        accounting_attributes_value_criteria: dict[str, Any] | None = None,
        as_of_date: str | None = None,
        include_history: bool = False,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter portfolio configuration records based on tickers, process codes, and more.

        Best practices to limit query size:
          - Keep include_history as False.
          - Restrict the number of process codes in the request (max 5).
          - Keep the number of portfolio tickers to 350 per process code.
          - Restrict records by providing accounting_attribute_names.

        Args:
            tickers: List of portfolio tickers to filter on (required).
            process_codes: List of process codes (max 5). Refer to ALPHA_FLAGFINAL
                           decodes table for valid cde values.
            accounting_attribute_names: Limit which attributes to return (e.g.
                           ["basis", "alpha_price_group"]). If not provided, all
                           attributes are returned.
            accounting_attributes_value_criteria: Filter by specific attribute values.
                           Dict mapping attribute name to a list of values.
            as_of_date: Optional date string (YYYY-MM-DD). Defaults to current date.
            include_history: Whether to include history of attribute changes. Default False.
            page_size: Max number of tickers to return (max 100, default 100).
            page_token: Pagination token for retrieving subsequent pages.
        """
        query: dict[str, Any] = {
            "tickers": tickers,
            "processCodes": process_codes,
        }
        if accounting_attribute_names is not None:
            query["accountingAttributeNames"] = accounting_attribute_names
        if accounting_attributes_value_criteria is not None:
            query["accountingAttributesValueCriteria"] = accounting_attributes_value_criteria
        if as_of_date is not None:
            query["asOfDate"] = as_of_date
        if include_history:
            query["includeHistory"] = include_history

        body: dict[str, Any] = {"query": query}
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api(
            "/configurations:filter",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def submit_portfolio_configuration_records_request(
        tickers: list[str],
        process_codes: list[str],
        accounting_attribute_names: list[str] | None = None,
        accounting_attributes_value_criteria: dict[str, Any] | None = None,
        as_of_date: str | None = None,
        include_history: bool = False,
        expansion_type: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Submit a long running configuration filter request for large datasets.

        Use this for large requests with many portfolio tickers or a portfolio group.
        Returns a request ID that can be passed to
        get_long_running_portfolio_configuration_record_status to retrieve the output.

        Best practices to limit query size:
          - Keep include_history as False.
          - Restrict the number of process codes in the request (max 5).
          - Keep the number of portfolio tickers or portfolios in a port group
            limited to below 7500 per process code.
          - Restrict records by providing accounting_attribute_names.

        Args:
            tickers: List of portfolio tickers to filter on (required).
            process_codes: List of process codes (max 5). Refer to ALPHA_FLAGFINAL
                           decodes table for valid cde values.
            accounting_attribute_names: Limit which attributes to return (e.g.
                           ["basis", "alpha_price_group"]). If not provided, all
                           attributes are returned.
            accounting_attributes_value_criteria: Filter by specific attribute values.
                           Dict mapping attribute name to a list of values.
            as_of_date: Optional date string (YYYY-MM-DD). Defaults to current date.
            include_history: Whether to include history of attribute changes. Default False.
            expansion_type: Ticker expansion type. If not set, tickers are treated as
                           portfolios. Use this when specifying a portfolio group.
            page_size: Max number of tickers to return (max 100, default 100).
            page_token: Pagination token for retrieving subsequent pages.
        """
        query: dict[str, Any] = {
            "tickers": tickers,
            "processCodes": process_codes,
        }
        if accounting_attribute_names is not None:
            query["accountingAttributeNames"] = accounting_attribute_names
        if accounting_attributes_value_criteria is not None:
            query["accountingAttributesValueCriteria"] = accounting_attributes_value_criteria
        if as_of_date is not None:
            query["asOfDate"] = as_of_date
        if include_history:
            query["includeHistory"] = include_history
        if expansion_type is not None:
            query["expansionType"] = expansion_type

        body: dict[str, Any] = {"query": query}
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api(
            "/configurations:submitPortfolioConfigurationRecordsRequest",
            http_method="post",
            request_body=body,
        )
