"""MCP tools for the Aladdin Coupon Reset API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_COUPON_RESET_BASE_PATH = "/api/investment-operations/asset-lifecycle/coupon-reset/v1/"

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


def _call_coupon_reset_api(
    endpoint_path: str,
    http_method: str = "get",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Coupon Reset API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_COUPON_RESET_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Coupon Reset API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def _build_coupon_reset_dict(
    asset_id: str | None = None,
    reset_date: str | None = None,
    determination_date: str | None = None,
    coupon: float | None = None,
    index_value: float | None = None,
    next_determination_date: str | None = None,
    next_reset_date: str | None = None,
    status: str | None = None,
    coupon_source: str | None = None,
    calculation_date: str | None = None,
    confirmer: str | None = None,
    quoted_date: str | None = None,
    coupon_reset_id: str | None = None,
) -> dict[str, Any]:
    """Build a coupon reset body dict, filtering out None values."""
    entry: dict[str, Any] = {}
    if coupon_reset_id is not None:
        entry["id"] = coupon_reset_id
    if asset_id is not None:
        entry["assetId"] = asset_id
    if reset_date is not None:
        entry["resetDate"] = reset_date
    if determination_date is not None:
        entry["determinationDate"] = determination_date
    if coupon is not None:
        entry["coupon"] = coupon
    if index_value is not None:
        entry["indexValue"] = index_value
    if next_determination_date is not None:
        entry["nextDeterminationDate"] = next_determination_date
    if next_reset_date is not None:
        entry["nextResetDate"] = next_reset_date
    if status is not None:
        entry["status"] = status
    if coupon_source is not None:
        entry["couponSource"] = coupon_source
    if calculation_date is not None:
        entry["calculationDate"] = calculation_date
    if confirmer is not None:
        entry["confirmer"] = confirmer
    if quoted_date is not None:
        entry["quotedDate"] = quoted_date
    return entry


def register_coupon_reset_tools(mcp: FastMCP) -> None:
    """Register Aladdin Coupon Reset API tools with the MCP server."""

    @mcp.tool()
    def get_coupon_reset(
        asset_id: str | None = None,
        reset_date: str | None = None,
    ) -> str:
        """Retrieve a single Coupon Reset record for a specified asset and reset date.

        Args:
            asset_id: The asset identifier.
            reset_date: The reset date (YYYY-MM-DD).
        """
        params: dict[str, Any] = {}
        if asset_id is not None:
            params["assetId"] = asset_id
        if reset_date is not None:
            params["resetDate"] = reset_date

        return _call_coupon_reset_api(
            "/couponResets",
            http_method="get",
            params=params if params else None,
        )

    @mcp.tool()
    def create_coupon_reset(
        asset_id: str,
        reset_date: str,
        coupon: float,
        determination_date: str | None = None,
        index_value: float | None = None,
        next_determination_date: str | None = None,
        next_reset_date: str | None = None,
        status: str | None = None,
        coupon_source: str | None = None,
        calculation_date: str | None = None,
        confirmer: str | None = None,
        quoted_date: str | None = None,
    ) -> str:
        """Create a new Coupon Reset record.

        Args:
            asset_id: The asset identifier.
            reset_date: The reset date (YYYY-MM-DD).
            coupon: The coupon value.
            determination_date: Index lookup date (YYYY-MM-DD).
            index_value: Index value used for coupon calculation.
            next_determination_date: Next determination date (YYYY-MM-DD).
            next_reset_date: Next reset date (YYYY-MM-DD).
            status: Reset status (STATE_UNSPECIFIED, STATE_DONE, STATE_ERROR, STATE_WAIT, STATE_MANUAL).
            coupon_source: Source of the reset (e.g. BRM, TradeEntry, RepoTrader, or a user).
            calculation_date: Calculation date (YYYY-MM-DD).
            confirmer: User ID of the confirmer.
            quoted_date: Coupon date as quoted by data provider (YYYY-MM-DD).
        """
        body = _build_coupon_reset_dict(
            asset_id=asset_id,
            reset_date=reset_date,
            coupon=coupon,
            determination_date=determination_date,
            index_value=index_value,
            next_determination_date=next_determination_date,
            next_reset_date=next_reset_date,
            status=status,
            coupon_source=coupon_source,
            calculation_date=calculation_date,
            confirmer=confirmer,
            quoted_date=quoted_date,
        )
        return _call_coupon_reset_api("/couponResets", http_method="post", request_body=body)

    @mcp.tool()
    def update_coupon_reset(
        asset_id: str,
        reset_date: str,
        coupon_reset_id: str | None = None,
        coupon: float | None = None,
        determination_date: str | None = None,
        index_value: float | None = None,
        next_determination_date: str | None = None,
        next_reset_date: str | None = None,
        status: str | None = None,
        coupon_source: str | None = None,
        calculation_date: str | None = None,
        confirmer: str | None = None,
        quoted_date: str | None = None,
        update_mask: str | None = None,
    ) -> str:
        """Update certain fields of a single Coupon Reset record.

        Only the fields provided will be updated. Use update_mask to specify
        exactly which fields to update.

        Args:
            asset_id: The asset identifier.
            reset_date: The reset date (YYYY-MM-DD).
            coupon_reset_id: The coupon reset record ID.
            coupon: The coupon value.
            determination_date: Index lookup date (YYYY-MM-DD).
            index_value: Index value used for coupon calculation.
            next_determination_date: Next determination date (YYYY-MM-DD).
            next_reset_date: Next reset date (YYYY-MM-DD).
            status: Reset status (STATE_UNSPECIFIED, STATE_DONE, STATE_ERROR, STATE_WAIT, STATE_MANUAL).
            coupon_source: Source of the reset.
            calculation_date: Calculation date (YYYY-MM-DD).
            confirmer: User ID of the confirmer.
            quoted_date: Coupon date as quoted by data provider (YYYY-MM-DD).
            update_mask: Comma-separated list of fields to update (e.g. "coupon,status").
        """
        body = _build_coupon_reset_dict(
            asset_id=asset_id,
            reset_date=reset_date,
            coupon_reset_id=coupon_reset_id,
            coupon=coupon,
            determination_date=determination_date,
            index_value=index_value,
            next_determination_date=next_determination_date,
            next_reset_date=next_reset_date,
            status=status,
            coupon_source=coupon_source,
            calculation_date=calculation_date,
            confirmer=confirmer,
            quoted_date=quoted_date,
        )
        params: dict[str, Any] | None = None
        if update_mask is not None:
            params = {"updateMask": update_mask}

        return _call_coupon_reset_api(
            "/couponResets",
            http_method="patch",
            request_body=body,
            params=params,
        )

    @mcp.tool()
    def batch_create_coupon_resets(
        coupon_resets: list[dict[str, Any]],
    ) -> str:
        """Batch create multiple Coupon Reset records.

        Args:
            coupon_resets: List of coupon reset dicts to create. Each dict can have:
                          assetId (str), resetDate (date str YYYY-MM-DD),
                          determinationDate (date str), coupon (float),
                          indexValue (float), nextDeterminationDate (date str),
                          nextResetDate (date str), status (str), couponSource (str),
                          calculationDate (date str), confirmer (str), quotedDate (date str).
        """
        requests: list[dict[str, Any]] = [
            {"couponReset": cr} for cr in coupon_resets
        ]
        body: dict[str, Any] = {"requests": requests}
        return _call_coupon_reset_api(
            "/couponResets:batchCreate",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def batch_update_coupon_resets(
        coupon_resets: list[dict[str, Any]],
        update_mask: str | None = None,
    ) -> str:
        """Batch update multiple Coupon Reset records.

        Args:
            coupon_resets: List of coupon reset dicts to update. Each dict can have:
                          id (str), assetId (str), resetDate (date str YYYY-MM-DD),
                          determinationDate (date str), coupon (float),
                          indexValue (float), nextDeterminationDate (date str),
                          nextResetDate (date str), status (str), couponSource (str),
                          calculationDate (date str), confirmer (str), quotedDate (date str).
            update_mask: Comma-separated list of fields to update, applied to all records.
        """
        requests: list[dict[str, Any]] = []
        for cr in coupon_resets:
            req: dict[str, Any] = {"couponReset": cr}
            if update_mask is not None:
                req["updateMask"] = update_mask
            requests.append(req)
        body: dict[str, Any] = {"requests": requests}
        return _call_coupon_reset_api(
            "/couponResets:batchUpdate",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def filter_coupon_resets(
        asset_id: str,
        accrual_start_date: str,
        accrual_end_date: str,
    ) -> str:
        """Filter Coupon Reset records by asset ID and accrual date range.

        Args:
            asset_id: The asset identifier.
            accrual_start_date: Accrual start date (YYYY-MM-DD).
            accrual_end_date: Accrual end date (YYYY-MM-DD).
        """
        params: dict[str, Any] = {
            "query.assetId": asset_id,
            "query.accrualStartDate": accrual_start_date,
            "query.accrualEndDate": accrual_end_date,
        }
        return _call_coupon_reset_api(
            "/couponResets:filter",
            http_method="get",
            params=params,
        )

    @mcp.tool()
    def filter_coupon_resets_by_parameters(
        filter_criteria: list[dict[str, Any]],
    ) -> str:
        """Filter Coupon Reset records by various parameters.

        Allows retrieval of coupon resets using flexible filter criteria
        with logical operators and comparisons.

        Args:
            filter_criteria: List of filter criteria dicts. Each dict can have:
                - filterParams: list of filter parameter dicts, each with:
                    - parameterName: one of COUPON_RESET_PARAMETER_NAME_ASSET_IDS,
                      COUPON_RESET_PARAMETER_NAME_RESET_DATE,
                      COUPON_RESET_PARAMETER_NAME_NEXT_RESET_DATE,
                      COUPON_RESET_PARAMETER_NAME_DETERMINATION_DATE,
                      COUPON_RESET_PARAMETER_NAME_NEXT_DETERMINATION_DATE,
                      COUPON_RESET_PARAMETER_NAME_MODIFY_DATE,
                      COUPON_RESET_PARAMETER_NAME_SECURITY_GROUP_AND_TYPE,
                      COUPON_RESET_PARAMETER_NAME_POS_DATE,
                      COUPON_RESET_PARAMETER_NAME_CURRENCIES,
                      COUPON_RESET_PARAMETER_NAME_SOURCE,
                      COUPON_RESET_PARAMETER_NAME_STATUS,
                      COUPON_RESET_PARAMETER_NAME_CONFIRMED_STATUS,
                      COUPON_RESET_PARAMETER_NAME_CONFIRMED_BY
                    - parameterValue: dict with one of singleValue, repeatedValue,
                      rangeValue, or assetFilter
                    - selfOperator: one of COMPARISON_EQUALS, COMPARISON_NOT_EQUALS,
                      COMPARISON_LESS_THAN, COMPARISON_LESS_EQUALS,
                      COMPARISON_GREATER_THAN, COMPARISON_GREATER_EQUALS
                - predicatesOperator: logical operator (LOGICAL_OR, LOGICAL_AND, LOGICAL_NOT)
        """
        body: dict[str, Any] = {
            "query": {
                "filterCriteria": filter_criteria,
            },
        }
        return _call_coupon_reset_api(
            "/couponResets:filterByParameters",
            http_method="post",
            request_body=body,
        )
