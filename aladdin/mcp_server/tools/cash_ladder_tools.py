"""MCP tools for the Aladdin Cash Ladder API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_BASE_PATH = "/api/portfolio-management/cash/cash-ladder/v2/"

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
    """Helper to call a Cash Ladder API endpoint and return JSON string."""
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
        logger.error(f"Cash Ladder API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_cash_ladder_tools(mcp: FastMCP) -> None:
    """Register Aladdin Cash Ladder API tools with the MCP server."""

    @mcp.tool()
    def get_cash_ladder(
        portfolio_group_ticker: str,
        cash_date: str,
        include_stored_cash: bool | None = None,
        include_pni: bool | None = None,
        include_intraday_trades_cash_impact: bool | None = None,
        include_intraday_auth_and_active_orders_cash_impact: bool | None = None,
        include_intraday_open_orders_cash_impact: bool | None = None,
        include_intraday_confirmed_new_cash: bool | None = None,
        include_intraday_auth_new_cash: bool | None = None,
        include_intraday_open_new_cash: bool | None = None,
        include_stif_ich: bool | None = None,
        cash_balance_view_currency_setting: str | None = None,
        include_collateral_pledged: bool | None = None,
        include_collateral_held: bool | None = None,
        default_calendar: str | None = None,
        cash_balance_trade_date_scope: str | None = None,
        cash_balance_open_date_scope: str | None = None,
        cash_balance_new_cash_trade_date_scope: str | None = None,
        cash_balance_order_type_scope: str | None = None,
    ) -> str:
        """Gets Cash Ladder for a given portfolio group and cash date.

        Returns a settlement date based ladder of cash balances for all
        exposure currencies for the specified portfolio group and cash date.

        Args:
            portfolio_group_ticker: Name of the portfolio or portfolio group for
                which cash balances are requested.
            cash_date: Cash date for which cash balances are requested (YYYY-MM-DD).
            include_stored_cash: Include stored (SOD) cash that is yet to be fully
                reconciled between custodian and Aladdin.
            include_pni: Include principal and interest in SOD balances.
            include_intraday_trades_cash_impact: Include cash impact from trades
                posted intraday.
            include_intraday_auth_and_active_orders_cash_impact: Include cash impact
                from intraday orders in active or authorized status.
            include_intraday_open_orders_cash_impact: Include cash impact from open
                orders posted intraday.
            include_intraday_confirmed_new_cash: Include new cash entries in
                confirmed status posted intraday.
            include_intraday_auth_new_cash: Include new cash entries in authorized
                status posted intraday.
            include_intraday_open_new_cash: Include new cash entries in open status
                posted intraday.
            include_stif_ich: Include trade date impact of STIF or ICH cash positions.
            cash_balance_view_currency_setting: Currency in which cash balances are
                returned (e.g. CASH_BALANCE_VIEW_CURRENCY_UNSPECIFIED,
                CASH_BALANCE_VIEW_CURRENCY_LOCAL, CASH_BALANCE_VIEW_CURRENCY_BASE).
            include_collateral_pledged: Include collateral pledged impact of SOD
                trades and intraday activities.
            include_collateral_held: Include collateral held impact of SOD trades
                and intraday activities.
            default_calendar: Default calendar for calculating ladder and activity
                settle dates. Use decodes API with MKT_CALENDARS to look up valid values.
            cash_balance_trade_date_scope: Future trade date up to which trade
                activity is retrieved.
            cash_balance_open_date_scope: Future date up to which order activity
                is retrieved.
            cash_balance_new_cash_trade_date_scope: Future date up to which new
                cash activity is retrieved.
            cash_balance_order_type_scope: Order type for orders and new cash.
        """
        params: dict[str, Any] = {
            "portfolioGroupTicker": portfolio_group_ticker,
            "cashDate": cash_date,
        }
        if include_stored_cash is not None:
            params["includeStoredCash"] = include_stored_cash
        if include_pni is not None:
            params["includePni"] = include_pni
        if include_intraday_trades_cash_impact is not None:
            params["includeIntradayTradesCashImpact"] = include_intraday_trades_cash_impact
        if include_intraday_auth_and_active_orders_cash_impact is not None:
            params["includeIntradayAuthAndActiveOrdersCashImpact"] = (
                include_intraday_auth_and_active_orders_cash_impact
            )
        if include_intraday_open_orders_cash_impact is not None:
            params["includeIntradayOpenOrdersCashImpact"] = include_intraday_open_orders_cash_impact
        if include_intraday_confirmed_new_cash is not None:
            params["includeIntradayConfirmedNewCash"] = include_intraday_confirmed_new_cash
        if include_intraday_auth_new_cash is not None:
            params["includeIntradayAuthNewCash"] = include_intraday_auth_new_cash
        if include_intraday_open_new_cash is not None:
            params["includeIntradayOpenNewCash"] = include_intraday_open_new_cash
        if include_stif_ich is not None:
            params["includeStifIch"] = include_stif_ich
        if cash_balance_view_currency_setting is not None:
            params["cashBalanceViewCurrencySetting"] = cash_balance_view_currency_setting
        if include_collateral_pledged is not None:
            params["includeCollateralPledged"] = include_collateral_pledged
        if include_collateral_held is not None:
            params["includeCollateralHeld"] = include_collateral_held
        if default_calendar is not None:
            params["defaultCalendar"] = default_calendar
        if cash_balance_trade_date_scope is not None:
            params["cashBalanceTradeDateScope"] = cash_balance_trade_date_scope
        if cash_balance_open_date_scope is not None:
            params["cashBalanceOpenDateScope"] = cash_balance_open_date_scope
        if cash_balance_new_cash_trade_date_scope is not None:
            params["cashBalanceNewCashTradeDateScope"] = cash_balance_new_cash_trade_date_scope
        if cash_balance_order_type_scope is not None:
            params["cashBalanceOrderTypeScope"] = cash_balance_order_type_scope

        return _call_api("/ladders", http_method="get", params=params)

    @mcp.tool()
    def filter_cash_ladder(
        portfolio_group_tickers: list[str],
        cash_date: str,
        include_stored_cash: bool | None = None,
        include_pni: bool | None = None,
        include_intraday_trades_cash_impact: bool | None = None,
        include_intraday_auth_and_active_orders_cash_impact: bool | None = None,
        include_intraday_open_orders_cash_impact: bool | None = None,
        include_intraday_confirmed_new_cash: bool | None = None,
        include_intraday_auth_new_cash: bool | None = None,
        include_intraday_open_new_cash: bool | None = None,
        include_stif_ich: bool | None = None,
        cash_balance_view_currency_setting: str | None = None,
        include_collateral_pledged: bool | None = None,
        include_collateral_held: bool | None = None,
        default_calendar: str | None = None,
        cash_balance_trade_date_scope: str | None = None,
        cash_balance_open_date_scope: str | None = None,
        cash_balance_new_cash_trade_date_scope: str | None = None,
        cash_balance_order_type_scope: str | None = None,
        enable_prefunding: bool | None = None,
        include_collateral_projected_held: bool | None = None,
        include_collateral_projected_pledged: bool | None = None,
        include_unfunded_commitment: bool | None = None,
        specific_settle_date_projections: list[str] | None = None,
        include_intraday_misc_cash: bool | None = None,
    ) -> str:
        """Filter Cash Ladder for multiple portfolio groups and a cash date.

        Supports filtering across up to 100 portfolio group tickers and provides
        additional options beyond the GET endpoint, such as prefunding, projected
        collateral, unfunded commitments, and specific settle date projections.

        Args:
            portfolio_group_tickers: List of portfolio or portfolio group names
                (maximum 100) for which cash balances are requested.
            cash_date: Cash date for which cash balances are requested (YYYY-MM-DD).
            include_stored_cash: Include stored (SOD) cash that is yet to be fully
                reconciled between custodian and Aladdin.
            include_pni: Include principal and interest in SOD balances.
            include_intraday_trades_cash_impact: Include cash impact from trades
                posted intraday.
            include_intraday_auth_and_active_orders_cash_impact: Include cash impact
                from intraday orders in active or authorized status.
            include_intraday_open_orders_cash_impact: Include cash impact from open
                orders posted intraday.
            include_intraday_confirmed_new_cash: Include new cash entries in
                confirmed status posted intraday.
            include_intraday_auth_new_cash: Include new cash entries in authorized
                status posted intraday.
            include_intraday_open_new_cash: Include new cash entries in open status
                posted intraday.
            include_stif_ich: Include trade date impact of STIF or ICH cash positions.
            cash_balance_view_currency_setting: Currency in which cash balances are
                returned (e.g. CASH_BALANCE_VIEW_CURRENCY_UNSPECIFIED,
                CASH_BALANCE_VIEW_CURRENCY_LOCAL, CASH_BALANCE_VIEW_CURRENCY_BASE).
            include_collateral_pledged: Include collateral pledged impact of SOD
                trades and intraday activities.
            include_collateral_held: Include collateral held impact of SOD trades
                and intraday activities.
            default_calendar: Default calendar for calculating ladder and activity
                settle dates. Use decodes API with MKT_CALENDARS to look up valid values.
            cash_balance_trade_date_scope: Future trade date up to which trade
                activity is retrieved.
            cash_balance_open_date_scope: Future date up to which order activity
                is retrieved.
            cash_balance_new_cash_trade_date_scope: Future date up to which new
                cash activity is retrieved.
            cash_balance_order_type_scope: Order type for orders and new cash.
            enable_prefunding: Adjust settle dates on the cash ladder based on
                prefunding rules.
            include_collateral_projected_held: Include impact of projected held
                collateral in cash balances.
            include_collateral_projected_pledged: Include impact of projected pledged
                collateral in cash balances.
            include_unfunded_commitment: Include impact of unfunded commitments in
                private equity markets.
            specific_settle_date_projections: List of settle dates in S format
                (e.g. S, S+1, S+45, S+90) to retrieve specific cash projections.
                If empty, returns S to S+7, S+30, S+60, S+90 by default.
            include_intraday_misc_cash: Include cash impact of intraday misc cash
                transactions.
        """
        query: dict[str, Any] = {
            "portfolioGroupTickers": portfolio_group_tickers,
            "cashDate": cash_date,
        }
        if include_stored_cash is not None:
            query["includeStoredCash"] = include_stored_cash
        if include_pni is not None:
            query["includePni"] = include_pni
        if include_intraday_trades_cash_impact is not None:
            query["includeIntradayTradesCashImpact"] = include_intraday_trades_cash_impact
        if include_intraday_auth_and_active_orders_cash_impact is not None:
            query["includeIntradayAuthAndActiveOrdersCashImpact"] = (
                include_intraday_auth_and_active_orders_cash_impact
            )
        if include_intraday_open_orders_cash_impact is not None:
            query["includeIntradayOpenOrdersCashImpact"] = include_intraday_open_orders_cash_impact
        if include_intraday_confirmed_new_cash is not None:
            query["includeIntradayConfirmedNewCash"] = include_intraday_confirmed_new_cash
        if include_intraday_auth_new_cash is not None:
            query["includeIntradayAuthNewCash"] = include_intraday_auth_new_cash
        if include_intraday_open_new_cash is not None:
            query["includeIntradayOpenNewCash"] = include_intraday_open_new_cash
        if include_stif_ich is not None:
            query["includeStifIch"] = include_stif_ich
        if cash_balance_view_currency_setting is not None:
            query["cashBalanceViewCurrencySetting"] = cash_balance_view_currency_setting
        if include_collateral_pledged is not None:
            query["includeCollateralPledged"] = include_collateral_pledged
        if include_collateral_held is not None:
            query["includeCollateralHeld"] = include_collateral_held
        if default_calendar is not None:
            query["defaultCalendar"] = default_calendar
        if cash_balance_trade_date_scope is not None:
            query["cashBalanceTradeDateScope"] = cash_balance_trade_date_scope
        if cash_balance_open_date_scope is not None:
            query["cashBalanceOpenDateScope"] = cash_balance_open_date_scope
        if cash_balance_new_cash_trade_date_scope is not None:
            query["cashBalanceNewCashTradeDateScope"] = cash_balance_new_cash_trade_date_scope
        if cash_balance_order_type_scope is not None:
            query["cashBalanceOrderTypeScope"] = cash_balance_order_type_scope
        if enable_prefunding is not None:
            query["enablePrefunding"] = enable_prefunding
        if include_collateral_projected_held is not None:
            query["includeCollateralProjectedHeld"] = include_collateral_projected_held
        if include_collateral_projected_pledged is not None:
            query["includeCollateralProjectedPledged"] = include_collateral_projected_pledged
        if include_unfunded_commitment is not None:
            query["includeUnfundedCommitment"] = include_unfunded_commitment
        if specific_settle_date_projections is not None:
            query["specificSettleDateProjections"] = specific_settle_date_projections
        if include_intraday_misc_cash is not None:
            query["includeIntradayMiscCash"] = include_intraday_misc_cash

        body: dict[str, Any] = {"cashLadderQuery": query}
        return _call_api("/ladders:filter", http_method="post", request_body=body)
