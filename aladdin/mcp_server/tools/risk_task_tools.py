"""MCP tools for the Aladdin Risk Task API (Risk Governance - Tasks)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_RISK_TASK_BASE_PATH = "/api/analytics/oversight/governance/v1/"

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


def _call_risk_task_api(
    endpoint_path: str,
    http_method: str = "get",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Risk Task API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_RISK_TASK_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Risk Task API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_risk_task_tools(mcp: FastMCP) -> None:
    """Register Aladdin Risk Task API tools with the MCP server."""

    @mcp.tool()
    def list_risk_tasks(
        workflow_states: list[str] | None = None,
        workflow_begin_range_time: str | None = None,
        workflow_end_range_time: str | None = None,
    ) -> str:
        """Retrieve a list of risk tasks from Risk Radar.

        Tasks are aggregates comprising related Exceptions, Rules, and Workflow
        items. Results can be filtered by workflow state and date range.

        If workflow_states is not provided, only tasks with non-terminal
        workflow states are returned. If terminal states are provided without
        a begin range time, results are restricted to a 45-day lookback.

        Args:
            workflow_states: List of workflow state strings to filter tasks by.
            workflow_begin_range_time: ISO 8601 datetime string for the start
                of the workflow date range filter.
            workflow_end_range_time: ISO 8601 datetime string for the end of
                the workflow date range filter.
        """
        params: dict[str, Any] = {}
        if workflow_states is not None:
            params["workflowStates"] = workflow_states
        if workflow_begin_range_time is not None:
            params["workflowBeginRangeTime"] = workflow_begin_range_time
        if workflow_end_range_time is not None:
            params["workflowEndRangeTime"] = workflow_end_range_time

        return _call_risk_task_api("/tasks", http_method="get", params=params)
