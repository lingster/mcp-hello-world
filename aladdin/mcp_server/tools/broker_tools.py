"""MCP tools for the Aladdin Broker API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_BASE_PATH = "/api/investment-operations/reference-data/broker/v1/"

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
    """Helper to call a Broker API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Broker API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def _build_broker_dict(
    broker_ticker: str | None = None,
    broker_name: str | None = None,
    broker_type: str | None = None,
    broker_issuer_id: str | None = None,
    broker_id: str | None = None,
    broker_external_organisation_id: str | None = None,
    broker_portfolio_id: str | None = None,
    legal_entity_id: str | None = None,
    business_purpose: str | None = None,
    active: bool | None = None,
) -> dict[str, Any]:
    """Build a broker dict from optional fields, filtering out None values."""
    broker: dict[str, Any] = {}
    if broker_id is not None:
        broker["id"] = broker_id
    if broker_ticker is not None:
        broker["brokerTicker"] = broker_ticker
    if broker_name is not None:
        broker["brokerName"] = broker_name
    if broker_type is not None:
        broker["brokerType"] = broker_type
    if broker_issuer_id is not None:
        broker["brokerIssuerId"] = broker_issuer_id
    if broker_external_organisation_id is not None:
        broker["brokerExternalOrganisationId"] = broker_external_organisation_id
    if broker_portfolio_id is not None:
        broker["brokerPortfolioId"] = broker_portfolio_id
    if legal_entity_id is not None:
        broker["legalEntityId"] = legal_entity_id
    if business_purpose is not None:
        broker["businessPurpose"] = business_purpose
    if active is not None:
        broker["active"] = active
    return broker


def register_broker_tools(mcp: FastMCP) -> None:
    """Register Aladdin Broker API tools with the MCP server."""

    @mcp.tool()
    def get_broker(broker_id: str) -> str:
        """Get a broker by its broker ID.

        Args:
            broker_id: The unique ID (broker code) of the broker to retrieve.
        """
        return _call_api(
            f"/brokers/{broker_id}",
            http_method="get",
        )

    @mcp.tool()
    def batch_create_brokers(brokers: list[dict[str, Any]]) -> str:
        """Create one or more brokers in a single batch request (max 100).

        Required fields per broker: brokerName, brokerTicker, brokerType, brokerIssuerId.
        Users need permissions under permType='brkrMaint'.

        Args:
            brokers: List of broker dicts to create. Each dict can have:
                     brokerTicker (str), brokerName (str), brokerType (str),
                     brokerIssuerId (str), brokerPortfolioId (str),
                     legalEntityId (str), businessPurpose (str), active (bool).
                     Do NOT provide id or brokerExternalOrganisationId for create.
                     brokerPortfolioId should only be provided when brokerType is PORTFOLIO.
        """
        requests = [{"broker": b} for b in brokers]
        body: dict[str, Any] = {"requests": requests}
        return _call_api("/brokers:batchCreateBrokers", http_method="post", request_body=body)

    @mcp.tool()
    def batch_update_brokers(brokers: list[dict[str, Any]]) -> str:
        """Batch update one or more brokers (max 100).

        Required fields per broker: id, brokerName, brokerTicker, brokerType, brokerIssuerId.
        Users need permissions under permType='brkrMaint'.

        Args:
            brokers: List of broker dicts to update. Each dict can have:
                     id (str, required - broker code), brokerTicker (str),
                     brokerName (str), brokerType (str), brokerIssuerId (str),
                     brokerPortfolioId (str), legalEntityId (str),
                     businessPurpose (str), active (bool).
                     Do NOT provide brokerExternalOrganisationId or brokerPortfolioId.
        """
        requests = [{"broker": b} for b in brokers]
        body: dict[str, Any] = {"requests": requests}
        return _call_api("/brokers:batchUpdateBrokers", http_method="post", request_body=body)

    @mcp.tool()
    def batch_validate_brokers(
        brokers: list[dict[str, Any]],
        action_type: str = "ACTION_TYPE_UNSPECIFIED",
    ) -> str:
        """Validate multiple broker requests for create and update API calls.

        Args:
            brokers: List of broker dicts to validate. Each dict can have:
                     id (str), brokerTicker (str), brokerName (str),
                     brokerType (str), brokerIssuerId (str),
                     brokerExternalOrganisationId (str), brokerPortfolioId (str),
                     legalEntityId (str), businessPurpose (str), active (bool).
            action_type: Determines whether validation is for a create or update request.
                         One of: ACTION_TYPE_UNSPECIFIED, ACTION_TYPE_CREATE, ACTION_TYPE_UPDATE.
        """
        requests = [{"broker": b} for b in brokers]
        body: dict[str, Any] = {
            "requests": requests,
            "actionType": action_type,
        }
        return _call_api("/brokers:batchValidateBrokers", http_method="post", request_body=body)

    @mcp.tool()
    def filter_brokers(
        broker_tickers: list[str] | None = None,
        broker_type: str | None = None,
        defunct: bool | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter brokers by any combination of broker tickers, broker type, and defunct status.

        Args:
            broker_tickers: List of broker tickers to filter by.
            broker_type: Broker type to filter by.
            defunct: If true, load only defunct counterparties; if false, only non-defunct.
            page_size: Maximum number of brokers to return. If 0 or unspecified,
                       the complete list is returned.
            page_token: Page token from a previous FilterBrokers call for pagination.
        """
        query: dict[str, Any] = {}
        if broker_tickers is not None:
            query["brokerTickers"] = broker_tickers
        if broker_type is not None:
            query["brokerType"] = broker_type
        if defunct is not None:
            query["defunct"] = defunct

        body: dict[str, Any] = {}
        if query:
            body["query"] = query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api("/brokers:filter", http_method="post", request_body=body)

    @mcp.tool()
    def retrieve_broker_by_ticker(broker_ticker: str) -> str:
        """Retrieve a broker by an exact match on the broker ticker.

        Args:
            broker_ticker: The broker ticker to search for (exact match).
        """
        return _call_api(
            "/brokers:retrieveBrokerByTicker",
            http_method="get",
            params={"brokerTicker": broker_ticker},
        )

    @mcp.tool()
    def search_brokers(
        search: str,
        search_type: str | None = None,
        load_defunct: bool | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Search brokers based on an input query string (minimum two characters).

        Args:
            search: Search string (at least two characters).
            search_type: Type of search to perform. One of:
                         SEARCH_TYPE_UNSPECIFIED (defaults to BROKER),
                         SEARCH_TYPE_BROKER (searches brokerTicker, brokerName),
                         SEARCH_TYPE_ISSUER (searches issuer),
                         SEARCH_TYPE_LEI (searches legal entity identifier).
            load_defunct: If true, include defunct brokers in results;
                         if false, only return non-defunct brokers.
            page_size: Maximum number of brokers to return (max 100, default 100).
            page_token: Page token from a previous search call for pagination.
        """
        params: dict[str, Any] = {"search": search}
        if search_type is not None:
            params["searchType"] = search_type
        if load_defunct is not None:
            params["loadDefunct"] = load_defunct
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token is not None:
            params["pageToken"] = page_token

        return _call_api(
            "/brokers:search",
            http_method="get",
            params=params,
        )
