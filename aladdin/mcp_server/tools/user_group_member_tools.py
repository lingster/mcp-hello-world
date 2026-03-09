"""MCP tools for the Aladdin User Group Member API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_USER_GROUP_MEMBER_BASE_PATH = "/api/platform/access/user-group/v1/"

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
    """Helper to call a User Group Member API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_USER_GROUP_MEMBER_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"User Group Member API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_user_group_member_tools(mcp: FastMCP) -> None:
    """Register Aladdin User Group Member API tools with the MCP server."""

    @mcp.tool()
    def list_user_group_members(
        parent: str,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """List all members of a specified User Group.

        Returns all members of the specified User Group. Note: This is not
        intended to be used for Authorization.

        Args:
            parent: The user group identifier whose members to list.
            page_size: Maximum number of members to return per page.
            page_token: Token for retrieving the next page of results.
        """
        params: dict[str, Any] = {}
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token is not None:
            params["pageToken"] = page_token

        return _call_api(
            f"/userGroups/{parent}/members",
            http_method="get",
            params=params if params else None,
        )

    @mcp.tool()
    def batch_create_user_group_members(
        parent: str,
        user_ids: list[str],
    ) -> str:
        """Add users to a User Group in batch.

        A maximum of 100 users can be added in a single batch request.

        Args:
            parent: The user group identifier to add members to.
            user_ids: List of user IDs to add to the group.
        """
        create_requests: list[dict[str, Any]] = [
            {"userGroupMember": {"id": uid}} for uid in user_ids
        ]
        body: dict[str, Any] = {"createRequests": create_requests}

        return _call_api(
            f"/userGroups/{parent}/members:batchCreate",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def batch_delete_user_group_members(
        parent: str,
        user_ids: list[str],
    ) -> str:
        """Remove users from a User Group in batch.

        A maximum of 100 users can be removed in a single batch request.

        Args:
            parent: The user group identifier to remove members from.
            user_ids: List of user IDs to remove from the group.
        """
        body: dict[str, Any] = {"ids": user_ids}

        return _call_api(
            f"/userGroups/{parent}/members:batchDelete",
            http_method="post",
            request_body=body,
        )
