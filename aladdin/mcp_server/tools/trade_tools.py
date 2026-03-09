"""MCP tools for the Aladdin Trade API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_TRADE_BASE_PATH = "/api/trading/trade-processing/trade/v2/"

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


def _call_trade_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Trade API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_TRADE_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Trade API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_trade_tools(mcp: FastMCP) -> None:
    """Register Aladdin Trade API tools with the MCP server."""

    @mcp.tool()
    def get_trade_longrunning_operation(operation_id: str) -> str:
        """Poll for the result of a long-running trade operation.

        Args:
            operation_id: The unique identifier of the long-running operation.
        """
        return _call_trade_api(
            f"/longrunningoperations/{operation_id}",
            http_method="get",
        )

    @mcp.tool()
    def post_trade(
        block_trade: dict[str, Any],
        mode: str | None = None,
        override_relationships: bool | None = None,
        override_charges: bool | None = None,
        update_entire_block: bool | None = None,
        account_code: str | None = None,
        entity_type: str | None = None,
        entity: int | None = None,
    ) -> str:
        """Post or update a single trade. Creates the trade if it does not exist, updates it if it does.

        Args:
            block_trade: The block trade object to post. Should contain 'trades' (list of
                         trade allocations) and block-level fields such as assetReference,
                         transactionType, price, tradeDate, settlementDate, etc.
            mode: Posting mode. One of POSTING_MODE_UNSPECIFIED, POSTING_MODE_NEW,
                  POSTING_MODE_UPDATE.
            override_relationships: Whether to override existing relationships.
            override_charges: Whether to override existing charges.
            update_entire_block: Whether to update the entire block of trades.
            account_code: Account code of the external account.
            entity_type: Entity type of the external account.
            entity: The entity identifier.
        """
        body: dict[str, Any] = {"blockTrade": block_trade}
        config: dict[str, Any] = {}
        if mode is not None:
            config["mode"] = mode
        if override_relationships is not None:
            config["overrideRelationships"] = override_relationships
        if override_charges is not None:
            config["overrideCharges"] = override_charges
        if update_entire_block is not None:
            config["updateEntireBlock"] = update_entire_block
        if account_code is not None:
            config["accountCode"] = account_code
        if entity_type is not None:
            config["entityType"] = entity_type
        if entity is not None:
            config["entity"] = entity
        if config:
            body["config"] = config

        return _call_trade_api("/trades:post", http_method="post", request_body=body)

    @mcp.tool()
    def batch_post_trades(
        block_trades: list[dict[str, Any]],
        mode: str | None = None,
        override_relationships: bool | None = None,
        override_charges: bool | None = None,
        update_entire_block: bool | None = None,
        account_code: str | None = None,
        entity_type: str | None = None,
        entity: int | None = None,
    ) -> str:
        """Post or update multiple trades in a batch. Returns a long-running operation.

        Creates trades that do not exist and updates those that do.

        Args:
            block_trades: List of block trade objects to post. Each should contain
                          'trades' (list of trade allocations) and block-level fields
                          such as assetReference, transactionType, price, tradeDate, etc.
            mode: Posting mode. One of POSTING_MODE_UNSPECIFIED, POSTING_MODE_NEW,
                  POSTING_MODE_UPDATE.
            override_relationships: Whether to override existing relationships.
            override_charges: Whether to override existing charges.
            update_entire_block: Whether to update the entire block of trades.
            account_code: Account code of the external account.
            entity_type: Entity type of the external account.
            entity: The entity identifier.
        """
        body: dict[str, Any] = {"blockTrades": block_trades}
        config: dict[str, Any] = {}
        if mode is not None:
            config["mode"] = mode
        if override_relationships is not None:
            config["overrideRelationships"] = override_relationships
        if override_charges is not None:
            config["overrideCharges"] = override_charges
        if update_entire_block is not None:
            config["updateEntireBlock"] = update_entire_block
        if account_code is not None:
            config["accountCode"] = account_code
        if entity_type is not None:
            config["entityType"] = entity_type
        if entity is not None:
            config["entity"] = entity
        if config:
            body["config"] = config

        return _call_trade_api("/trades:batchPost", http_method="post", request_body=body)

    @mcp.tool()
    def cancel_trade(
        portfolio_id: str | None = None,
        portfolio_ticker: str | None = None,
        invnum: int | None = None,
        suppress_external_notification: bool | None = None,
        cancel_entire_block: bool | None = None,
    ) -> str:
        """Cancel a single trade. Returns the trade cancel response.

        Provide either portfolio_id or portfolio_ticker to identify the portfolio,
        along with the invnum to identify the specific trade.

        Args:
            portfolio_id: The portfolio ID associated with the trade.
            portfolio_ticker: The portfolio ticker associated with the trade.
            invnum: The invnum of the trade to cancel.
            suppress_external_notification: Whether to suppress external notifications.
            cancel_entire_block: Whether to cancel the entire block of trades.
        """
        body: dict[str, Any] = {}
        trade_key: dict[str, Any] = {}
        portfolio_ref: dict[str, Any] = {}
        if portfolio_id is not None:
            portfolio_ref["portfolioId"] = portfolio_id
        if portfolio_ticker is not None:
            portfolio_ref["portfolioTicker"] = portfolio_ticker
        if portfolio_ref:
            trade_key["portfolioReference"] = portfolio_ref
        if invnum is not None:
            trade_key["invnum"] = invnum
        if trade_key:
            body["tradeKey"] = trade_key

        config: dict[str, Any] = {}
        if suppress_external_notification is not None:
            config["suppressExternalNotification"] = suppress_external_notification
        if cancel_entire_block is not None:
            config["cancelEntireBlock"] = cancel_entire_block
        if config:
            body["config"] = config

        return _call_trade_api("/trades:cancel", http_method="post", request_body=body)

    @mcp.tool()
    def batch_cancel_trades(
        trade_keys: list[dict[str, Any]],
        suppress_external_notification: bool | None = None,
        cancel_entire_block: bool | None = None,
    ) -> str:
        """Cancel multiple trades in a batch. Returns a long-running operation.

        Args:
            trade_keys: List of trade key objects to cancel. Each dict should contain
                        portfolioReference (with portfolioId or portfolioTicker) and/or
                        invnum to identify the trade.
            suppress_external_notification: Whether to suppress external notifications.
            cancel_entire_block: Whether to cancel the entire block of trades.
        """
        body: dict[str, Any] = {"tradeKeys": trade_keys}
        config: dict[str, Any] = {}
        if suppress_external_notification is not None:
            config["suppressExternalNotification"] = suppress_external_notification
        if cancel_entire_block is not None:
            config["cancelEntireBlock"] = cancel_entire_block
        if config:
            body["config"] = config

        return _call_trade_api("/trades:batchCancel", http_method="post", request_body=body)

    @mcp.tool()
    def filter_trades(
        criteria: dict[str, Any] | None = None,
        options: list[str] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
        expands: list[str] | None = None,
    ) -> str:
        """Filter trades by criteria such as portfolio, date/time, trade attributes, asset, or broker.

        Args:
            criteria: Filter criteria object with optional keys:
                      - portfolio: portfolio criterion (e.g. portfolio references)
                      - dateTime: date/time criterion (e.g. trade date range)
                      - trade: trade criterion (e.g. transaction type, status)
                      - asset: asset criterion
                      - broker: broker criterion
            options: List of query options. Valid values:
                     FILTER_QUERY_OPTION_UNSPECIFIED,
                     FILTER_QUERY_OPTION_LOAD_TRADE_RELATIONSHIP,
                     FILTER_QUERY_OPTION_LOAD_EXTERNAL_TRADE_REFERENCE,
                     FILTER_QUERY_OPTION_LOAD_TRADE_COLLATERAL,
                     FILTER_QUERY_OPTION_LOAD_TRADE_FX_LEGS.
            page_size: Maximum number of trades to return.
            page_token: Page token from a previous filterTrades call for pagination.
            expands: List of related reference data to include (e.g. asset-related fields).
        """
        body: dict[str, Any] = {}
        query: dict[str, Any] = {}
        if criteria is not None:
            query["criteria"] = criteria
        if options is not None:
            query["options"] = options
        if query:
            body["query"] = query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token
        if expands is not None:
            body["expands"] = expands

        return _call_trade_api("/trades:filter", http_method="post", request_body=body)

    @mcp.tool()
    def retrieve_trades(
        trade_keys: list[dict[str, Any]] | None = None,
        extern_trade_keys: list[dict[str, Any]] | None = None,
        order_keys: list[str] | None = None,
        options: list[str] | None = None,
        expands: list[str] | None = None,
    ) -> str:
        """Retrieve trades by specific trade keys, external trade keys, or order keys.

        Args:
            trade_keys: List of trade key criteria. Each dict should contain
                        portfolioReference (with portfolioId or portfolioTicker)
                        and/or invnum.
            extern_trade_keys: List of external trade reference criteria.
            order_keys: List of order IDs to retrieve trades for.
            options: List of query options. Valid values:
                     RETRIEVE_QUERY_OPTION_UNSPECIFIED,
                     RETRIEVE_QUERY_OPTION_LOAD_COMPLETE_BLOCK.
            expands: List of related reference data to include (e.g. asset-related fields).
        """
        body: dict[str, Any] = {}
        query: dict[str, Any] = {}
        if trade_keys is not None:
            query["criteria"] = {"tradeKeys": trade_keys}
        if extern_trade_keys is not None:
            query.setdefault("criteria", {})["externTradeKeys"] = extern_trade_keys
        if order_keys is not None:
            query.setdefault("criteria", {})["orderKeys"] = order_keys
        if options is not None:
            query["options"] = options
        if query:
            body["query"] = query
        if expands is not None:
            body["expands"] = expands

        return _call_trade_api("/trades:retrieve", http_method="post", request_body=body)
