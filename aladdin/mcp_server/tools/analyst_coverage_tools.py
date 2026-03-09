"""MCP tools for the Aladdin Analyst Coverage API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_BASE_PATH = "/api/investment-research/analyst/coverage/v1/"

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
    """Helper to call an Analyst Coverage API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Analyst Coverage API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def _build_entity_id(entity_id: dict[str, Any]) -> dict[str, Any]:
    """Normalize an entity ID dict, filtering out None values."""
    cleaned: dict[str, Any] = {}
    for key in ("issuer", "assetId", "investmentStrategyId"):
        if entity_id.get(key):
            cleaned[key] = entity_id[key]
    return cleaned


def _build_coverage_dict(coverage: dict[str, Any]) -> dict[str, Any]:
    """Normalize a coverage dict, filtering out None values."""
    cleaned: dict[str, Any] = {}
    for key in ("id", "analystId", "analystRole", "creator", "startTime", "modifier", "endTime", "action"):
        if coverage.get(key):
            cleaned[key] = coverage[key]
    if coverage.get("entityId"):
        cleaned["entityId"] = _build_entity_id(coverage["entityId"])
    return cleaned


def register_analyst_coverage_tools(mcp: FastMCP) -> None:
    """Register Aladdin Analyst Coverage API tools with the MCP server."""

    @mcp.tool()
    def create_analyst_coverage(
        analyst_id: str,
        analyst_role: str,
        issuer: str | None = None,
        asset_id: str | None = None,
        investment_strategy_id: str | None = None,
        action: str = "COVERAGE_ACTION_TYPE_ADD",
    ) -> str:
        """Assign analyst coverage to an entity.

        Args:
            analyst_id: The user ID of the analyst.
            analyst_role: Role of the research analyst (e.g. "Primary Credit Analyst",
                          "Primary Equity Analyst", "Secondary Equity Analyst").
            issuer: The issuer identifier for the entity. Provide one of issuer,
                    asset_id, or investment_strategy_id.
            asset_id: The asset ID for a security.
            investment_strategy_id: The investment strategy ID.
            action: Coverage action type. One of COVERAGE_ACTION_TYPE_UNSPECIFIED,
                    COVERAGE_ACTION_TYPE_ADD, COVERAGE_ACTION_TYPE_TRANSFER,
                    COVERAGE_ACTION_TYPE_REMOVE.
        """
        entity_id: dict[str, Any] = {}
        if issuer:
            entity_id["issuer"] = issuer
        if asset_id:
            entity_id["assetId"] = asset_id
        if investment_strategy_id:
            entity_id["investmentStrategyId"] = investment_strategy_id

        body: dict[str, Any] = {
            "analystId": analyst_id,
            "analystRole": analyst_role,
            "action": action,
        }
        if entity_id:
            body["entityId"] = entity_id

        return _call_api("/coverages", http_method="post", request_body=body)

    @mcp.tool()
    def get_analyst_coverage(coverage_id: str) -> str:
        """Retrieve analyst coverage assignment by its coverage ID.

        Args:
            coverage_id: The unique ID of the coverage assignment to retrieve.
        """
        return _call_api(
            f"/coverages/{coverage_id}",
            http_method="get",
        )

    @mcp.tool()
    def delete_analyst_coverage(coverage_id: str) -> str:
        """Delete an analyst coverage assignment by its coverage ID.

        Args:
            coverage_id: The unique ID of the coverage assignment to delete.
        """
        return _call_api(
            f"/coverages/{coverage_id}",
            http_method="delete",
        )

    @mcp.tool()
    def batch_create_analyst_coverages(
        requests: list[dict[str, Any]],
    ) -> str:
        """Assign analyst coverage assignments in batch.

        Args:
            requests: List of coverage creation requests. Each dict should contain
                      an "analystCoverage" key with a coverage object having fields:
                      analystId (str), analystRole (str),
                      entityId (dict with issuer/assetId/investmentStrategyId),
                      action (str, e.g. COVERAGE_ACTION_TYPE_ADD).
        """
        cleaned_requests: list[dict[str, Any]] = []
        for req in requests:
            entry: dict[str, Any] = {}
            if req.get("analystCoverage"):
                entry["analystCoverage"] = _build_coverage_dict(req["analystCoverage"])
            cleaned_requests.append(entry)

        body: dict[str, Any] = {"requests": cleaned_requests}
        return _call_api("/coverages:batchCreate", http_method="post", request_body=body)

    @mcp.tool()
    def batch_delete_analyst_coverages(
        analyst_coverages: list[dict[str, Any]],
    ) -> str:
        """Delete analyst coverage assignments in batch.

        Args:
            analyst_coverages: List of coverage objects to delete. Each dict can have:
                               id (str), analystId (str), analystRole (str),
                               entityId (dict with issuer/assetId/investmentStrategyId).
        """
        body: dict[str, Any] = {
            "analystCoverages": [_build_coverage_dict(c) for c in analyst_coverages],
        }
        return _call_api("/coverages:batchDelete", http_method="post", request_body=body)

    @mcp.tool()
    def batch_transfer_analyst_coverages(
        analyst_coverages: list[dict[str, Any]],
        analyst_id: str,
        analyst_role: str,
    ) -> str:
        """Transfer analyst coverage assignments in batch to a new analyst.

        Args:
            analyst_coverages: List of coverage objects to transfer. Each dict can have:
                               id (str), analystId (str), analystRole (str),
                               entityId (dict with issuer/assetId/investmentStrategyId).
            analyst_id: The user ID of the analyst to transfer coverage to.
            analyst_role: The role to assign for the new analyst (e.g. "Primary Credit Analyst").
        """
        body: dict[str, Any] = {
            "analystCoverages": [_build_coverage_dict(c) for c in analyst_coverages],
            "analystId": analyst_id,
            "analystRole": analyst_role,
        }
        return _call_api("/coverages:batchTransfer", http_method="patch", request_body=body)

    @mcp.tool()
    def search_active_analyst_coverages(
        filter_criteria: list[str] | None = None,
        order_by: str | None = None,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> str:
        """Search active analyst coverage assignments by specified criteria.

        Filter syntax uses Solr query format: [target field]:[term]
        e.g. analystId:"rbajarol"

        Args:
            filter_criteria: List of filter strings (e.g. ['analystId:"jsmith"']).
            order_by: Sort order string (e.g. "modified_time desc, analystId").
            page_size: Max number of coverages to return (default 10).
            page_number: Page number for pagination.
        """
        body: dict[str, Any] = {}
        if filter_criteria:
            body["filterCriteria"] = filter_criteria
        if order_by is not None:
            body["orderBy"] = order_by
        if page_size is not None:
            body["pageSize"] = page_size
        if page_number is not None:
            body["pageNumber"] = page_number

        return _call_api("/coverages:searchActive", http_method="post", request_body=body)

    @mcp.tool()
    def search_historical_analyst_coverages(
        filter_criteria: list[str] | None = None,
        order_by: str | None = None,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> str:
        """Retrieve historical analyst coverage assignments by specified criteria.

        Filter syntax uses Solr query format: [target field]:[term]
        e.g. analystId:"rbajarol"

        Args:
            filter_criteria: List of filter strings (e.g. ['analystId:"jsmith"']).
            order_by: Sort order string (e.g. "modified_time desc, analystId").
            page_size: Max number of coverages to return (default 10).
            page_number: Page number for pagination.
        """
        body: dict[str, Any] = {}
        if filter_criteria:
            body["filterCriteria"] = filter_criteria
        if order_by is not None:
            body["orderBy"] = order_by
        if page_size is not None:
            body["pageSize"] = page_size
        if page_number is not None:
            body["pageNumber"] = page_number

        return _call_api("/coverages:searchHistorical", http_method="post", request_body=body)

    @mcp.tool()
    def transfer_analyst_coverage(
        analyst_id: str,
        analyst_role: str,
        analyst_coverage: dict[str, Any] | None = None,
    ) -> str:
        """Transfer a single analyst coverage assignment to a new analyst.

        Args:
            analyst_id: The user ID of the analyst to transfer coverage to.
            analyst_role: The role to assign for the new analyst
                          (e.g. "Primary Credit Analyst").
            analyst_coverage: The coverage entry to transfer. Dict can have:
                              id (str), analystId (str), analystRole (str),
                              entityId (dict with issuer/assetId/investmentStrategyId).
        """
        body: dict[str, Any] = {
            "analystId": analyst_id,
            "analystRole": analyst_role,
        }
        if analyst_coverage:
            body["analystCoverage"] = _build_coverage_dict(analyst_coverage)

        return _call_api("/coverages:transfer", http_method="patch", request_body=body)
