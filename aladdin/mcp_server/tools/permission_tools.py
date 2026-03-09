"""MCP tools for the Aladdin Permission API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_PERMISSION_BASE_PATH = "/api/platform/access/permission/v1/"

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


def _call_permission_api(
    endpoint_path: str,
    http_method: str = "get",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Permission API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_PERMISSION_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Permission API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_permission_tools(mcp: FastMCP) -> None:
    """Register Aladdin Permission API tools with the MCP server."""

    @mcp.tool()
    def get_permission(permission_id: str) -> str:
        """Get details for a specific permission by its name/ID.

        Permissions cannot be applied directly to a user; they must be applied
        to a User Group first, then the user is added to a User Group.

        Args:
            permission_id: The name of the permission to retrieve.
        """
        return _call_permission_api(
            f"/permissions/{permission_id}",
            http_method="get",
        )

    @mcp.tool()
    def filter_permissions(
        user_group_id: str | None = None,
        page_token: str | None = None,
        page_size: int | None = None,
    ) -> str:
        """Filter and list permissions, optionally scoped to a User Group.

        Returns a list of permissions for a User Group. Returns all permissions
        if a User Group is not specified.

        Args:
            user_group_id: User Group ID to retrieve all permissions for.
                           If omitted, all permissions are returned.
            page_token: A page token received from a previous call.
                        Provide this to retrieve the subsequent page.
            page_size: The maximum number of permissions to return.
                       Defaults to 1000 if unspecified; maximum is 1000.
        """
        body: dict[str, Any] = {}
        if user_group_id is not None:
            body["permissionQuery"] = {"userGroupId": user_group_id}
        if page_token is not None:
            body["pageToken"] = page_token
        if page_size is not None:
            body["pageSize"] = page_size

        return _call_permission_api(
            "/permissions:filter",
            http_method="post",
            request_body=body,
        )
