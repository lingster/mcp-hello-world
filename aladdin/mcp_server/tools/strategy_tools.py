"""MCP tools for the Aladdin Strategy API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_STRATEGY_BASE_PATH = "/api/portfolio-management/target/strategy/v1/"

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


def _call_strategy_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Strategy API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_STRATEGY_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Strategy API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_strategy_tools(mcp: FastMCP) -> None:
    """Register Aladdin Strategy API tools with the MCP server."""

    @mcp.tool()
    def create_strategy(
        strategy_name: str,
        strategy_description: str = "",
        expire_date: str | None = None,
        start_date: str | None = None,
    ) -> str:
        """Create a new trade strategy in Aladdin.

        Args:
            strategy_name: The name of the strategy. If the strategy has a parent,
                           it must be prefixed and separated by a colon (e.g. "Parent:Child").
            strategy_description: A description of the strategy.
            expire_date: The expiration date (YYYY-MM-DD). Defaults to 2222-12-31 if omitted.
            start_date: The start date of the strategy (YYYY-MM-DD).
        """
        body: dict[str, Any] = {
            "strategyName": strategy_name,
        }
        if strategy_description:
            body["strategyDescription"] = strategy_description
        if expire_date is not None:
            body["expireDate"] = expire_date
        if start_date is not None:
            body["startDate"] = start_date

        return _call_strategy_api("/strategies", http_method="post", request_body=body)

    @mcp.tool()
    def get_strategy(strategy_id: str) -> str:
        """Retrieve a strategy by its ID. Returns expired strategies as well.

        Args:
            strategy_id: The numeric ID of the strategy to retrieve.
        """
        return _call_strategy_api(
            f"/strategies/{strategy_id}",
            http_method="get",
        )

    @mcp.tool()
    def delete_strategy(strategy_id: str) -> str:
        """Delete a strategy (soft delete).

        Sets the expire date to today's date in Aladdin Server Timezone.

        Args:
            strategy_id: The numeric ID of the strategy to delete.
        """
        return _call_strategy_api(
            f"/strategies/{strategy_id}",
            http_method="delete",
        )

    @mcp.tool()
    def batch_create_strategies(
        strategies: list[dict[str, Any]],
    ) -> str:
        """Create multiple new strategies in a single request.

        Args:
            strategies: List of strategy dicts to create. Each dict can have:
                        strategyName (str, required), strategyDescription (str),
                        expireDate (str, YYYY-MM-DD), startDate (str, YYYY-MM-DD).
        """
        requests: list[dict[str, Any]] = []
        for s in strategies:
            entry: dict[str, Any] = {}
            if s.get("strategyName"):
                entry["strategyName"] = s["strategyName"]
            if s.get("strategyDescription"):
                entry["strategyDescription"] = s["strategyDescription"]
            if s.get("expireDate"):
                entry["expireDate"] = s["expireDate"]
            if s.get("startDate"):
                entry["startDate"] = s["startDate"]
            requests.append(entry)

        body: dict[str, Any] = {"requests": requests}
        return _call_strategy_api("/strategies:batchCreate", http_method="post", request_body=body)

    @mcp.tool()
    def batch_delete_strategies(
        strategy_ids: list[str],
    ) -> str:
        """Delete multiple strategies in a single request (soft delete).

        Sets the expire date of each strategy to today's date in Aladdin Server Timezone.

        Args:
            strategy_ids: List of strategy IDs to delete.
        """
        body: dict[str, Any] = {"ids": strategy_ids}
        return _call_strategy_api("/strategies:batchDelete", http_method="post", request_body=body)

    @mcp.tool()
    def batch_update_strategies(
        requests: list[dict[str, Any]],
    ) -> str:
        """Update multiple strategies in a single request.

        Args:
            requests: List of update request dicts. Each dict should have:
                      strategy (dict with id, strategyName, strategyDescription, expireDate, startDate),
                      updateMask (str, comma-separated list of fields to update,
                                  e.g. "strategyDescription,expireDate").
        """
        body: dict[str, Any] = {"requests": requests}
        return _call_strategy_api("/strategies:batchUpdate", http_method="post", request_body=body)

    @mcp.tool()
    def filter_strategies(
        strategy_names: list[str] | None = None,
        expire_date: str | None = None,
        include_expired: bool | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter strategies based on query criteria.

        Returns all active strategies if no filtering criteria is provided.
        Active strategies are those with expire date null or >= today.

        Args:
            strategy_names: List of strategy names to filter by.
            expire_date: Filter strategies with expire date >= this value (YYYY-MM-DD).
            include_expired: Whether to include expired strategies in results.
            page_size: Maximum number of strategies to return (default server-side is typically 1000).
            page_token: Page token from a previous call for pagination.
        """
        body: dict[str, Any] = {}
        strategy_query: dict[str, Any] = {}

        if strategy_names is not None:
            strategy_query["strategyNames"] = strategy_names
        if expire_date is not None:
            strategy_query["expireDate"] = expire_date
        if include_expired is not None:
            strategy_query["includeExpired"] = include_expired

        if strategy_query:
            body["strategyQuery"] = strategy_query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_strategy_api("/strategies:filter", http_method="post", request_body=body)

    @mcp.tool()
    def filter_strategies_by_pattern(
        strategy_name_pattern: str,
        expire_date: str | None = None,
        include_expired: bool | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter strategies by pattern matching on strategy name.

        Uses "*" for wildcard searching. For example:
          - "Equity*" matches strategies starting with "Equity"
          - "*Growth*" matches strategies containing "Growth"

        Args:
            strategy_name_pattern: The pattern to match against strategy names.
                                   Use "*" as a wildcard character.
            expire_date: Filter strategies with expire date >= this value (YYYY-MM-DD).
            include_expired: Whether to include expired strategies in results.
            page_size: Maximum number of strategies to return.
            page_token: Page token from a previous call for pagination.
        """
        query: dict[str, Any] = {
            "strategyNamePattern": strategy_name_pattern,
        }
        if expire_date is not None:
            query["expireDate"] = expire_date
        if include_expired is not None:
            query["includeExpired"] = include_expired

        body: dict[str, Any] = {"query": query}
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_strategy_api("/strategies:filterByPattern", http_method="post", request_body=body)

    @mcp.tool()
    def undelete_strategy(strategy_id: str) -> str:
        """Undelete a previously deleted strategy.

        Reverses the expire date back to the default value of 2222-12-31.

        Args:
            strategy_id: The numeric ID of the strategy to undelete.
        """
        body: dict[str, Any] = {"id": strategy_id}
        return _call_strategy_api("/strategies:undelete", http_method="post", request_body=body)
