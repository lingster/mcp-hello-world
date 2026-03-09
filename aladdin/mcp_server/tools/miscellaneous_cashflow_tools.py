"""MCP tools for the Aladdin Miscellaneous Cashflow API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_MISC_CASHFLOW_BASE_PATH = "/api/investment-operations/cash-flows/miscellaneous-cashflow/v1/"

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
    """Helper to call a Miscellaneous Cashflow API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_MISC_CASHFLOW_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Miscellaneous Cashflow API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def _build_cashflow_body(
    portfolio_id: str | None = None,
    investment_number: int | None = None,
    series_number: int | None = None,
    currency_code: str | None = None,
    broker_id: str | None = None,
    principal: float | None = None,
    interest: float | None = None,
    commission: float | None = None,
    other_fee: float | None = None,
    original_face: float | None = None,
    asset_id: str | None = None,
    trade_date: str | None = None,
    settle_date: str | None = None,
    status: str | None = None,
    sub_transaction_type: str | None = None,
    entered_by: str | None = None,
    trader: str | None = None,
    confirmed_by: str | None = None,
    reviewed_by: str | None = None,
    strategy_id: int | None = None,
    exchange_rate: float | None = None,
    actual_settle_date: str | None = None,
    settled_amount: float | None = None,
    settlement_instruction_id: str | None = None,
    client_payment_reference: str | None = None,
    cashflow_comment_text: str | None = None,
    cashflow_external_id: dict[str, Any] | None = None,
    factor: float | None = None,
    price: float | None = None,
    trade_par: float | None = None,
    short_indicator: str | None = None,
    structured_by: str | None = None,
    settlement_confirmed: str | None = None,
    duplicate_number: int | None = None,
    source: str | None = None,
    accounting_method: str | None = None,
    version: int | None = None,
    portfolio_ticker: str | None = None,
) -> dict[str, Any]:
    """Build a v1MiscellaneousCashflow dict, filtering out None values."""
    field_map: list[tuple[str, str, Any]] = [
        ("portfolioId", "portfolio_id", portfolio_id),
        ("investmentNumber", "investment_number", investment_number),
        ("seriesNumber", "series_number", series_number),
        ("currencyCode", "currency_code", currency_code),
        ("brokerId", "broker_id", broker_id),
        ("principal", "principal", principal),
        ("interest", "interest", interest),
        ("commission", "commission", commission),
        ("otherFee", "other_fee", other_fee),
        ("originalFace", "original_face", original_face),
        ("assetId", "asset_id", asset_id),
        ("tradeDate", "trade_date", trade_date),
        ("settleDate", "settle_date", settle_date),
        ("status", "status", status),
        ("subTransactionType", "sub_transaction_type", sub_transaction_type),
        ("enteredBy", "entered_by", entered_by),
        ("trader", "trader", trader),
        ("confirmedBy", "confirmed_by", confirmed_by),
        ("reviewedBy", "reviewed_by", reviewed_by),
        ("strategyId", "strategy_id", strategy_id),
        ("exchangeRate", "exchange_rate", exchange_rate),
        ("actualSettleDate", "actual_settle_date", actual_settle_date),
        ("settledAmount", "settled_amount", settled_amount),
        ("settlementInstructionId", "settlement_instruction_id", settlement_instruction_id),
        ("clientPaymentReference", "client_payment_reference", client_payment_reference),
        ("cashflowCommentText", "cashflow_comment_text", cashflow_comment_text),
        ("cashflowExternalId", "cashflow_external_id", cashflow_external_id),
        ("factor", "factor", factor),
        ("price", "price", price),
        ("tradePar", "trade_par", trade_par),
        ("shortIndicator", "short_indicator", short_indicator),
        ("structuredBy", "structured_by", structured_by),
        ("settlementConfirmed", "settlement_confirmed", settlement_confirmed),
        ("duplicateNumber", "duplicate_number", duplicate_number),
        ("source", "source", source),
        ("accountingMethod", "accounting_method", accounting_method),
        ("version", "version", version),
        ("portfolioTicker", "portfolio_ticker", portfolio_ticker),
    ]
    body: dict[str, Any] = {}
    for api_key, _, value in field_map:
        if value is not None:
            body[api_key] = value
    return body


