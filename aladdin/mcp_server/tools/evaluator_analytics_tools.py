"""MCP tools for the Aladdin Evaluator Analytics API (Risk Governance - Rule Evaluation)."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_EVALUATOR_ANALYTICS_BASE_PATH = "/api/analytics/oversight/governance/v1/"

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
    """Helper to call an Evaluator Analytics API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_EVALUATOR_ANALYTICS_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Evaluator Analytics API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_evaluator_analytics_tools(mcp: FastMCP) -> None:
    """Register Aladdin Evaluator Analytics API tools with the MCP server."""

    @mcp.tool()
    def get_longrunning_operation(operation_id: str) -> str:
        """Get the latest state of a long-running operation from triggering the evaluator.

        Args:
            operation_id: The unique ID of the long-running operation.
        """
        return _call_api(
            f"/evaluator/longrunningoperations/{operation_id}",
            http_method="get",
        )

    @mcp.tool()
    def evaluate_portfolio(
        portfolio_id: str,
        as_of_date: str,
        benchmark_type: str | None = None,
        benchmark_order: str | None = None,
        benchmark_ticker: str | None = None,
    ) -> str:
        """Trigger rule evaluation for a specified portfolio and date against all rules.

        Args:
            portfolio_id: Unique identifier of the portfolio to evaluate.
            as_of_date: The date for the evaluation in YYYY-MM-DD format.
            benchmark_type: Benchmark type (e.g. RISK, PERFORMANCE, FORWARD, OTHER, NONE).
            benchmark_order: Which benchmark to use
                (PORTFOLIO_ANALYTICS_BENCHMARK_ORDER_UNSPECIFIED |
                 PORTFOLIO_ANALYTICS_BENCHMARK_ORDER_PRIMARY |
                 PORTFOLIO_ANALYTICS_BENCHMARK_ORDER_SECONDARY).
            benchmark_ticker: Benchmark ticker. Only needed when benchmark_type is OTHER.
        """
        body: dict[str, Any] = {
            "portfolioId": portfolio_id,
            "asOfDate": as_of_date,
        }
        benchmark_config: dict[str, Any] = {}
        if benchmark_type is not None:
            benchmark_config["benchmarkType"] = benchmark_type
        if benchmark_order is not None:
            benchmark_config["benchmarkOrder"] = benchmark_order
        if benchmark_ticker is not None:
            benchmark_config["benchmarkTicker"] = benchmark_ticker
        if benchmark_config:
            body["benchmarkConfig"] = benchmark_config

        return _call_api("/portfolio:evaluate", http_method="post", request_body=body)

    @mcp.tool()
    def evaluate_portfolio_rule(
        portfolio_id: str,
        as_of_date: str,
        rule_id: str,
    ) -> str:
        """Trigger rule evaluation for a specified portfolio and date against a specific rule.

        Args:
            portfolio_id: Unique identifier of the portfolio to evaluate.
            as_of_date: The date for the evaluation in YYYY-MM-DD format.
            rule_id: Unique identifier of the rule to evaluate.
        """
        body: dict[str, Any] = {
            "portfolioId": portfolio_id,
            "asOfDate": as_of_date,
            "ruleId": rule_id,
        }
        return _call_api("/portfolio:evaluateRule", http_method="post", request_body=body)

    @mcp.tool()
    def list_rule_evaluations(
        filter: str | None = None,
        page_token: str | None = None,
        page_size: int | None = None,
        order_by: str | None = None,
        facet_fields: list[str] | None = None,
        as_of_date: str | None = None,
        start_eval_time: str | None = None,
        end_eval_time: str | None = None,
    ) -> str:
        """Retrieve rule evaluations matching the parameters provided.

        Args:
            filter: AIP-160 filter string for filtering results.
            page_token: Offset token for pagination into the result set.
            page_size: Number of entries to return (max 100, default 5).
            order_by: Ordering of returned entries by evaluationTime
                (e.g. 'evaluationTime:asc' or 'evaluationTime:desc').
            facet_fields: List of fields to use for facet search
                (response includes term counts for each field).
            as_of_date: Retrieve evaluations matching this as-of date (YYYY-MM-DD).
            start_eval_time: Retrieve evaluations with evaluationTime >= this datetime (RFC 3339).
            end_eval_time: Retrieve evaluations with evaluationTime <= this datetime (RFC 3339).
        """
        params: dict[str, Any] = {}
        if filter is not None:
            params["filter"] = filter
        if page_token is not None:
            params["pageToken"] = page_token
        if page_size is not None:
            params["pageSize"] = page_size
        if order_by is not None:
            params["orderBy"] = order_by
        if facet_fields is not None:
            params["facetFields"] = facet_fields
        if as_of_date is not None:
            params["asOfDate"] = as_of_date
        if start_eval_time is not None:
            params["startEvalTime"] = start_eval_time
        if end_eval_time is not None:
            params["endEvalTime"] = end_eval_time

        return _call_api("/ruleEvaluations", http_method="get", params=params)
