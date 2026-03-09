"""MCP tools for the Aladdin Portfolio Group API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_PORTFOLIO_GROUP_BASE_PATH = "/api/portfolio/configuration/portfolio-group/v1/"

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
    http_method: str = "get",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Portfolio Group API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_PORTFOLIO_GROUP_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Portfolio Group API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_portfolio_group_tools(mcp: FastMCP) -> None:
    """Register Aladdin Portfolio Group API tools with the MCP server."""

    @mcp.tool()
    def is_child_of(child_ticker: str, parent_ticker: str) -> str:
        """Determine if a portfolio/group is a direct child inside a parent group.

        Args:
            child_ticker: The ticker of the potential child portfolio/group.
            parent_ticker: The ticker of the parent group.
        """
        return _call_api(
            f"/portfolioGroups/{child_ticker}/isChildOf/{parent_ticker}",
            http_method="get",
        )

    @mcp.tool()
    def is_descendant_of(child_ticker: str, parent_ticker: str) -> str:
        """Determine if a portfolio/group is a descendant of a parent group.

        Args:
            child_ticker: The ticker of the potential descendant portfolio/group.
            parent_ticker: The ticker of the ancestor group.
        """
        return _call_api(
            f"/portfolioGroups/{child_ticker}/isDescendantOf/{parent_ticker}",
            http_method="get",
        )

    @mcp.tool()
    def get_portfolio_group_ancestors(id: str) -> str:
        """Get the ancestor groups (parents, grand-parents, etc.) of a portfolio/group.

        Args:
            id: The portfolio group ticker.
        """
        return _call_api(
            f"/portfolioGroups/{id}/ancestors",
            http_method="get",
        )

    @mcp.tool()
    def get_portfolio_group_members(id: str) -> str:
        """Get the members (sub-groups and portfolios) inside a portfolio group.

        Args:
            id: The portfolio group ticker.
        """
        return _call_api(
            f"/portfolioGroups/{id}/members",
            http_method="get",
        )

    @mcp.tool()
    def get_portfolio_group_node(id: str) -> str:
        """Get the data of a single portfolio group node (parent and child code lists).

        Args:
            id: The portfolio group ticker.
        """
        return _call_api(
            f"/portfolioGroups/{id}/node",
            http_method="get",
        )

    @mcp.tool()
    def get_portfolio_group_parents(id: str) -> str:
        """Get the direct parent groups of a portfolio/group.

        Args:
            id: The portfolio group ticker.
        """
        return _call_api(
            f"/portfolioGroups/{id}/parents",
            http_method="get",
        )

    @mcp.tool()
    def is_ancestor_of(parent_ticker: str, child_ticker: str) -> str:
        """Determine if a group is an ancestor of a specified portfolio/group.

        Args:
            parent_ticker: The ticker of the potential ancestor group.
            child_ticker: The ticker of the potential descendant portfolio/group.
        """
        return _call_api(
            f"/portfolioGroups/{parent_ticker}/isAncestorOf/{child_ticker}",
            http_method="get",
        )

    @mcp.tool()
    def is_parent_of(parent_ticker: str, child_ticker: str) -> str:
        """Determine if a group is a direct parent of a specified portfolio/group.

        Args:
            parent_ticker: The ticker of the potential parent group.
            child_ticker: The ticker of the potential child portfolio/group.
        """
        return _call_api(
            f"/portfolioGroups/{parent_ticker}/isParentOf/{child_ticker}",
            http_method="get",
        )

    @mcp.tool()
    def remove_portfolio_group(portfolio_id: int) -> str:
        """Delete an empty portfolio group.

        Permissions: PortGroupMOD, asPortMOD (for non-GP groups), GPMaint (for GP groups).

        Args:
            portfolio_id: The portfolio code of the group to delete.
        """
        return _call_api(
            f"/portfolioGroups/{portfolio_id}",
            http_method="delete",
        )

    @mcp.tool()
    def add_portfolio_group_children(
        relationships: list[dict[str, str]],
    ) -> str:
        """Add new child groups or portfolios to specified parent groups.

        Permissions: PortGroupMOD, asPortMOD (for non-GP groups), GPMaint (for GP groups).

        Args:
            relationships: List of parent-child relationships to add. Each dict should have:
                           parentTicker (str) and childTicker (str).
        """
        body: dict[str, Any] = {"relationships": relationships}
        return _call_api(
            "/portfolioGroups:addChildren",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def delete_portfolio_group_children(
        relationships: list[dict[str, str]],
    ) -> str:
        """Delete existing child groups or portfolios from specified parent groups.

        Permissions: PortGroupMOD, asPortMOD (for non-GP groups), GPMaint (for GP groups).

        Args:
            relationships: List of parent-child relationships to remove. Each dict should have:
                           parentTicker (str) and childTicker (str).
        """
        body: dict[str, Any] = {"relationships": relationships}
        return _call_api(
            "/portfolioGroups:deleteChildren",
            http_method="post",
            request_body=body,
        )
