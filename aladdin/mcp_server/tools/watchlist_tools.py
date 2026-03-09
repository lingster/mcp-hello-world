"""MCP tools for the Aladdin Investment Watchlist API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_WATCHLIST_BASE_PATH = "/api/investment-research/surveillance/watchlist/v1/"

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


def _call_watchlist_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Watchlist API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_WATCHLIST_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Watchlist API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def _build_security_dicts(securities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize security dicts, filtering out None values."""
    cleaned: list[dict[str, Any]] = []
    for sec in securities:
        entry: dict[str, Any] = {}
        if sec.get("assetId"):
            entry["assetId"] = sec["assetId"]
        if sec.get("addedDate"):
            entry["addedDate"] = sec["addedDate"]
        if sec.get("expiryDate"):
            entry["expiryDate"] = sec["expiryDate"]
        if sec.get("preTradeNote"):
            entry["preTradeNote"] = sec["preTradeNote"]
        if sec.get("assetType"):
            entry["assetType"] = sec["assetType"]
        cleaned.append(entry)
    return cleaned


def register_watchlist_tools(mcp: FastMCP) -> None:
    """Register Aladdin Watchlist API tools with the MCP server."""

    @mcp.tool()
    def create_watchlist(
        title: str,
        owner_id: str,
        description: str = "",
        shareable: bool = False,
        column_tags: list[str] | None = None,
        securities: list[dict[str, Any]] | None = None,
    ) -> str:
        """Create a new investment watchlist.

        Args:
            title: The title of the watchlist.
            owner_id: The user ID who owns the watchlist.
            description: Description of the watchlist.
            shareable: Whether the watchlist can be shared with others.
            column_tags: List of column tags for the watchlist.
            securities: List of securities to add. Each dict can have:
                        assetId (str), addedDate (date str), expiryDate (date str),
                        preTradeNote (str), assetType (RESEARCH_ASSET_TYPE_UNSPECIFIED|RESEARCH_ASSET_TYPE_BOND|RESEARCH_ASSET_TYPE_EQUITY).
        """
        body: dict[str, Any] = {
            "title": title,
            "ownerId": owner_id,
            "shareable": shareable,
        }
        if description:
            body["description"] = description
        if column_tags:
            body["columnTags"] = column_tags
        if securities:
            body["securities"] = _build_security_dicts(securities)

        return _call_watchlist_api("/watchlists", http_method="post", request_body=body)

    @mcp.tool()
    def get_watchlist(watchlist_id: str) -> str:
        """Retrieve a saved watchlist by its ID.

        Args:
            watchlist_id: The unique ID of the watchlist to retrieve.
        """
        return _call_watchlist_api(
            f"/watchlists/{watchlist_id}",
            http_method="get",
        )

    @mcp.tool()
    def delete_watchlist(watchlist_id: str) -> str:
        """Delete a saved watchlist.

        Args:
            watchlist_id: The unique ID of the watchlist to delete.
        """
        return _call_watchlist_api(
            f"/watchlists/{watchlist_id}",
            http_method="delete",
        )

    @mcp.tool()
    def update_watchlist(
        watchlist_id: str,
        title: str | None = None,
        owner_id: str | None = None,
        description: str | None = None,
        shareable: bool | None = None,
        column_tags: list[str] | None = None,
        update_mask: str | None = None,
    ) -> str:
        """Update an existing watchlist's properties.

        Only the fields provided will be updated. Use update_mask to specify
        exactly which fields to update.

        Args:
            watchlist_id: The unique ID of the watchlist to update.
            title: New title for the watchlist.
            owner_id: New owner user ID.
            description: New description.
            shareable: Whether the watchlist can be shared.
            column_tags: New list of column tags.
            update_mask: Comma-separated list of fields to update (e.g. "title,description").
        """
        body: dict[str, Any] = {"id": watchlist_id}
        if title is not None:
            body["title"] = title
        if owner_id is not None:
            body["ownerId"] = owner_id
        if description is not None:
            body["description"] = description
        if shareable is not None:
            body["shareable"] = shareable
        if column_tags is not None:
            body["columnTags"] = column_tags

        params: dict[str, Any] | None = None
        if update_mask is not None:
            params = {"updateMask": update_mask}

        return _call_watchlist_api(
            f"/watchlists/{watchlist_id}",
            http_method="patch",
            request_body=body,
            params=params,
        )

    @mcp.tool()
    def add_securities_to_watchlist(
        watchlist_id: str,
        securities: list[dict[str, Any]],
    ) -> str:
        """Add securities to an existing watchlist.

        Args:
            watchlist_id: The ID of the watchlist to add securities to.
            securities: List of securities to add. Each dict can have:
                        assetId (str, required), addedDate (date str YYYY-MM-DD),
                        expiryDate (date str YYYY-MM-DD), preTradeNote (str),
                        assetType (RESEARCH_ASSET_TYPE_UNSPECIFIED|RESEARCH_ASSET_TYPE_BOND|RESEARCH_ASSET_TYPE_EQUITY).
        """
        body: dict[str, Any] = {
            "id": watchlist_id,
            "securities": _build_security_dicts(securities),
        }
        return _call_watchlist_api("/watchlists:addSecurities", http_method="post", request_body=body)

    @mcp.tool()
    def edit_securities_in_watchlist(
        watchlist_id: str,
        securities: list[dict[str, Any]],
    ) -> str:
        """Edit securities within a watchlist (update expiry date, pre-trade note, etc.).

        Args:
            watchlist_id: The ID of the watchlist containing the securities.
            securities: List of securities to edit. Each dict can have:
                        assetId (str, required - identifies which security to edit),
                        addedDate (date str YYYY-MM-DD), expiryDate (date str YYYY-MM-DD),
                        preTradeNote (str),
                        assetType (RESEARCH_ASSET_TYPE_UNSPECIFIED|RESEARCH_ASSET_TYPE_BOND|RESEARCH_ASSET_TYPE_EQUITY).
        """
        body: dict[str, Any] = {
            "id": watchlist_id,
            "securities": _build_security_dicts(securities),
        }
        return _call_watchlist_api("/watchlists:editSecurities", http_method="post", request_body=body)

    @mcp.tool()
    def remove_securities_from_watchlist(
        watchlist_id: str,
        securities: list[dict[str, Any]],
    ) -> str:
        """Remove securities from a watchlist by their asset IDs.

        Args:
            watchlist_id: The ID of the watchlist to remove securities from.
            securities: List of securities to remove. Each dict should have at least
                        assetId (str) to identify which security to remove.
        """
        body: dict[str, Any] = {
            "id": watchlist_id,
            "securities": _build_security_dicts(securities),
        }
        return _call_watchlist_api("/watchlists:removeSecurities", http_method="post", request_body=body)

    @mcp.tool()
    def search_watchlists(
        filter_criteria: list[str] | None = None,
        order_by: str | None = None,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> str:
        """Search watchlists by criteria such as owner, name, etc.

        Filter syntax examples:
          - 'owner:"username"' to filter by owner
          - 'Technology' to match anything containing "Technology"

        Args:
            filter_criteria: List of filter strings (e.g. ['owner:"jsmith"', 'Technology']).
            order_by: Sort order string (e.g. 'modified_time desc, owner').
            page_size: Max number of watchlists to return (default 10).
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

        return _call_watchlist_api("/watchlists:search", http_method="post", request_body=body)

    @mcp.tool()
    def filter_watchlists_by_user(owner_id: str) -> str:
        """Retrieve all watchlists owned by a specific user.

        Args:
            owner_id: The user ID to filter watchlists by.
        """
        body: dict[str, Any] = {"ownerId": owner_id}
        return _call_watchlist_api("/watchlists:filterByUser", http_method="post", request_body=body)