def register_miscellaneous_cashflow_tools(mcp: FastMCP) -> None:
    """Register Aladdin Miscellaneous Cashflow API tools with the MCP server."""

    @mcp.tool()
    def create_miscellaneous_cashflow(
        portfolio_id: str,
        currency_code: str,
        sub_transaction_type: str,
        trade_date: str,
        settle_date: str,
        principal: float | None = None,
        interest: float | None = None,
        commission: float | None = None,
        other_fee: float | None = None,
        original_face: float | None = None,
        asset_id: str | None = None,
        broker_id: str | None = None,
        entered_by: str | None = None,
        trader: str | None = None,
        strategy_id: int | None = None,
        exchange_rate: float | None = None,
        settlement_instruction_id: str | None = None,
        client_payment_reference: str | None = None,
        cashflow_comment_text: str | None = None,
        cashflow_external_id: dict[str, Any] | None = None,
        factor: float | None = None,
        price: float | None = None,
        trade_par: float | None = None,
        short_indicator: str | None = None,
        structured_by: str | None = None,
        duplicate_number: int | None = None,
        source: str | None = None,
        accounting_method: str | None = None,
        portfolio_ticker: str | None = None,
        validate_only: bool = False,
    ) -> str:
        """Create a miscellaneous cash (transaction_type=MISC) without SSI.

        Use validateOnly=True to run validations without posting the cashflow.
        To create with SSI, use create_miscellaneous_cashflow_and_default_settlement_instruction
        or create_miscellaneous_cashflow_and_send_transmission instead.

        Args:
            portfolio_id: Portfolio Code string identifier.
            currency_code: Currency code for the cashflow.
            sub_transaction_type: Cashflow sub-transaction type.
            trade_date: Trade date (YYYY-MM-DD).
            settle_date: Settlement date (YYYY-MM-DD).
            principal: Principal amount.
            interest: Interest amount.
            commission: Commission amount.
            other_fee: Other fee amount.
            original_face: Original face value.
            asset_id: Asset identifier.
            broker_id: Counterparty code for settlement.
            entered_by: User who entered the cashflow.
            trader: Trader identifier.
            strategy_id: Strategy identifier.
            exchange_rate: Exchange rate.
            settlement_instruction_id: Settle Code string value.
            client_payment_reference: Client payment reference.
            cashflow_comment_text: Comment text for the cashflow.
            cashflow_external_id: External cashflow ID dict with keys: externalId1, externalIdOrganization, externalId2, memo.
            factor: Factor value.
            price: Price value.
            trade_par: Trade par value.
            short_indicator: Short indicator.
            structured_by: Structured by identifier.
            duplicate_number: Duplicate number.
            source: Source identifier.
            accounting_method: Accounting method.
            portfolio_ticker: Portfolio ticker.
            validate_only: If True, only run validations without posting.
        """
        body = _build_cashflow_body(
            portfolio_id=portfolio_id,
            currency_code=currency_code,
            sub_transaction_type=sub_transaction_type,
            trade_date=trade_date,
            settle_date=settle_date,
            principal=principal,
            interest=interest,
            commission=commission,
            other_fee=other_fee,
            original_face=original_face,
            asset_id=asset_id,
            broker_id=broker_id,
            entered_by=entered_by,
            trader=trader,
            strategy_id=strategy_id,
            exchange_rate=exchange_rate,
            settlement_instruction_id=settlement_instruction_id,
            client_payment_reference=client_payment_reference,
            cashflow_comment_text=cashflow_comment_text,
            cashflow_external_id=cashflow_external_id,
            factor=factor,
            price=price,
            trade_par=trade_par,
            short_indicator=short_indicator,
            structured_by=structured_by,
            duplicate_number=duplicate_number,
            source=source,
            accounting_method=accounting_method,
            portfolio_ticker=portfolio_ticker,
        )
        params: dict[str, Any] | None = None
        if validate_only:
            params = {"validateOnly": True}

        return _call_api("/miscellaneousCashflows", http_method="post", request_body=body, params=params)

    @mcp.tool()
    def cancel_miscellaneous_cashflow(
        portfolio_id: str | None = None,
        investment_number: int | None = None,
        series_number: int | None = None,
        cashflow_external_id: dict[str, Any] | None = None,
        validate_only: bool = False,
        update_extern_id1: bool = False,
    ) -> str:
        """Cancel a miscellaneous cash without SSI by setting status to 'C'.

        A cashflow can be identified by either (portfolioId + investmentNumber + seriesNumber)
        or by (externalId1 + externalIdOrganization) via cashflowExternalId.

        Args:
            portfolio_id: Portfolio Code string identifier.
            investment_number: Cashflow investment number.
            series_number: Series number.
            cashflow_external_id: External ID dict with keys: externalId1, externalIdOrganization.
            validate_only: If True, only run validations without cancelling.
            update_extern_id1: Whether to update externalId1.
        """
        cashflow_body = _build_cashflow_body(
            portfolio_id=portfolio_id,
            investment_number=investment_number,
            series_number=series_number,
            cashflow_external_id=cashflow_external_id,
        )
        body: dict[str, Any] = {"miscellaneousCashflow": cashflow_body}
        if validate_only:
            body["validateOnly"] = True
        if update_extern_id1:
            body["updateExternId1"] = True

        return _call_api(
            "/miscellaneousCashflows:cancelMiscellaneousCashflow",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def cancel_miscellaneous_cashflow_and_send_transmission(
        portfolio_id: str | None = None,
        investment_number: int | None = None,
        series_number: int | None = None,
        cashflow_external_id: dict[str, Any] | None = None,
        validate_only: bool = False,
        update_extern_id1: bool = False,
    ) -> str:
        """Cancel a miscellaneous cash with SSI and send transmission.

        A cashflow can be identified by either (portfolioId + investmentNumber + seriesNumber)
        or by (externalId1 + externalIdOrganization) via cashflowExternalId.

        Args:
            portfolio_id: Portfolio Code string identifier.
            investment_number: Cashflow investment number.
            series_number: Series number.
            cashflow_external_id: External ID dict with keys: externalId1, externalIdOrganization.
            validate_only: If True, only run validations without cancelling.
            update_extern_id1: Whether to update externalId1.
        """
        cashflow_body = _build_cashflow_body(
            portfolio_id=portfolio_id,
            investment_number=investment_number,
            series_number=series_number,
            cashflow_external_id=cashflow_external_id,
        )
        body: dict[str, Any] = {"miscellaneousCashflow": cashflow_body}
        if validate_only:
            body["validateOnly"] = True
        if update_extern_id1:
            body["updateExternId1"] = True

        return _call_api(
            "/miscellaneousCashflows:cancelMiscellaneousCashflowAndSendTransmission",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def create_miscellaneous_cashflow_and_default_settlement_instruction(
        portfolio_id: str,
        currency_code: str,
        sub_transaction_type: str,
        trade_date: str,
        settle_date: str,
        principal: float | None = None,
        interest: float | None = None,
        commission: float | None = None,
        other_fee: float | None = None,
        original_face: float | None = None,
        asset_id: str | None = None,
        broker_id: str | None = None,
        entered_by: str | None = None,
        trader: str | None = None,
        strategy_id: int | None = None,
        exchange_rate: float | None = None,
        client_payment_reference: str | None = None,
        cashflow_comment_text: str | None = None,
        cashflow_external_id: dict[str, Any] | None = None,
        factor: float | None = None,
        price: float | None = None,
        trade_par: float | None = None,
        short_indicator: str | None = None,
        structured_by: str | None = None,
        duplicate_number: int | None = None,
        source: str | None = None,
        accounting_method: str | None = None,
        portfolio_ticker: str | None = None,
        validate_only: bool = False,
        suppress_defaulting_error: bool = False,
    ) -> str:
        """Create a miscellaneous cash and default the Standard Settlement Instruction (SSI).

        Args:
            portfolio_id: Portfolio Code string identifier.
            currency_code: Currency code for the cashflow.
            sub_transaction_type: Cashflow sub-transaction type.
            trade_date: Trade date (YYYY-MM-DD).
            settle_date: Settlement date (YYYY-MM-DD).
            principal: Principal amount.
            interest: Interest amount.
            commission: Commission amount.
            other_fee: Other fee amount.
            original_face: Original face value.
            asset_id: Asset identifier.
            broker_id: Counterparty code for settlement.
            entered_by: User who entered the cashflow.
            trader: Trader identifier.
            strategy_id: Strategy identifier.
            exchange_rate: Exchange rate.
            client_payment_reference: Client payment reference.
            cashflow_comment_text: Comment text for the cashflow.
            cashflow_external_id: External cashflow ID dict with keys: externalId1, externalIdOrganization, externalId2, memo.
            factor: Factor value.
            price: Price value.
            trade_par: Trade par value.
            short_indicator: Short indicator.
            structured_by: Structured by identifier.
            duplicate_number: Duplicate number.
            source: Source identifier.
            accounting_method: Accounting method.
            portfolio_ticker: Portfolio ticker.
            validate_only: If True, only run validations without posting.
            suppress_defaulting_error: If True, suppress SSI defaulting errors.
        """
        cashflow_body = _build_cashflow_body(
            portfolio_id=portfolio_id,
            currency_code=currency_code,
            sub_transaction_type=sub_transaction_type,
            trade_date=trade_date,
            settle_date=settle_date,
            principal=principal,
            interest=interest,
            commission=commission,
            other_fee=other_fee,
            original_face=original_face,
            asset_id=asset_id,
            broker_id=broker_id,
            entered_by=entered_by,
            trader=trader,
            strategy_id=strategy_id,
            exchange_rate=exchange_rate,
            client_payment_reference=client_payment_reference,
            cashflow_comment_text=cashflow_comment_text,
            cashflow_external_id=cashflow_external_id,
            factor=factor,
            price=price,
            trade_par=trade_par,
            short_indicator=short_indicator,
            structured_by=structured_by,
            duplicate_number=duplicate_number,
            source=source,
            accounting_method=accounting_method,
            portfolio_ticker=portfolio_ticker,
        )
        body: dict[str, Any] = {"miscellaneousCashflow": cashflow_body}
        if validate_only:
            body["validateOnly"] = True
        if suppress_defaulting_error:
            body["suppressDefaultingError"] = True

        return _call_api(
            "/miscellaneousCashflows:createMiscellaneousCashflowAndDefaultSettlementInstruction",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def create_miscellaneous_cashflow_and_send_transmission(
        portfolio_id: str,
        currency_code: str,
        sub_transaction_type: str,
        trade_date: str,
        settle_date: str,
        principal: float | None = None,
        interest: float | None = None,
        commission: float | None = None,
        other_fee: float | None = None,
        original_face: float | None = None,
        asset_id: str | None = None,
        broker_id: str | None = None,
        entered_by: str | None = None,
        trader: str | None = None,
        strategy_id: int | None = None,
        exchange_rate: float | None = None,
        settlement_instruction_id: str | None = None,
        client_payment_reference: str | None = None,
        cashflow_comment_text: str | None = None,
        cashflow_external_id: dict[str, Any] | None = None,
        factor: float | None = None,
        price: float | None = None,
        trade_par: float | None = None,
        short_indicator: str | None = None,
        structured_by: str | None = None,
        duplicate_number: int | None = None,
        source: str | None = None,
        accounting_method: str | None = None,
        portfolio_ticker: str | None = None,
        validate_only: bool = False,
    ) -> str:
        """Create a miscellaneous cash and send transmission (with SSI).

        Args:
            portfolio_id: Portfolio Code string identifier.
            currency_code: Currency code for the cashflow.
            sub_transaction_type: Cashflow sub-transaction type.
            trade_date: Trade date (YYYY-MM-DD).
            settle_date: Settlement date (YYYY-MM-DD).
            principal: Principal amount.
            interest: Interest amount.
            commission: Commission amount.
            other_fee: Other fee amount.
            original_face: Original face value.
            asset_id: Asset identifier.
            broker_id: Counterparty code for settlement.
            entered_by: User who entered the cashflow.
            trader: Trader identifier.
            strategy_id: Strategy identifier.
            exchange_rate: Exchange rate.
            settlement_instruction_id: Settle Code string value.
            client_payment_reference: Client payment reference.
            cashflow_comment_text: Comment text for the cashflow.
            cashflow_external_id: External cashflow ID dict with keys: externalId1, externalIdOrganization, externalId2, memo.
            factor: Factor value.
            price: Price value.
            trade_par: Trade par value.
            short_indicator: Short indicator.
            structured_by: Structured by identifier.
            duplicate_number: Duplicate number.
            source: Source identifier.
            accounting_method: Accounting method.
            portfolio_ticker: Portfolio ticker.
            validate_only: If True, only run validations without posting.
        """
        cashflow_body = _build_cashflow_body(
            portfolio_id=portfolio_id,
            currency_code=currency_code,
            sub_transaction_type=sub_transaction_type,
            trade_date=trade_date,
            settle_date=settle_date,
            principal=principal,
            interest=interest,
            commission=commission,
            other_fee=other_fee,
            original_face=original_face,
            asset_id=asset_id,
            broker_id=broker_id,
            entered_by=entered_by,
            trader=trader,
            strategy_id=strategy_id,
            exchange_rate=exchange_rate,
            settlement_instruction_id=settlement_instruction_id,
            client_payment_reference=client_payment_reference,
            cashflow_comment_text=cashflow_comment_text,
            cashflow_external_id=cashflow_external_id,
            factor=factor,
            price=price,
            trade_par=trade_par,
            short_indicator=short_indicator,
            structured_by=structured_by,
            duplicate_number=duplicate_number,
            source=source,
            accounting_method=accounting_method,
            portfolio_ticker=portfolio_ticker,
        )
        body: dict[str, Any] = {"miscellaneousCashflow": cashflow_body}
        if validate_only:
            body["validateOnly"] = True

        return _call_api(
            "/miscellaneousCashflows:createMiscellaneousCashflowAndSendTransmission",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def update_miscellaneous_cashflow(
        portfolio_id: str,
        investment_number: int,
        series_number: int,
        currency_code: str | None = None,
        broker_id: str | None = None,
        principal: float | None = None,
        interest: float | None = None,
        commission: float | None = None,
        other_fee: float | None = None,
        original_face: float | None = None,
        asset_id: str | None = None,
        trade_date: str | None = None,
        settle_date: str | None = None,
        sub_transaction_type: str | None = None,
        entered_by: str | None = None,
        trader: str | None = None,
        strategy_id: int | None = None,
        exchange_rate: float | None = None,
        settlement_instruction_id: str | None = None,
        client_payment_reference: str | None = None,
        cashflow_comment_text: str | None = None,
        cashflow_external_id: dict[str, Any] | None = None,
        factor: float | None = None,
        price: float | None = None,
        trade_par: float | None = None,
        short_indicator: str | None = None,
        structured_by: str | None = None,
        duplicate_number: int | None = None,
        source: str | None = None,
        accounting_method: str | None = None,
        version: int | None = None,
        portfolio_ticker: str | None = None,
        validate_only: bool = False,
    ) -> str:
        """Update a miscellaneous cash without SSI.

        Args:
            portfolio_id: Portfolio Code string identifier (required to identify cashflow).
            investment_number: Cashflow investment number (required to identify cashflow).
            series_number: Series number (required to identify cashflow).
            currency_code: Currency code for the cashflow.
            broker_id: Counterparty code for settlement.
            principal: Principal amount.
            interest: Interest amount.
            commission: Commission amount.
            other_fee: Other fee amount.
            original_face: Original face value.
            asset_id: Asset identifier.
            trade_date: Trade date (YYYY-MM-DD).
            settle_date: Settlement date (YYYY-MM-DD).
            sub_transaction_type: Cashflow sub-transaction type.
            entered_by: User who entered the cashflow.
            trader: Trader identifier.
            strategy_id: Strategy identifier.
            exchange_rate: Exchange rate.
            settlement_instruction_id: Settle Code string value.
            client_payment_reference: Client payment reference.
            cashflow_comment_text: Comment text for the cashflow.
            cashflow_external_id: External cashflow ID dict.
            factor: Factor value.
            price: Price value.
            trade_par: Trade par value.
            short_indicator: Short indicator.
            structured_by: Structured by identifier.
            duplicate_number: Duplicate number.
            source: Source identifier.
            accounting_method: Accounting method.
            version: Version number for optimistic locking.
            portfolio_ticker: Portfolio ticker.
            validate_only: If True, only run validations without updating.
        """
        body = _build_cashflow_body(
            portfolio_id=portfolio_id,
            investment_number=investment_number,
            series_number=series_number,
            currency_code=currency_code,
            broker_id=broker_id,
            principal=principal,
            interest=interest,
            commission=commission,
            other_fee=other_fee,
            original_face=original_face,
            asset_id=asset_id,
            trade_date=trade_date,
            settle_date=settle_date,
            sub_transaction_type=sub_transaction_type,
            entered_by=entered_by,
            trader=trader,
            strategy_id=strategy_id,
            exchange_rate=exchange_rate,
            settlement_instruction_id=settlement_instruction_id,
            client_payment_reference=client_payment_reference,
            cashflow_comment_text=cashflow_comment_text,
            cashflow_external_id=cashflow_external_id,
            factor=factor,
            price=price,
            trade_par=trade_par,
            short_indicator=short_indicator,
            structured_by=structured_by,
            duplicate_number=duplicate_number,
            source=source,
            accounting_method=accounting_method,
            version=version,
            portfolio_ticker=portfolio_ticker,
        )
        params: dict[str, Any] | None = None
        if validate_only:
            params = {"validateOnly": True}

        return _call_api(
            "/miscellaneousCashflows:updateMiscellaneousCashflow",
            http_method="patch",
            request_body=body,
            params=params,
        )

    @mcp.tool()
    def update_miscellaneous_cashflow_and_default_settlement_instruction(
        portfolio_id: str,
        investment_number: int,
        series_number: int,
        currency_code: str | None = None,
        broker_id: str | None = None,
        principal: float | None = None,
        interest: float | None = None,
        commission: float | None = None,
        other_fee: float | None = None,
        original_face: float | None = None,
        asset_id: str | None = None,
        trade_date: str | None = None,
        settle_date: str | None = None,
        sub_transaction_type: str | None = None,
        entered_by: str | None = None,
        trader: str | None = None,
        strategy_id: int | None = None,
        exchange_rate: float | None = None,
        client_payment_reference: str | None = None,
        cashflow_comment_text: str | None = None,
        cashflow_external_id: dict[str, Any] | None = None,
        factor: float | None = None,
        price: float | None = None,
        trade_par: float | None = None,
        short_indicator: str | None = None,
        structured_by: str | None = None,
        duplicate_number: int | None = None,
        source: str | None = None,
        accounting_method: str | None = None,
        version: int | None = None,
        portfolio_ticker: str | None = None,
        validate_only: bool = False,
        suppress_defaulting_error: bool = False,
    ) -> str:
        """Update a miscellaneous cash and default the Standard Settlement Instruction (SSI).

        Args:
            portfolio_id: Portfolio Code string identifier (required to identify cashflow).
            investment_number: Cashflow investment number (required to identify cashflow).
            series_number: Series number (required to identify cashflow).
            currency_code: Currency code for the cashflow.
            broker_id: Counterparty code for settlement.
            principal: Principal amount.
            interest: Interest amount.
            commission: Commission amount.
            other_fee: Other fee amount.
            original_face: Original face value.
            asset_id: Asset identifier.
            trade_date: Trade date (YYYY-MM-DD).
            settle_date: Settlement date (YYYY-MM-DD).
            sub_transaction_type: Cashflow sub-transaction type.
            entered_by: User who entered the cashflow.
            trader: Trader identifier.
            strategy_id: Strategy identifier.
            exchange_rate: Exchange rate.
            client_payment_reference: Client payment reference.
            cashflow_comment_text: Comment text for the cashflow.
            cashflow_external_id: External cashflow ID dict.
            factor: Factor value.
            price: Price value.
            trade_par: Trade par value.
            short_indicator: Short indicator.
            structured_by: Structured by identifier.
            duplicate_number: Duplicate number.
            source: Source identifier.
            accounting_method: Accounting method.
            version: Version number for optimistic locking.
            portfolio_ticker: Portfolio ticker.
            validate_only: If True, only run validations without updating.
            suppress_defaulting_error: If True, suppress SSI defaulting errors.
        """
        body = _build_cashflow_body(
            portfolio_id=portfolio_id,
            investment_number=investment_number,
            series_number=series_number,
            currency_code=currency_code,
            broker_id=broker_id,
            principal=principal,
            interest=interest,
            commission=commission,
            other_fee=other_fee,
            original_face=original_face,
            asset_id=asset_id,
            trade_date=trade_date,
            settle_date=settle_date,
            sub_transaction_type=sub_transaction_type,
            entered_by=entered_by,
            trader=trader,
            strategy_id=strategy_id,
            exchange_rate=exchange_rate,
            client_payment_reference=client_payment_reference,
            cashflow_comment_text=cashflow_comment_text,
            cashflow_external_id=cashflow_external_id,
            factor=factor,
            price=price,
            trade_par=trade_par,
            short_indicator=short_indicator,
            structured_by=structured_by,
            duplicate_number=duplicate_number,
            source=source,
            accounting_method=accounting_method,
            version=version,
            portfolio_ticker=portfolio_ticker,
        )
        params: dict[str, Any] | None = None
        if validate_only:
            params = {"validateOnly": True}
        if suppress_defaulting_error:
            params = params or {}
            params["suppressDefaultingError"] = True

        return _call_api(
            "/miscellaneousCashflows:updateMiscellaneousCashflowAndDefaultSettlementInstruction",
            http_method="patch",
            request_body=body,
            params=params,
        )

    @mcp.tool()
    def update_miscellaneous_cashflow_and_send_transmission(
        portfolio_id: str,
        investment_number: int,
        series_number: int,
        currency_code: str | None = None,
        broker_id: str | None = None,
        principal: float | None = None,
        interest: float | None = None,
        commission: float | None = None,
        other_fee: float | None = None,
        original_face: float | None = None,
        asset_id: str | None = None,
        trade_date: str | None = None,
        settle_date: str | None = None,
        sub_transaction_type: str | None = None,
        entered_by: str | None = None,
        trader: str | None = None,
        strategy_id: int | None = None,
        exchange_rate: float | None = None,
        settlement_instruction_id: str | None = None,
        client_payment_reference: str | None = None,
        cashflow_comment_text: str | None = None,
        cashflow_external_id: dict[str, Any] | None = None,
        factor: float | None = None,
        price: float | None = None,
        trade_par: float | None = None,
        short_indicator: str | None = None,
        structured_by: str | None = None,
        duplicate_number: int | None = None,
        source: str | None = None,
        accounting_method: str | None = None,
        version: int | None = None,
        portfolio_ticker: str | None = None,
        validate_only: bool = False,
    ) -> str:
        """Update a miscellaneous cash and send transmission (with SSI).

        Args:
            portfolio_id: Portfolio Code string identifier (required to identify cashflow).
            investment_number: Cashflow investment number (required to identify cashflow).
            series_number: Series number (required to identify cashflow).
            currency_code: Currency code for the cashflow.
            broker_id: Counterparty code for settlement.
            principal: Principal amount.
            interest: Interest amount.
            commission: Commission amount.
            other_fee: Other fee amount.
            original_face: Original face value.
            asset_id: Asset identifier.
            trade_date: Trade date (YYYY-MM-DD).
            settle_date: Settlement date (YYYY-MM-DD).
            sub_transaction_type: Cashflow sub-transaction type.
            entered_by: User who entered the cashflow.
            trader: Trader identifier.
            strategy_id: Strategy identifier.
            exchange_rate: Exchange rate.
            settlement_instruction_id: Settle Code string value.
            client_payment_reference: Client payment reference.
            cashflow_comment_text: Comment text for the cashflow.
            cashflow_external_id: External cashflow ID dict.
            factor: Factor value.
            price: Price value.
            trade_par: Trade par value.
            short_indicator: Short indicator.
            structured_by: Structured by identifier.
            duplicate_number: Duplicate number.
            source: Source identifier.
            accounting_method: Accounting method.
            version: Version number for optimistic locking.
            portfolio_ticker: Portfolio ticker.
            validate_only: If True, only run validations without updating.
        """
        body = _build_cashflow_body(
            portfolio_id=portfolio_id,
            investment_number=investment_number,
            series_number=series_number,
            currency_code=currency_code,
            broker_id=broker_id,
            principal=principal,
            interest=interest,
            commission=commission,
            other_fee=other_fee,
            original_face=original_face,
            asset_id=asset_id,
            trade_date=trade_date,
            settle_date=settle_date,
            sub_transaction_type=sub_transaction_type,
            entered_by=entered_by,
            trader=trader,
            strategy_id=strategy_id,
            exchange_rate=exchange_rate,
            settlement_instruction_id=settlement_instruction_id,
            client_payment_reference=client_payment_reference,
            cashflow_comment_text=cashflow_comment_text,
            cashflow_external_id=cashflow_external_id,
            factor=factor,
            price=price,
            trade_par=trade_par,
            short_indicator=short_indicator,
            structured_by=structured_by,
            duplicate_number=duplicate_number,
            source=source,
            accounting_method=accounting_method,
            version=version,
            portfolio_ticker=portfolio_ticker,
        )
        params: dict[str, Any] | None = None
        if validate_only:
            params = {"validateOnly": True}

        return _call_api(
            "/miscellaneousCashflows:updateMiscellaneousCashflowAndSendTransmission",
            http_method="patch",
            request_body=body,
            params=params,
        )
