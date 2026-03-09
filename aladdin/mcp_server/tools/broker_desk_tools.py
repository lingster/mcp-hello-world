"""MCP tools for the Aladdin Broker Desk API."""

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
    """Helper to call a Broker Desk API endpoint and return JSON string."""
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
        logger.error(f"Broker Desk API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def _build_broker_desk_dict(desk: dict[str, Any]) -> dict[str, Any]:
    """Normalize a broker desk dict, filtering out None values."""
    cleaned: dict[str, Any] = {}
    for key in (
        "id",
        "brokerId",
        "brokerEntity",
        "deskType",
        "assistantId",
        "salesmanId",
        "deskRule",
        "deskCode",
    ):
        if desk.get(key) is not None:
            cleaned[key] = desk[key]
    return cleaned


def register_broker_desk_tools(mcp: FastMCP) -> None:
    """Register Aladdin Broker Desk API tools with the MCP server."""

    @mcp.tool()
    def batch_create_broker_desks(
        broker_ticker: str,
        requests: list[dict[str, Any]],
        broker_id: str | None = None,
        skip_bql_validation: bool | None = None,
    ) -> str:
        """Create one or more broker desks (max 100 per request).

        Required fields per broker desk: brokerTicker, deskType.
        Users need permissions under permType='brkrDskCon'.

        Args:
            broker_ticker: Broker ticker.
            requests: List of create requests. Each dict should contain a 'brokerDesk'
                      key with fields: deskType (str, required), brokerEntity (str),
                      assistantId (str), salesmanId (str), deskRule (str), deskCode (str).
            broker_id: Aladdin Broker Identifier (numeric). Not supported currently.
            skip_bql_validation: If true, skip BQL validation.
        """
        body: dict[str, Any] = {
            "brokerTicker": broker_ticker,
            "requests": requests,
        }
        if broker_id is not None:
            body["brokerId"] = broker_id
        if skip_bql_validation is not None:
            body["skipBqlValidation"] = skip_bql_validation

        return _call_api("/brokerDesks:batchCreate", http_method="post", request_body=body)

    @mcp.tool()
    def batch_remove_broker_desks(
        broker_ticker: str,
        requests: list[dict[str, Any]],
        broker_id: str | None = None,
    ) -> str:
        """Delete one or more broker desks (max 100 per request).

        Required fields per broker desk: id.

        Args:
            broker_ticker: Broker ticker.
            requests: List of remove requests. Each dict should contain a 'brokerDesk'
                      key with at least the 'id' field identifying the desk to delete.
            broker_id: Aladdin Broker Identifier (numeric).
        """
        body: dict[str, Any] = {
            "brokerTicker": broker_ticker,
            "requests": requests,
        }
        if broker_id is not None:
            body["brokerId"] = broker_id

        return _call_api("/brokerDesks:batchRemove", http_method="post", request_body=body)

    @mcp.tool()
    def batch_update_broker_desks(
        broker_ticker: str,
        requests: list[dict[str, Any]],
        broker_id: str | None = None,
        skip_bql_validation: bool | None = None,
    ) -> str:
        """Batch update broker desks.

        Required fields per broker desk: id, brokerTicker, deskType.
        Users need permissions under permType='brkrDskCon'.

        Args:
            broker_ticker: Broker ticker.
            requests: List of update requests. Each dict should contain a 'brokerDesk'
                      key with fields: id (str, required), deskType (str, required),
                      brokerEntity (str), assistantId (str), salesmanId (str),
                      deskRule (str), deskCode (str).
            broker_id: Aladdin Broker Identifier (numeric). Not supported currently.
            skip_bql_validation: If true, skip BQL validation.
        """
        body: dict[str, Any] = {
            "brokerTicker": broker_ticker,
            "requests": requests,
        }
        if broker_id is not None:
            body["brokerId"] = broker_id
        if skip_bql_validation is not None:
            body["skipBqlValidation"] = skip_bql_validation

        return _call_api("/brokerDesks:batchUpdate", http_method="post", request_body=body)

    @mcp.tool()
    def batch_validate_broker_desks(
        broker_ticker: str,
        requests: list[dict[str, Any]],
        action_type: str,
        broker_id: str | None = None,
        skip_bql_validation: bool | None = None,
    ) -> str:
        """Validate multiple broker desk requests for create and update API calls.

        Args:
            broker_ticker: Broker ticker.
            requests: List of validate requests. Each dict should contain a 'brokerDesk'
                      key with the broker desk fields to validate.
            action_type: Enum determining whether this is a create or update request
                         (e.g. ACTION_TYPE_CREATE, ACTION_TYPE_UPDATE).
            broker_id: Aladdin Broker Identifier (numeric).
            skip_bql_validation: If true, skip BQL validation.
        """
        body: dict[str, Any] = {
            "brokerTicker": broker_ticker,
            "requests": requests,
            "actionType": action_type,
        }
        if broker_id is not None:
            body["brokerId"] = broker_id
        if skip_bql_validation is not None:
            body["skipBqlValidation"] = skip_bql_validation

        return _call_api("/brokerDesks:batchValidate", http_method="post", request_body=body)

    @mcp.tool()
    def filter_broker_desks(
        broker_ticker: str | None = None,
        broker_id: str | None = None,
        load_defunct: bool | None = None,
        broker_tickers: list[str] | None = None,
        broker_type: str | None = None,
        broker_entity: str | None = None,
        filter_type: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter broker desks based on broker ticker or advanced filter criteria.

        Supports basic filtering by a single broker ticker or advanced filtering
        by any combination of broker tickers, broker type, and broker entity.

        Args:
            broker_ticker: Broker ticker for basic filtering.
            broker_id: Aladdin Broker Identifier (numeric). Not supported currently.
            load_defunct: If true, load all desks including defunct ones; otherwise
                         only active desks are returned.
            broker_tickers: List of broker tickers for advanced filtering.
            broker_type: Broker type filter for advanced filtering.
            broker_entity: Broker entity filter for advanced filtering.
            filter_type: Filter type enum (e.g. FILTER_TYPE_BASIC, FILTER_TYPE_ADVANCED).
            page_size: Maximum number of broker desks to return per page.
            page_token: Page token from a previous FilterBrokerDesks call for pagination.
        """
        broker_desk_query: dict[str, Any] = {}
        if broker_ticker is not None:
            broker_desk_query["brokerTicker"] = broker_ticker
        if broker_id is not None:
            broker_desk_query["brokerId"] = broker_id
        if load_defunct is not None:
            broker_desk_query["loadDefunct"] = load_defunct
        if filter_type is not None:
            broker_desk_query["filterType"] = filter_type

        # Build extended query if any advanced filters are provided
        extended_query: dict[str, Any] = {}
        if broker_tickers is not None:
            extended_query["brokerTickers"] = broker_tickers
        if broker_type is not None:
            extended_query["brokerType"] = broker_type
        if broker_entity is not None:
            extended_query["brokerEntity"] = broker_entity
        if extended_query:
            broker_desk_query["brokerDeskExtendedQuery"] = extended_query

        body: dict[str, Any] = {}
        if broker_desk_query:
            body["brokerDeskQuery"] = broker_desk_query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api("/brokerDesks:filter", http_method="post", request_body=body)

    @mcp.tool()
    def undelete_broker_desk(
        broker_desk_id: str,
    ) -> str:
        """Reverse the soft delete of a broker desk, restoring it.

        Args:
            broker_desk_id: The id of the broker desk to undelete.
        """
        body: dict[str, Any] = {
            "id": broker_desk_id,
        }

        return _call_api("/brokerDesks:undelete", http_method="post", request_body=body)
