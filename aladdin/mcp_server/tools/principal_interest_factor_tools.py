"""MCP tools for the Aladdin Principal Interest Factor API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_PIF_BASE_PATH = "/api/investment-operations/asset-lifecycle/principal-interest-factor/v1/"

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


def _call_pif_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Principal Interest Factor API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_PIF_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"PIF API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def _build_pif_body(
    asset_id: str | None = None,
    record_date: str | None = None,
    payment_date: str | None = None,
    currency_code: str | None = None,
    principal_state: str | None = None,
    interest_state: str | None = None,
    principal: float | None = None,
    principal_accrual_date: str | None = None,
    factor: float | None = None,
    previous_factor: float | None = None,
    interest: float | None = None,
    interest_accrual_date: str | None = None,
    coupon: float | None = None,
    period_day_count: int | None = None,
    date_calc_basis: str | None = None,
    entry_date: str | None = None,
    source: str | None = None,
    next_payment_date: str | None = None,
    user_principal: float | None = None,
    user_interest: float | None = None,
    pif_comment: str | None = None,
    nominal_payment_date: str | None = None,
    confirmer: str | None = None,
    recon_source: str | None = None,
    interest_accrual_end_date: str | None = None,
    suspension_date: str | None = None,
    coupon_source: str | None = None,
    settlement_code: int | None = None,
    final_payment: bool | None = None,
    fixing_rate: float | None = None,
    fixing_date: str | None = None,
    sequence_number: int | None = None,
) -> dict[str, Any]:
    """Build a PIF body dict, filtering out None values."""
    field_map: list[tuple[str, str, Any]] = [
        ("assetId", "asset_id", asset_id),
        ("recordDate", "record_date", record_date),
        ("paymentDate", "payment_date", payment_date),
        ("currencyCode", "currency_code", currency_code),
        ("principalState", "principal_state", principal_state),
        ("interestState", "interest_state", interest_state),
        ("principal", "principal", principal),
        ("principalAccrualDate", "principal_accrual_date", principal_accrual_date),
        ("factor", "factor", factor),
        ("previousFactor", "previous_factor", previous_factor),
        ("interest", "interest", interest),
        ("interestAccrualDate", "interest_accrual_date", interest_accrual_date),
        ("coupon", "coupon", coupon),
        ("periodDayCount", "period_day_count", period_day_count),
        ("dateCalcBasis", "date_calc_basis", date_calc_basis),
        ("entryDate", "entry_date", entry_date),
        ("source", "source", source),
        ("nextPaymentDate", "next_payment_date", next_payment_date),
        ("userPrincipal", "user_principal", user_principal),
        ("userInterest", "user_interest", user_interest),
        ("pifComment", "pif_comment", pif_comment),
        ("nominalPaymentDate", "nominal_payment_date", nominal_payment_date),
        ("confirmer", "confirmer", confirmer),
        ("reconSource", "recon_source", recon_source),
        ("interestAccrualEndDate", "interest_accrual_end_date", interest_accrual_end_date),
        ("suspensionDate", "suspension_date", suspension_date),
        ("couponSource", "coupon_source", coupon_source),
        ("settlementCode", "settlement_code", settlement_code),
        ("finalPayment", "final_payment", final_payment),
        ("fixingRate", "fixing_rate", fixing_rate),
        ("fixingDate", "fixing_date", fixing_date),
        ("sequenceNumber", "sequence_number", sequence_number),
    ]
    body: dict[str, Any] = {}
    for api_key, _, value in field_map:
        if value is not None:
            body[api_key] = value
    return body


def register_principal_interest_factor_tools(mcp: FastMCP) -> None:
    """Register Aladdin Principal Interest Factor API tools with the MCP server."""

    @mcp.tool()
    def get_principal_interest_factor(
        asset_id: str,
        record_date: str,
        payment_date: str,
        currency_code: str,
    ) -> str:
        """Retrieve a unique Principal Interest Factor (PIF) record.

        PIFs represent the amount of payment per 1000 of Original Face currency
        units value held in the given asset, used with position data to generate
        cashflows.

        Args:
            asset_id: Asset Identifier.
            record_date: Record date of the PIF (i.e. trade date), format YYYY-MM-DD.
            payment_date: Payment date of the PIF (i.e. settle date), format YYYY-MM-DD.
            currency_code: Currency code (e.g. USD, EUR).
        """
        params: dict[str, Any] = {
            "key.assetId": asset_id,
            "key.recordDate": record_date,
            "key.paymentDate": payment_date,
            "key.currencyCode": currency_code,
        }
        return _call_pif_api(
            "/principalInterestFactor",
            http_method="get",
            params=params,
        )

    @mcp.tool()
    def delete_principal_interest_factor(
        asset_id: str,
        record_date: str,
        payment_date: str,
        currency_code: str,
    ) -> str:
        """Delete a Principal Interest Factor (PIF) record.

        Args:
            asset_id: Asset Identifier.
            record_date: Record date of the PIF (i.e. trade date), format YYYY-MM-DD.
            payment_date: Payment date of the PIF (i.e. settle date), format YYYY-MM-DD.
            currency_code: Currency code (e.g. USD, EUR).
        """
        params: dict[str, Any] = {
            "key.assetId": asset_id,
            "key.recordDate": record_date,
            "key.paymentDate": payment_date,
            "key.currencyCode": currency_code,
        }
        return _call_pif_api(
            "/principalInterestFactor",
            http_method="delete",
            params=params,
        )

    @mcp.tool()
    def create_principal_interest_factor(
        asset_id: str,
        record_date: str,
        payment_date: str,
        currency_code: str,
        principal_state: str | None = None,
        interest_state: str | None = None,
        principal: float | None = None,
        principal_accrual_date: str | None = None,
        factor: float | None = None,
        previous_factor: float | None = None,
        interest: float | None = None,
        interest_accrual_date: str | None = None,
        coupon: float | None = None,
        period_day_count: int | None = None,
        date_calc_basis: str | None = None,
        entry_date: str | None = None,
        source: str | None = None,
        next_payment_date: str | None = None,
        user_principal: float | None = None,
        user_interest: float | None = None,
        pif_comment: str | None = None,
        nominal_payment_date: str | None = None,
        confirmer: str | None = None,
        recon_source: str | None = None,
        interest_accrual_end_date: str | None = None,
        suspension_date: str | None = None,
        coupon_source: str | None = None,
        settlement_code: int | None = None,
        final_payment: bool | None = None,
        fixing_rate: float | None = None,
        fixing_date: str | None = None,
        sequence_number: int | None = None,
    ) -> str:
        """Create a new Principal Interest Factor (PIF) record.

        Args:
            asset_id: Asset Identifier.
            record_date: Record date of the PIF (i.e. trade date), format YYYY-MM-DD.
            payment_date: Payment date of the PIF (i.e. settle date), format YYYY-MM-DD.
            currency_code: Currency code (e.g. USD, EUR).
            principal_state: Principal state (STATE_UNSPECIFIED, STATE_PROJECTED, STATE_DONE, STATE_ERROR, STATE_FACTOR_WAIT, STATE_MANUAL).
            interest_state: Interest state (STATE_UNSPECIFIED, STATE_PROJECTED, STATE_DONE, STATE_ERROR, STATE_FACTOR_WAIT, STATE_MANUAL).
            principal: Principal value.
            principal_accrual_date: Principal accrual date, format YYYY-MM-DD.
            factor: Factor used for p/i calculation.
            previous_factor: Previous period's factor.
            interest: Interest value.
            interest_accrual_date: Interest accrual date, format YYYY-MM-DD.
            coupon: Coupon value used for p/i calculation.
            period_day_count: Number of days in this period.
            date_calc_basis: Day count basis used for calculations.
            entry_date: Entry date of the PIF, format YYYY-MM-DD.
            source: Source of this PIF (controlled by decode PMT_SOURCE).
            next_payment_date: Next payment date, format YYYY-MM-DD.
            user_principal: User specified principal value.
            user_interest: User specified interest value.
            pif_comment: Comment on the PIF.
            nominal_payment_date: Nominal (unadjusted) payment date, format YYYY-MM-DD.
            confirmer: User-id of the confirmer.
            recon_source: Source against which this PIF has been reconciled (controlled by decode REMIT_SOURCE).
            interest_accrual_end_date: End of interest accrual range, format YYYY-MM-DD.
            suspension_date: Factor/Coupon suspension date, format YYYY-MM-DD.
            coupon_source: Source of coupon (controlled by decode PMT_CPN_SOURCE).
            settlement_code: Settlement code.
            final_payment: Whether this is the final payment.
            fixing_rate: Fixing rate.
            fixing_date: Fixing date, format YYYY-MM-DD.
            sequence_number: Sequence number.
        """
        pif_body = _build_pif_body(
            asset_id=asset_id,
            record_date=record_date,
            payment_date=payment_date,
            currency_code=currency_code,
            principal_state=principal_state,
            interest_state=interest_state,
            principal=principal,
            principal_accrual_date=principal_accrual_date,
            factor=factor,
            previous_factor=previous_factor,
            interest=interest,
            interest_accrual_date=interest_accrual_date,
            coupon=coupon,
            period_day_count=period_day_count,
            date_calc_basis=date_calc_basis,
            entry_date=entry_date,
            source=source,
            next_payment_date=next_payment_date,
            user_principal=user_principal,
            user_interest=user_interest,
            pif_comment=pif_comment,
            nominal_payment_date=nominal_payment_date,
            confirmer=confirmer,
            recon_source=recon_source,
            interest_accrual_end_date=interest_accrual_end_date,
            suspension_date=suspension_date,
            coupon_source=coupon_source,
            settlement_code=settlement_code,
            final_payment=final_payment,
            fixing_rate=fixing_rate,
            fixing_date=fixing_date,
            sequence_number=sequence_number,
        )
        body: dict[str, Any] = {"principalInterestFactor": pif_body}
        return _call_pif_api("/principalInterestFactors", http_method="post", request_body=body)

    @mcp.tool()
    def update_principal_interest_factor(
        asset_id: str,
        record_date: str,
        payment_date: str,
        currency_code: str,
        update_mask: str | None = None,
        principal_state: str | None = None,
        interest_state: str | None = None,
        principal: float | None = None,
        principal_accrual_date: str | None = None,
        factor: float | None = None,
        previous_factor: float | None = None,
        interest: float | None = None,
        interest_accrual_date: str | None = None,
        coupon: float | None = None,
        period_day_count: int | None = None,
        date_calc_basis: str | None = None,
        entry_date: str | None = None,
        source: str | None = None,
        next_payment_date: str | None = None,
        user_principal: float | None = None,
        user_interest: float | None = None,
        pif_comment: str | None = None,
        nominal_payment_date: str | None = None,
        confirmer: str | None = None,
        recon_source: str | None = None,
        interest_accrual_end_date: str | None = None,
        suspension_date: str | None = None,
        coupon_source: str | None = None,
        settlement_code: int | None = None,
        final_payment: bool | None = None,
        fixing_rate: float | None = None,
        fixing_date: str | None = None,
        sequence_number: int | None = None,
    ) -> str:
        """Update an existing Principal Interest Factor (PIF) record.

        Only the fields provided will be updated. Use update_mask to specify
        exactly which fields to update.

        Args:
            asset_id: Asset Identifier.
            record_date: Record date of the PIF (i.e. trade date), format YYYY-MM-DD.
            payment_date: Payment date of the PIF (i.e. settle date), format YYYY-MM-DD.
            currency_code: Currency code (e.g. USD, EUR).
            update_mask: Comma-separated list of fields to update (e.g. "principal,interest").
            principal_state: Principal state (STATE_UNSPECIFIED, STATE_PROJECTED, STATE_DONE, STATE_ERROR, STATE_FACTOR_WAIT, STATE_MANUAL).
            interest_state: Interest state (STATE_UNSPECIFIED, STATE_PROJECTED, STATE_DONE, STATE_ERROR, STATE_FACTOR_WAIT, STATE_MANUAL).
            principal: Principal value.
            principal_accrual_date: Principal accrual date, format YYYY-MM-DD.
            factor: Factor used for p/i calculation.
            previous_factor: Previous period's factor.
            interest: Interest value.
            interest_accrual_date: Interest accrual date, format YYYY-MM-DD.
            coupon: Coupon value used for p/i calculation.
            period_day_count: Number of days in this period.
            date_calc_basis: Day count basis used for calculations.
            entry_date: Entry date of the PIF, format YYYY-MM-DD.
            source: Source of this PIF (controlled by decode PMT_SOURCE).
            next_payment_date: Next payment date, format YYYY-MM-DD.
            user_principal: User specified principal value.
            user_interest: User specified interest value.
            pif_comment: Comment on the PIF.
            nominal_payment_date: Nominal (unadjusted) payment date, format YYYY-MM-DD.
            confirmer: User-id of the confirmer.
            recon_source: Source against which this PIF has been reconciled (controlled by decode REMIT_SOURCE).
            interest_accrual_end_date: End of interest accrual range, format YYYY-MM-DD.
            suspension_date: Factor/Coupon suspension date, format YYYY-MM-DD.
            coupon_source: Source of coupon (controlled by decode PMT_CPN_SOURCE).
            settlement_code: Settlement code.
            final_payment: Whether this is the final payment.
            fixing_rate: Fixing rate.
            fixing_date: Fixing date, format YYYY-MM-DD.
            sequence_number: Sequence number.
        """
        pif_body = _build_pif_body(
            asset_id=asset_id,
            record_date=record_date,
            payment_date=payment_date,
            currency_code=currency_code,
            principal_state=principal_state,
            interest_state=interest_state,
            principal=principal,
            principal_accrual_date=principal_accrual_date,
            factor=factor,
            previous_factor=previous_factor,
            interest=interest,
            interest_accrual_date=interest_accrual_date,
            coupon=coupon,
            period_day_count=period_day_count,
            date_calc_basis=date_calc_basis,
            entry_date=entry_date,
            source=source,
            next_payment_date=next_payment_date,
            user_principal=user_principal,
            user_interest=user_interest,
            pif_comment=pif_comment,
            nominal_payment_date=nominal_payment_date,
            confirmer=confirmer,
            recon_source=recon_source,
            interest_accrual_end_date=interest_accrual_end_date,
            suspension_date=suspension_date,
            coupon_source=coupon_source,
            settlement_code=settlement_code,
            final_payment=final_payment,
            fixing_rate=fixing_rate,
            fixing_date=fixing_date,
            sequence_number=sequence_number,
        )
        request_body: dict[str, Any] = pif_body
        params: dict[str, Any] | None = None
        if update_mask is not None:
            params = {"updateMask": update_mask}

        return _call_pif_api(
            "/principalInterestFactors",
            http_method="patch",
            request_body=request_body,
            params=params,
        )

    @mcp.tool()
    def batch_create_principal_interest_factors(
        pif_records: list[dict[str, Any]],
    ) -> str:
        """Batch create multiple Principal Interest Factor (PIF) records.

        Args:
            pif_records: List of PIF dicts to create. Each dict should contain
                         a "principalInterestFactor" key with PIF fields:
                         assetId, recordDate (YYYY-MM-DD), paymentDate (YYYY-MM-DD),
                         currencyCode, principal, interest, factor, etc.
        """
        body: dict[str, Any] = {"requests": pif_records}
        return _call_pif_api("/principalInterestFactors:batchCreate", http_method="post", request_body=body)

    @mcp.tool()
    def batch_update_principal_interest_factors(
        pif_records: list[dict[str, Any]],
    ) -> str:
        """Batch update multiple Principal Interest Factor (PIF) records.

        Args:
            pif_records: List of PIF update request dicts. Each dict should contain
                         "principalInterestFactor" (with PIF fields to update) and
                         optionally "updateMask" (comma-separated field names).
        """
        body: dict[str, Any] = {"requests": pif_records}
        return _call_pif_api("/principalInterestFactors:batchUpdate", http_method="post", request_body=body)

    @mcp.tool()
    def filter_principal_interest_factors(
        filter_criteria: list[dict[str, Any]],
    ) -> str:
        """Filter Principal Interest Factor (PIF) records based on criteria.

        Criteria are AND'ed together (maximum 10 criteria).

        Args:
            filter_criteria: List of filter criteria dicts. Each dict should have:
                             - filterParams (list of filter parameter dicts)
                             - predicatesOperator (optional, logical operator for predicates)
        """
        body: dict[str, Any] = {
            "query": {
                "filterCriteria": filter_criteria,
            },
        }
        return _call_pif_api("/principalInterestFactors:filter", http_method="post", request_body=body)

    @mcp.tool()
    def list_principal_interest_factors(
        keys: list[dict[str, Any]],
    ) -> str:
        """List Principal Interest Factor (PIF) records by composite keys.

        Args:
            keys: List of key dicts, each containing:
                  - assetId (str, required): Asset Identifier.
                  - recordDate (str, required): Record date (YYYY-MM-DD).
                  - paymentDate (str, required): Payment date (YYYY-MM-DD).
                  - currencyCode (str, required): Currency code.
        """
        body: dict[str, Any] = {"keys": keys}
        return _call_pif_api("/principalInterestFactors:list", http_method="post", request_body=body)

    @mcp.tool()
    def filter_principal_interest_factor_audit_trails(
        asset_id: str,
        record_date: str,
        payment_date: str,
        currency_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter audit trails for a specific Principal Interest Factor (PIF).

        Args:
            asset_id: Asset Identifier for the PIF.
            record_date: Record date of the PIF (YYYY-MM-DD).
            payment_date: Payment date of the PIF (YYYY-MM-DD).
            currency_code: Currency code.
            start_date: Start date for when revision was made (YYYY-MM-DD).
            end_date: End date for when revision was made (YYYY-MM-DD).
            page_size: Maximum number of audit records to return (default 5000).
            page_token: Token for retrieving the next page of results.
        """
        query: dict[str, Any] = {
            "key": {
                "assetId": asset_id,
                "recordDate": record_date,
                "paymentDate": payment_date,
                "currencyCode": currency_code,
            },
        }
        if start_date is not None:
            query["startDate"] = start_date
        if end_date is not None:
            query["endDate"] = end_date

        body: dict[str, Any] = {"query": query}
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_pif_api(
            "/principalInterestFactorAuditTrails:filter",
            http_method="post",
            request_body=body,
        )
