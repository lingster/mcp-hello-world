"""MCP tools for the Aladdin Compliance LevelAPI."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_LEVEL_BASE_PATH = "/api/compliance/state/level/v1/"

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


def _call_level_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a LevelAPI endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_LEVEL_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"LevelAPI call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_level_tools(mcp: FastMCP) -> None:
    """Register Aladdin Compliance LevelAPI tools with the MCP server."""

    @mcp.tool()
    def filter_level(
        portfolio_ticker: str,
        include_portfolio_group_result: bool | None = None,
        level_date: str | None = None,
        rule_assignment_ids: list[int] | None = None,
        rule_ids: list[int] | None = None,
        condition_state: bool | None = None,
        groups: list[str] | None = None,
        compliance_rule_state: str | None = None,
        as_traded: bool | None = None,
    ) -> str:
        """Find compliance levels based on filter criteria.

        Retrieves start-of-day and intraday compliance levels across
        portfolios and portfolio groups.

        Args:
            portfolio_ticker: A shorthand name which this portfolio was assigned
                in Aladdin. This is a mandatory field.
            include_portfolio_group_result: When True, results are limited to rules
                assigned directly to the portfolio or portfolio group provided,
                excluding rules assigned to underlying portfolios.
            level_date: Date parameter to retrieve historical data (YYYY-MM-DD).
                No supplied value will return the most recent data.
            rule_assignment_ids: Unique primary key identifiers of Aladdin rule
                assignments to filter by.
            rule_ids: IDs associated with the rules to filter by.
            condition_state: Filter by rule state. False if the rule is in
                violation, True otherwise.
            groups: Filter results to specific groups, e.g. ['USD', 'GBP', 'JPY'].
            compliance_rule_state: Filter by compliance rule state. One of:
                COMPLIANCE_RULE_STATE_UNSPECIFIED, COMPLIANCE_RULE_STATE_PASSED,
                COMPLIANCE_RULE_STATE_WARNING, COMPLIANCE_RULE_STATE_RESTRICTION.
            as_traded: When True, return levels for the as-traded view.
        """
        level_filter: dict[str, Any] = {
            "portfolioTicker": portfolio_ticker,
        }
        if include_portfolio_group_result is not None:
            level_filter["includePortfolioGroupResult"] = include_portfolio_group_result
        if level_date is not None:
            level_filter["levelDate"] = level_date
        if rule_assignment_ids is not None:
            level_filter["ruleAssignmentIds"] = rule_assignment_ids
        if rule_ids is not None:
            level_filter["ruleIds"] = rule_ids
        if condition_state is not None:
            level_filter["conditionState"] = condition_state
        if groups is not None:
            level_filter["groups"] = groups
        if compliance_rule_state is not None:
            level_filter["complianceRuleState"] = compliance_rule_state
        if as_traded is not None:
            level_filter["asTraded"] = as_traded

        body: dict[str, Any] = {
            "levelFilter": level_filter,
        }

        return _call_level_api(
            "/levels:filterLevel",
            http_method="post",
            request_body=body,
        )
