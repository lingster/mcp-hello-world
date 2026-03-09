"""MCP tools for the Aladdin Risk Custom Evaluation Metric API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_RISK_CUSTOM_EVAL_METRIC_BASE_PATH = "/api/analytics/oversight/governance/v1/"

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
    """Helper to call a Risk Custom Evaluation Metric API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_RISK_CUSTOM_EVAL_METRIC_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Risk Custom Evaluation Metric API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_risk_custom_evaluation_metric_tools(mcp: FastMCP) -> None:
    """Register Aladdin Risk Custom Evaluation Metric API tools with the MCP server."""

    @mcp.tool()
    def list_risk_custom_evaluation_metrics(
        report_time: str | None = None,
        begin_range_date: str | None = None,
        end_range_date: str | None = None,
        read_mask: str | None = None,
        page_token: str | None = None,
        page_size: int | None = None,
        filter: str | None = None,
        order_by: str | None = None,
    ) -> str:
        """List custom evaluation metrics used for rule evaluation in Risk Radar.

        Args:
            report_time: The report time for filtering metrics.
            begin_range_date: The beginning of the date range filter.
            end_range_date: The end of the date range filter.
            read_mask: Comma-separated list of fields to return.
            page_token: Token for retrieving the next page of results.
            page_size: Maximum number of results to return per page.
            filter: Filter expression for narrowing results.
            order_by: Sort order string for the results.
        """
        params: dict[str, Any] = {}
        if report_time is not None:
            params["reportTime"] = report_time
        if begin_range_date is not None:
            params["beginRangeDate"] = begin_range_date
        if end_range_date is not None:
            params["endRangeDate"] = end_range_date
        if read_mask is not None:
            params["readMask"] = read_mask
        if page_token is not None:
            params["pageToken"] = page_token
        if page_size is not None:
            params["pageSize"] = page_size
        if filter is not None:
            params["filter"] = filter
        if order_by is not None:
            params["orderBy"] = order_by

        return _call_api(
            "/customEvaluationMetric",
            http_method="get",
            params=params if params else None,
        )

    @mcp.tool()
    def get_risk_custom_evaluation_metric_long_running_operation(
        id: str,
    ) -> str:
        """Get the latest state of a long-running operation for risk custom evaluation metrics.

        Args:
            id: The server-assigned ID of the long-running operation.
        """
        return _call_api(
            f"/customEvaluationMetric/longrunningoperations/{id}",
            http_method="get",
        )

    @mcp.tool()
    def batch_query_risk_custom_evaluation_metrics(
        requests: list[dict[str, Any]],
    ) -> str:
        """Bulk query custom evaluation metrics used for rule evaluation in Risk Radar.

        Args:
            requests: List of query request dicts. Each dict can have:
                      scopeId (str), scopeType (str), entityId (str),
                      entityType (str), metric (str),
                      asOfDate (str - effective date for the record).
        """
        body: dict[str, Any] = {"requests": requests}
        return _call_api(
            "/customEvaluationMetric:batchQuery",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def upload_risk_custom_evaluation_metrics(
        requests: list[dict[str, Any]],
    ) -> str:
        """Bulk upload custom evaluation metrics to create or update existing metrics in Risk Radar.

        Args:
            requests: List of create/update request dicts. Each dict can have:
                      asOfDate (str), riskCustomEvaluationMetric (dict with fields:
                      id, validBeginDate, validEndDate, entryTime, expiryTime,
                      modifier, scopeId, scopeType, scope, entityId, entityType,
                      entity, metricCategory, metric,
                      riskMetricValue (dict with metricValueInteger (str) and/or
                      metricValueDouble (float))).
        """
        body: dict[str, Any] = {"requests": requests}
        return _call_api(
            "/customEvaluationMetric:uploadCustomEvaluationMetrics",
            http_method="post",
            request_body=body,
        )
