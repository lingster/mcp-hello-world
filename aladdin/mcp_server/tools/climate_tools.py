"""MCP tools for the Aladdin Climate Data API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_CLIMATE_BASE_PATH = "/api/analytics/data/climate/v1/"

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


def _call_climate_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Climate API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_CLIMATE_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Climate API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_climate_tools(mcp: FastMCP) -> None:
    """Register Aladdin Climate API tools with the MCP server."""

    @mcp.tool()
    def retrieve_climate_data(
        id_type: str,
        ids: list[str],
        as_of_date: str,
        climate_risk_requests: list[dict[str, Any]],
        page_size: int | None = None,
        page_token: str | None = None,
        app_key: str | None = None,
    ) -> str:
        """Retrieve climate data for a given date.

        Fetches physical, transition, and temperature alignment analytics
        for selected entity types by specifying the desired datapoints,
        climate risk type, and scenario.

        Args:
            id_type: Type of entity identifiers. One of:
                     ID_TYPE_SECURITY, ID_TYPE_DEAL, ID_TYPE_LOAN,
                     ID_TYPE_PROPERTY, ID_TYPE_ISSUER, ID_TYPE_SECTOR,
                     ID_TYPE_MACRO.
            ids: Entity identifiers such as CUSIPs, Issuer IDs, etc.
                 Example: ['S60180858', 'R53975'].
            as_of_date: Date for which data is requested (YYYY-MM-DD).
                        Example: '2022-08-17'.
            climate_risk_requests: List of climate risk request dicts. Each dict can have:
                metricType (str): Climate risk type. One of METRIC_TYPE_PHYSICAL,
                    METRIC_TYPE_TRANSITION, METRIC_TYPE_TEMP_ALIGNMENT,
                    METRIC_TYPE_COMBINED_CLIMATE.
                metricCodes (list[str], required): Datapoint codes to fetch.
                    Example: ['PR_DAYS_OVER_90F', 'TR_CAPACITY_MACRO_WIND_PROJ_MWH'].
                climateScenarios (list[dict]): Scenario combinations. Each dict can have:
                    name (str, required): Scenario name, e.g. 'RCP 4.5', 'RCP 8.5',
                        '2 Degree'.
                    percentile (str): Percentile impact, e.g. 'mean' or '0.83'.
                        Only applicable to physical risk.
                    timeframe (str): Timeframe for data, e.g. 'Today', '2030', '2040'.
            page_size: Maximum number of ids per response page. Defaults to
                       server maximum if unspecified.
            page_token: Page token from a previous call for pagination.
            app_key: Optional application identifier key.
        """
        body: dict[str, Any] = {
            "idType": id_type,
            "ids": ids,
            "asOfDate": as_of_date,
            "climateRiskRequests": climate_risk_requests,
        }
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token
        if app_key is not None:
            body["appKey"] = app_key

        return _call_climate_api("/data:retrieve", http_method="post", request_body=body)

    @mcp.tool()
    def retrieve_climate_metadata(
        metric_type: str,
        metric_codes: list[str] | None = None,
    ) -> str:
        """Retrieve climate metadata describing available datapoints.

        Returns metadata about available datapoints across physical,
        transition, and temperature alignment analytics.

        Args:
            metric_type: The type of climate risk to retrieve metadata for.
                         One of: METRIC_TYPE_PHYSICAL, METRIC_TYPE_TRANSITION,
                         METRIC_TYPE_TEMP_ALIGNMENT, METRIC_TYPE_COMBINED_CLIMATE.
            metric_codes: Optional list of specific metric codes to filter by.
                          If omitted, metadata for all codes of the given type
                          is returned.
        """
        params: dict[str, Any] = {"metricType": metric_type}
        if metric_codes is not None:
            params["metricCodes"] = metric_codes

        return _call_climate_api("/metadata:retrieve", http_method="get", params=params)
