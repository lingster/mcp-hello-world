"""MCP tools for the Aladdin Broker Confirm Routing API."""

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
    """Helper to call a Broker Confirm Routing API endpoint and return JSON string."""
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
        logger.error(
            f"Broker Confirm Routing API call failed: {http_method.upper()} {endpoint_path}: {e}"
        )
        return json.dumps({"error": str(e)})


def register_broker_confirm_routing_tools(mcp: FastMCP) -> None:
    """Register Aladdin Broker Confirm Routing API tools with the MCP server."""

    @mcp.tool()
    def batch_create_broker_confirm_routings(
        requests: list[dict[str, Any]],
        broker_ticker: str | None = None,
        broker_id: str | None = None,
        skip_bql_validation: bool | None = None,
    ) -> str:
        """Batch create broker confirm routings.

        Each request in the batch contains a brokerConfirmRouting object describing
        the routing to create. A maximum of 100 routings can be created in a batch.

        Args:
            requests: List of create requests. Each dict should have a
                      "brokerConfirmRouting" key containing a dict with fields such as:
                      id (str), brokerId (str), brokerDeskId (str),
                      deliveryPurpose (str), deliveryType (str), deliveryFormat (str),
                      recipientContactId (str), autoSend (bool),
                      confirmDeliveryRule (str), reviewerSignRequired (bool),
                      deliveryStartDate (date str), deliveryStopDate (date str),
                      scheduleName (str), businessPurpose (str).
            broker_ticker: Broker ticker.
            broker_id: Aladdin Broker Identifier (Numeric).
            skip_bql_validation: If true, skip BQL validation for the request.
        """
        body: dict[str, Any] = {"requests": requests}
        if broker_ticker is not None:
            body["brokerTicker"] = broker_ticker
        if broker_id is not None:
            body["brokerId"] = broker_id
        if skip_bql_validation is not None:
            body["skipBqlValidation"] = skip_bql_validation

        return _call_api("/brokerConfirmRoutings:batchCreate", http_method="post", request_body=body)

    @mcp.tool()
    def batch_remove_broker_confirm_routings(
        requests: list[dict[str, Any]],
        broker_ticker: str | None = None,
        broker_id: str | None = None,
    ) -> str:
        """Batch remove broker confirm routings.

        Each request in the batch contains a brokerConfirmRouting object identifying
        the routing to delete. A maximum of 100 routings can be deleted in a batch.
        Broker Entity should not be specified in any delete request.

        Args:
            requests: List of remove requests. Each dict should have a
                      "brokerConfirmRouting" key containing a dict with fields such as:
                      id (str), brokerId (str), brokerDeskId (str),
                      deliveryPurpose (str), deliveryType (str), deliveryFormat (str),
                      recipientContactId (str), autoSend (bool),
                      confirmDeliveryRule (str), reviewerSignRequired (bool),
                      deliveryStartDate (date str), deliveryStopDate (date str),
                      scheduleName (str), businessPurpose (str).
            broker_ticker: Broker ticker.
            broker_id: Aladdin Broker Identifier (Numeric).
        """
        body: dict[str, Any] = {"requests": requests}
        if broker_ticker is not None:
            body["brokerTicker"] = broker_ticker
        if broker_id is not None:
            body["brokerId"] = broker_id

        return _call_api("/brokerConfirmRoutings:batchRemove", http_method="post", request_body=body)

    @mcp.tool()
    def batch_update_broker_confirm_routings(
        requests: list[dict[str, Any]],
        broker_ticker: str | None = None,
        broker_id: str | None = None,
        skip_bql_validation: bool | None = None,
    ) -> str:
        """Batch update broker confirm routings.

        Each request in the batch contains a brokerConfirmRouting object with updated
        fields. A maximum of 100 routings can be updated in a batch.
        Broker Entity should not be specified in any update request.

        Args:
            requests: List of update requests. Each dict should have a
                      "brokerConfirmRouting" key containing a dict with fields such as:
                      id (str), brokerId (str), brokerDeskId (str),
                      deliveryPurpose (str), deliveryType (str), deliveryFormat (str),
                      recipientContactId (str), autoSend (bool),
                      confirmDeliveryRule (str), reviewerSignRequired (bool),
                      deliveryStartDate (date str), deliveryStopDate (date str),
                      scheduleName (str), businessPurpose (str).
            broker_ticker: Broker ticker.
            broker_id: Aladdin Broker Identifier (Numeric).
            skip_bql_validation: If true, skip BQL validation for the request.
        """
        body: dict[str, Any] = {"requests": requests}
        if broker_ticker is not None:
            body["brokerTicker"] = broker_ticker
        if broker_id is not None:
            body["brokerId"] = broker_id
        if skip_bql_validation is not None:
            body["skipBqlValidation"] = skip_bql_validation

        return _call_api("/brokerConfirmRoutings:batchUpdate", http_method="post", request_body=body)

    @mcp.tool()
    def batch_validate_broker_confirm_routings(
        requests: list[dict[str, Any]],
        broker_ticker: str | None = None,
        broker_id: str | None = None,
        action_type: str | None = None,
        skip_bql_validation: bool | None = None,
    ) -> str:
        """Batch validate broker confirm routings before creating or updating.

        Each request in the batch contains a brokerConfirmRouting object to validate.
        A maximum of 100 routings can be validated in a batch.

        Args:
            requests: List of validate requests. Each dict should have a
                      "brokerConfirmRouting" key containing a dict with fields such as:
                      id (str), brokerId (str), brokerDeskId (str),
                      deliveryPurpose (str), deliveryType (str), deliveryFormat (str),
                      recipientContactId (str), autoSend (bool),
                      confirmDeliveryRule (str), reviewerSignRequired (bool),
                      deliveryStartDate (date str), deliveryStopDate (date str),
                      scheduleName (str), businessPurpose (str).
            broker_ticker: Broker ticker.
            broker_id: Aladdin Broker Identifier (Numeric).
            action_type: Determines whether validating a create or update request.
                         One of: ACTION_TYPE_UNSPECIFIED, ACTION_TYPE_CREATE,
                         ACTION_TYPE_UPDATE.
            skip_bql_validation: If true, skip BQL validation for the request.
        """
        body: dict[str, Any] = {"requests": requests}
        if broker_ticker is not None:
            body["brokerTicker"] = broker_ticker
        if broker_id is not None:
            body["brokerId"] = broker_id
        if action_type is not None:
            body["actionType"] = action_type
        if skip_bql_validation is not None:
            body["skipBqlValidation"] = skip_bql_validation

        return _call_api(
            "/brokerConfirmRoutings:batchValidate", http_method="post", request_body=body
        )

    @mcp.tool()
    def filter_broker_confirm_routings(
        broker_ticker: str | None = None,
        broker_id: str | None = None,
        load_defunct: bool | None = None,
        filter_type: str | None = None,
        broker_confirm_routing_extended_query: dict[str, Any] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter broker confirm routings by query criteria.

        Args:
            broker_ticker: Broker ticker to filter by.
            broker_id: Aladdin Broker Identifier (Numeric) to filter by.
            load_defunct: If true, load all routings including defunct ones;
                          otherwise only non-defunct data is returned.
            filter_type: Type of filter being performed. One of:
                         FILTER_TYPE_UNSPECIFIED, FILTER_TYPE_BASIC,
                         FILTER_TYPE_ADVANCE, FILTER_TYPE_ID.
            broker_confirm_routing_extended_query: Extended query with additional
                         filters. Dict may contain: brokerTickers (list[str]),
                         brokerType (str), brokerEntity (str).
            page_size: Maximum number of routings to return. If 0 or unspecified,
                       the complete list is returned.
            page_token: Page token from a previous call to retrieve the next page.
        """
        query: dict[str, Any] = {}
        if broker_ticker is not None:
            query["brokerTicker"] = broker_ticker
        if broker_id is not None:
            query["brokerId"] = broker_id
        if load_defunct is not None:
            query["loadDefunct"] = load_defunct
        if filter_type is not None:
            query["filterType"] = filter_type
        if broker_confirm_routing_extended_query is not None:
            query["brokerConfirmRoutingExtendedQuery"] = broker_confirm_routing_extended_query

        body: dict[str, Any] = {}
        if query:
            body["brokerConfirmRoutingQuery"] = query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api("/brokerConfirmRoutings:filter", http_method="post", request_body=body)
