"""MCP tools for the Aladdin Order API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_ORDER_BASE_PATH = "/api/trading/order-management/order/v1/"

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


def _call_order_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call an Order API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_ORDER_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Order API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_order_tools(mcp: FastMCP) -> None:
    """Register Aladdin Order API tools with the MCP server."""

    @mcp.tool()
    def get_longrunning_operation(operation_id: str) -> str:
        """Poll for the results of a long running order operation.

        Args:
            operation_id: The unique identifier of the long running operation.
        """
        return _call_order_api(
            f"/longrunningoperations/{operation_id}",
            http_method="get",
        )

    @mcp.tool()
    def cancel_order(
        order_id: str | None = None,
        external_id1: str | None = None,
        account_code: str | None = None,
        order_comments: list[dict[str, Any]] | None = None,
    ) -> str:
        """Cancel a single Aladdin order by order ID or external reference.

        Provide either order_id or the external reference fields
        (external_id1 + account_code) to identify the order.

        Args:
            order_id: The Aladdin order ID to cancel.
            external_id1: External ID for the order (used with account_code).
            account_code: Aladdin account code (used with external_id1).
            order_comments: Optional list of comments to attach. Each dict
                            can have keys like 'comment' (str).
        """
        body: dict[str, Any] = {}
        if order_id is not None:
            body["orderId"] = order_id
        if external_id1 is not None or account_code is not None:
            ext_ref: dict[str, Any] = {}
            if external_id1 is not None:
                ext_ref["externalId1"] = external_id1
            if account_code is not None:
                ext_ref["accountCode"] = account_code
            body["externalReference"] = ext_ref
        if order_comments is not None:
            body["orderComments"] = order_comments

        return _call_order_api("/order:cancel", http_method="post", request_body=body)

    @mcp.tool()
    def post_order(
        order: dict[str, Any],
        what_if: bool | None = None,
        run_compliance: bool | None = None,
        account_code: str | None = None,
        external_entity_type: str | None = None,
        compliance_timeout: str | None = None,
    ) -> str:
        """Post a new or update a single Aladdin order.

        Args:
            order: Order details dict. Common keys include:
                - assetId (str): Asset identifier.
                - transactionType (str): e.g. "BUY", "SELL".
                - orderDate (str): Date of the order (YYYY-MM-DD).
                - settleDate (str): Settlement date (YYYY-MM-DD).
                - tradeDate (str): Trade date (YYYY-MM-DD).
                - basketId (str): Basket grouping identifier.
                - tradingLimitType (str): e.g. "Price", "Yield".
                - tradingLimitValue (float): Limit value.
                - orderType (str): Type of order.
                - pmInstruction (str): PM instruction e.g. "Approved".
                - pmInitials (str): PM initials.
                - face (float): Face value.
                - principal (float): Principal amount.
                - orderComments (list[dict]): Comments on the order.
                - orderCustomFields (list[dict]): UDFs (max 20).
            what_if: If true, performs a dry run without persisting.
            run_compliance: Whether to run compliance (default true).
            account_code: Aladdin account code for the organization.
            external_entity_type: External entity type (e.g. "CUST", "FUTR").
            compliance_timeout: Timeout for compliance run (e.g. "10s").
        """
        body: dict[str, Any] = {"order": order}
        config: dict[str, Any] = {}
        if what_if is not None:
            config["whatIf"] = what_if
        if run_compliance is not None:
            config["runCompliance"] = run_compliance
        if account_code is not None:
            config["accountCode"] = account_code
        if external_entity_type is not None:
            config["externalEntityType"] = external_entity_type
        if compliance_timeout is not None:
            config["complianceTimeout"] = compliance_timeout
        if config:
            body["postOrderConfig"] = config

        return _call_order_api("/order:post", http_method="post", request_body=body)

    @mcp.tool()
    def filter_order_ids(
        portfolio_group_criterion: dict[str, Any] | None = None,
        basket_id_criterion: dict[str, Any] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter Aladdin order IDs by portfolio group or basket ID criteria.

        Args:
            portfolio_group_criterion: Portfolio group filter criteria dict.
            basket_id_criterion: Basket ID filter criteria dict.
            page_size: Maximum number of results per page.
            page_token: Page token from a previous call for pagination.
        """
        body: dict[str, Any] = {}
        query: dict[str, Any] = {}
        if portfolio_group_criterion is not None:
            query["portfolioGroupCriterion"] = portfolio_group_criterion
        if basket_id_criterion is not None:
            query["basketIdCriterion"] = basket_id_criterion
        if query:
            body["query"] = query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_order_api("/orderIds:filter", http_method="post", request_body=body)

    @mcp.tool()
    def batch_cancel_orders(
        requests: list[dict[str, Any]],
    ) -> str:
        """Cancel multiple Aladdin orders in a single batch request.

        Args:
            requests: List of cancel order request dicts (1-500). Each dict
                      can have keys: orderId (str), externalReference (dict
                      with externalId1/accountCode), orderComments (list).
        """
        body: dict[str, Any] = {"requests": requests}
        return _call_order_api("/orders:batchCancel", http_method="post", request_body=body)

    @mcp.tool()
    def batch_post_orders(
        orders: list[dict[str, Any]],
        what_if: bool | None = None,
        run_compliance: bool | None = None,
        account_code: str | None = None,
        external_entity_type: str | None = None,
        compliance_timeout: str | None = None,
    ) -> str:
        """Post new and/or update multiple Aladdin orders in a batch.

        Args:
            orders: List of order dicts. See post_order for order dict keys.
            what_if: If true, performs a dry run without persisting.
            run_compliance: Whether to run compliance (default true).
            account_code: Aladdin account code for the organization.
            external_entity_type: External entity type (e.g. "CUST", "FUTR").
            compliance_timeout: Timeout for compliance run (e.g. "10s").
        """
        body: dict[str, Any] = {"orders": orders}
        config: dict[str, Any] = {}
        if what_if is not None:
            config["whatIf"] = what_if
        if run_compliance is not None:
            config["runCompliance"] = run_compliance
        if account_code is not None:
            config["accountCode"] = account_code
        if external_entity_type is not None:
            config["externalEntityType"] = external_entity_type
        if compliance_timeout is not None:
            config["complianceTimeout"] = compliance_timeout
        if config:
            body["postOrderConfig"] = config

        return _call_order_api("/orders:batchPost", http_method="post", request_body=body)

    @mcp.tool()
    def filter_orders(
        query: dict[str, Any] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter Aladdin orders by various criteria.

        Supports filtering by order IDs, external IDs, portfolio group,
        basket ID, modified time, dealing capacity, and more.

        Args:
            query: Order query dict with one criterion key. Supported keys:
                - retrieveOrderReservations (bool)
                - orderIdCriterion (dict): Filter by order IDs.
                - externalIdCriterion (dict): Filter by external ID.
                - externalIdListCriterion (dict): Filter by external ID list.
                - portfolioGroupCriterion (dict): Filter by portfolio group.
                - basketIdCriterion (dict): Filter by basket ID.
                - portfolioModifiedTimeCriterion (dict): Filter by modified time.
                - dealingCapacityCriterion (dict): Filter by dealing capacity.
                - traderOrderByPmOrderIdCriterion (dict): Filter trader orders by PM order ID.
            page_size: Maximum number of results per page.
            page_token: Page token from a previous call for pagination.
        """
        body: dict[str, Any] = {}
        if query is not None:
            body["query"] = query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_order_api("/orders:filter", http_method="post", request_body=body)
