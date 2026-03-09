"""MCP tools for the Aladdin ESG Data API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_ESG_DATA_BASE_PATH = "/api/analytics/data/esg/v1/"

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


def _call_esg_data_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call an ESG Data API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_ESG_DATA_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"ESG Data API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_esg_data_tools(mcp: FastMCP) -> None:
    """Register Aladdin ESG Data API tools with the MCP server."""

    @mcp.tool()
    def retrieve_esg_data_as_of_date(
        ids: list[str],
        id_type: str,
        as_of_date: str,
        provider_measures: list[dict[str, Any]],
        issuer_traversal: bool | None = None,
        ignore_default_issuer_traversal: bool | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Retrieve ESG data as of a specific date for given entities.

        Fetches ESG data by asset or issuer from multiple vendors (e.g. MSCI,
        SUST, ISS, REFINITIV, CLARITY_AI), returning the data in a unified schema.

        Args:
            ids: List of entity identifiers (asset IDs or issuer IDs).
            id_type: Type of the IDs being passed. One of:
                     ID_TYPE_UNSPECIFIED, ID_TYPE_ALADDIN_ISSUER, ID_TYPE_ASSET_ID.
            as_of_date: The date for which to retrieve ESG data (e.g. "2024-01-15").
            provider_measures: List of provider/measure specs. Each dict must have:
                               providerId (str, e.g. "MSCI") and measures (list[str],
                               e.g. ["ESG_IA_SCORE", "ESG_FINAL_RATING"]).
            issuer_traversal: Whether parent issuer traversal should be done (ALPHA feature).
            ignore_default_issuer_traversal: Whether to ignore default issuer traversal.
            page_size: Maximum number of results per page.
            page_token: Token from a previous call for pagination.
        """
        body: dict[str, Any] = {
            "ids": ids,
            "idType": id_type,
            "asOfDate": as_of_date,
            "providerMeasures": provider_measures,
        }
        if issuer_traversal is not None:
            body["issuerTraversal"] = issuer_traversal
        if ignore_default_issuer_traversal is not None:
            body["ignoreDefaultIssuerTraversal"] = ignore_default_issuer_traversal
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_esg_data_api("/data:retrieve", http_method="post", request_body=body)

    @mcp.tool()
    def retrieve_esg_metadata(
        provider_id: str,
        provider_category: str | None = None,
        measures: list[str] | None = None,
    ) -> str:
        """Retrieve ESG metadata (measure definitions) for a given provider.

        Returns metadata on ESG data measures by selecting a provider, optional
        provider category, and optional unique measure names.

        Args:
            provider_id: The ESG data provider ID (e.g. "MSCI", "SUST", "ISS",
                         "REFINITIV", "CLARITY_AI").
            provider_category: Optional category to filter measures by.
            measures: Optional list of specific measure names to retrieve metadata for.
        """
        params: dict[str, Any] = {"providerId": provider_id}
        if provider_category is not None:
            params["providerCategory"] = provider_category
        if measures is not None:
            params["measures"] = measures

        return _call_esg_data_api("/metadata:retrieve", http_method="get", params=params)

    @mcp.tool()
    def retrieve_esg_data_time_series(
        ids: list[str],
        id_type: str,
        from_date: str,
        to_date: str,
        provider_id: str,
        measures: list[str],
        rollup_flag: bool | None = None,
        period: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Retrieve time series ESG data for given entities over a date range.

        Returns ESG data points across a time range, optionally split by reporting
        frequency. Note: this API is in ALPHA and may change at any time.

        Args:
            ids: List of entity identifiers (asset IDs or issuer IDs).
            id_type: Type of the IDs being passed. One of:
                     ID_TYPE_UNSPECIFIED, ID_TYPE_ALADDIN_ISSUER, ID_TYPE_ASSET_ID.
            from_date: Start date of the time range (e.g. "2023-01-01").
            to_date: End date of the time range (e.g. "2024-01-01").
            provider_id: The ESG data provider ID (e.g. "MSCI").
            measures: List of measure names to retrieve (e.g. ["ESG_IA_SCORE"]).
            rollup_flag: Whether to roll up data.
            period: Reporting frequency for splitting the data. One of:
                    REPORT_FREQUENCY_UNSPECIFIED, REPORT_FREQUENCY_WEEKLY,
                    REPORT_FREQUENCY_MONTHLY, REPORT_FREQUENCY_QUARTERLY,
                    REPORT_FREQUENCY_ANNUALLY.
            page_size: Maximum number of results per page.
            page_token: Token from a previous call for pagination.
        """
        body: dict[str, Any] = {
            "ids": ids,
            "idType": id_type,
            "fromDate": from_date,
            "toDate": to_date,
            "providerId": provider_id,
            "measures": measures,
        }
        if rollup_flag is not None:
            body["rollupFlag"] = rollup_flag
        if period is not None:
            body["period"] = period
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_esg_data_api("/timeseriesdata:retrieve", http_method="post", request_body=body)
