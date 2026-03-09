"""MCP tools for the Aladdin Compliance Rule API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_COMPLIANCE_RULE_BASE_PATH = "/api/compliance/state/compliance-rule/v1/"

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


def _call_compliance_rule_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Compliance Rule API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_COMPLIANCE_RULE_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Compliance Rule API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_compliance_rule_tools(mcp: FastMCP) -> None:
    """Register Aladdin Compliance Rule API tools with the MCP server."""

    @mcp.tool()
    def filter_compliance_rules(
        rule_names: list[str] | None = None,
        page_token: str | None = None,
        page_size: int | None = None,
    ) -> str:
        """Filter compliance rules by rule names.

        Compliance Rules are used to automatically monitor whether a fund
        adheres to a regulation, client mandate, or internal guideline.

        Each returned rule includes metadata such as id, description, category,
        rule usage, coding note, jurisdiction country code, regulation,
        compliance deadline, labels, documentation, rule type details
        (prohibition, concentration, value-at-risk, disclosure, scripted,
        look-through-definition, information, trade, counterparty,
        counterparty-exposure-limit), state, modify time, and modifier.

        Args:
            rule_names: List of rule names to filter by (max 2000, recommended up to 500).
                        If not provided, returns all rules.
            page_token: A page token from a previous call to retrieve the next page.
            page_size: Maximum number of rules to return (default 100, max 100).
        """
        body: dict[str, Any] = {}

        if rule_names is not None:
            body["query"] = {"ruleNames": rule_names}
        if page_token is not None:
            body["pageToken"] = page_token
        if page_size is not None:
            body["pageSize"] = page_size

        return _call_compliance_rule_api(
            "/complianceRules:filter",
            http_method="post",
            request_body=body,
        )
