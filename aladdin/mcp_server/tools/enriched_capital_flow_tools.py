"""MCP tools for the Aladdin Enriched Capital Flow API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_ENRICHED_CAPITAL_FLOW_BASE_PATH = "/api/clients/capital-flows/enriched-capital-flow/v1/"

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
    """Helper to call an Enriched Capital Flow API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_ENRICHED_CAPITAL_FLOW_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Enriched Capital Flow API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_enriched_capital_flow_tools(mcp: FastMCP) -> None:
    """Register Aladdin Enriched Capital Flow API tools with the MCP server."""

    @mcp.tool()
    def get_enriched_capital_flow(capital_flow_id: str) -> str:
        """Retrieve a capital flow transaction by its ID.

        Args:
            capital_flow_id: The unique ID of the capital flow transaction to retrieve.
        """
        return _call_api(
            f"/enrichedCapitalFlows/{capital_flow_id}",
            http_method="get",
        )

    @mcp.tool()
    def transition_enriched_capital_flow(
        enriched_capital_flow_id: str | None = None,
        primary_external_id: str | None = None,
        version: int | None = None,
        action: str | None = None,
        comment: str | None = None,
        rebook_primary_external_id: str | None = None,
    ) -> str:
        """Transition a capital flow to a given state.

        User requires standard newcash permissions to perform actions based on
        business workflow and user's role.

        Args:
            enriched_capital_flow_id: Capital flow transaction newcash ID.
            primary_external_id: Primary external identifier for the capital flow.
            version: Version of the capital flow record.
            action: The transition action to perform (e.g. ACTION_UNSPECIFIED,
                    ACTION_APPROVE, ACTION_REJECT, ACTION_CANCEL, etc.).
            comment: Optional comment for the transition.
            rebook_primary_external_id: Primary external ID for rebook operations.
        """
        transition: dict[str, Any] = {}
        if enriched_capital_flow_id is not None:
            transition["enrichedCapitalFlowId"] = enriched_capital_flow_id
        if primary_external_id is not None:
            transition["primaryExternalId"] = primary_external_id
        if version is not None:
            transition["version"] = version
        if action is not None:
            transition["action"] = action
        if comment is not None:
            transition["enrichedCapitalFlowComment"] = comment
        if rebook_primary_external_id is not None:
            transition["rebookPrimaryExternalId"] = rebook_primary_external_id

        body: dict[str, Any] = {"enrichedCapitalFlowTransition": transition}
        return _call_api("/enrichedCapitalFlow:transition", http_method="post", request_body=body)

    @mcp.tool()
    def batch_transition_enriched_capital_flows(
        transitions: list[dict[str, Any]],
    ) -> str:
        """Transition multiple capital flows to given states in a single batch.

        Args:
            transitions: List of transition dicts. Each dict can have:
                         enrichedCapitalFlowId (str), primaryExternalId (str),
                         version (int), action (str), enrichedCapitalFlowComment (str),
                         rebookPrimaryExternalId (str).
        """
        body: dict[str, Any] = {"enrichedCapitalFlowsTransitions": transitions}
        return _call_api("/enrichedCapitalFlows:batchTransition", http_method="post", request_body=body)

    @mcp.tool()
    def batch_validate_enriched_capital_flows(
        enriched_capital_flows: list[dict[str, Any]],
    ) -> str:
        """Validate all capital flows in a single batch.

        Args:
            enriched_capital_flows: List of enriched capital flow dicts to validate.
        """
        body: dict[str, Any] = {"enrichedCapitalFlows": enriched_capital_flows}
        return _call_api("/enrichedCapitalFlows:batchValidate", http_method="post", request_body=body)

    @mcp.tool()
    def filter_enriched_capital_flows(
        ids: list[str] | None = None,
        primary_external_ids: list[str] | None = None,
        organization_id: str | None = None,
        order_ids: list[str] | None = None,
        portfolio_tickers: list[str] | None = None,
        trade_date: str | None = None,
        portfolio_group_tickers: list[str] | None = None,
        modify_date: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter capital flows based on a search query.

        Args:
            ids: List of capital flow IDs to filter by.
            primary_external_ids: List of primary external IDs to filter by.
            organization_id: Organization ID to filter by.
            order_ids: List of order IDs to filter by.
            portfolio_tickers: List of portfolio tickers to filter by.
            trade_date: Trade date to filter by (date string).
            portfolio_group_tickers: List of portfolio group tickers to filter by.
            modify_date: Modify date to filter by (date string).
            page_size: Maximum number of records to return per page.
            page_token: Pagination token for retrieving the next page.
        """
        query: dict[str, Any] = {}
        if ids is not None:
            query["ids"] = ids
        if primary_external_ids is not None:
            query["primaryExternalIds"] = primary_external_ids
        if organization_id is not None:
            query["organizationId"] = organization_id
        if order_ids is not None:
            query["orderIds"] = order_ids
        if portfolio_tickers is not None:
            query["portfolioTickers"] = portfolio_tickers
        if trade_date is not None:
            query["tradeDate"] = trade_date
        if portfolio_group_tickers is not None:
            query["portfolioGroupTickers"] = portfolio_group_tickers
        if modify_date is not None:
            query["modifyDate"] = modify_date

        body: dict[str, Any] = {"enrichedCapitalFlowQuery": query}
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api("/enrichedCapitalFlows:filter", http_method="post", request_body=body)

    @mcp.tool()
    def filter_enriched_capital_flows_by_historical_transactions(
        enriched_capital_flow_id: str | None = None,
        enriched_capital_flow_version: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter capital flows historical records based on a search query.

        Args:
            enriched_capital_flow_id: The capital flow ID to look up history for.
            enriched_capital_flow_version: Specific version of the capital flow.
            page_size: Maximum number of records to return per page.
            page_token: Pagination token for retrieving the next page.
        """
        query: dict[str, Any] = {}
        if enriched_capital_flow_id is not None:
            query["enrichedCapitalFlowId"] = enriched_capital_flow_id
        if enriched_capital_flow_version is not None:
            query["enrichedCapitalFlowVersion"] = enriched_capital_flow_version

        body: dict[str, Any] = {"query": query}
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api(
            "/enrichedCapitalFlows:filterByHistoricalTransactions",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def import_enriched_capital_flows(
        enriched_capital_flows: list[dict[str, Any]],
        manual_state_cycle: bool = False,
    ) -> str:
        """Create or update multiple capital flow transactions via import.

        The id and primaryExternalId fields are not mandatory when creating
        new capital flow transactions.

        Args:
            enriched_capital_flows: List of enriched capital flow dicts to import.
            manual_state_cycle: When True, enables the API to respect the capital
                                flows state provided by the user in the request body.
        """
        body: dict[str, Any] = {
            "enrichedCapitalFlows": enriched_capital_flows,
            "manualStateCycle": manual_state_cycle,
        }
        return _call_api("/enrichedCapitalFlows:import", http_method="post", request_body=body)
