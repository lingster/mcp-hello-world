"""MCP tools for the Aladdin Corporate Action Entitlement API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_CORPORATE_ACTION_ENTITLEMENT_BASE_PATH = (
    "/api/investment-operations/asset-lifecycle/corporate-action/v1/"
)

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
    """Helper to call a Corporate Action Entitlement API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_CORPORATE_ACTION_ENTITLEMENT_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(
            f"Corporate Action Entitlement API call failed: "
            f"{http_method.upper()} {endpoint_path}: {e}"
        )
        return json.dumps({"error": str(e)})


def register_corporate_action_entitlement_tools(mcp: FastMCP) -> None:
    """Register Aladdin Corporate Action Entitlement API tools with the MCP server."""

    @mcp.tool()
    def cancel_corporate_action_elections(
        parent: str,
        corporate_action_id: str,
        entitlement_touch_count: int,
    ) -> str:
        """Cancel elections for a corporate action entitlement.

        Args:
            parent: The entitlement ID (parent resource).
            corporate_action_id: The corporate action ID.
            entitlement_touch_count: The entitlement touch count (version).
        """
        body: dict[str, Any] = {
            "corporateActionId": corporate_action_id,
            "entitlementTouchCount": entitlement_touch_count,
        }
        return _call_api(
            f"/corporateActionEntitlements/{parent}/corporateActionElection:cancel",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def elect_corporate_action_elections(
        elect_election_request_details: list[dict[str, Any]],
    ) -> str:
        """Elect elections for corporate action entitlements.

        Args:
            elect_election_request_details: List of election request details. Each dict should contain:
                - entitlementKey (dict): with entitlementId (str), corporateActionId (str),
                  and entitlementTouchCount (int) to uniquely identify the entitlement.
                - elections (list[dict]): elections to elect, each with fields such as
                  optionNumber (int), electedAmount (float), electionPercentage (float),
                  electionReason (str), etc.
                - overrideCompliance (bool, optional): whether to ignore compliance violations.
        """
        body: dict[str, Any] = {
            "electElectionRequestDetails": elect_election_request_details,
        }
        return _call_api(
            "/corporateActionEntitlements:electElections",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def filter_corporate_action_entitlements(
        ids: list[str] | None = None,
        corporate_action_ids: list[str] | None = None,
        portfolio_ids: list[str] | None = None,
        entitlement_types: list[str] | None = None,
        entitlement_load_flags: list[str] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter corporate action entitlements by various criteria.

        At least one query criterion (ids, corporate_action_ids, portfolio_ids, or
        entitlement_types) should be provided. corporate_action_ids is mandatory when
        using portfolio_ids or entitlement_types.

        Args:
            ids: Aladdin corporate action entitlement IDs (numeric values as strings).
            corporate_action_ids: Aladdin parent corporate action IDs (numeric values as strings).
            portfolio_ids: Portfolio IDs for the entitlements (numeric values as strings).
                           Works in conjunction with corporate_action_ids.
            entitlement_types: Corporate action entitlement types to filter by.
                               Works in conjunction with corporate_action_ids.
            entitlement_load_flags: Load flags controlling what data to include in the response.
            page_size: Maximum number of entitlements to return (max 250, default 250).
            page_token: Page token from a previous call to retrieve the next page.
        """
        query: dict[str, Any] = {}
        if ids is not None:
            query["ids"] = ids
        if corporate_action_ids is not None:
            query["corporateActionIds"] = corporate_action_ids
        if portfolio_ids is not None:
            query["portfolioIds"] = portfolio_ids
        if entitlement_types is not None:
            query["entitlementTypes"] = entitlement_types

        body: dict[str, Any] = {}
        if query:
            body["corporateActionEntitlementQuery"] = query
        if entitlement_load_flags is not None:
            body["entitlementLoadFlags"] = entitlement_load_flags
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api(
            "/corporateActionEntitlements:filter",
            http_method="post",
            request_body=body,
        )
