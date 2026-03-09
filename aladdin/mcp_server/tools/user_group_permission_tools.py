"""MCP tools for the Aladdin User Group Permission API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_USER_GROUP_PERMISSION_BASE_PATH = "/api/platform/access/permission/v1/"

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


def _call_user_group_permission_api(
    endpoint_path: str,
    http_method: str = "get",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a User Group Permission API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_USER_GROUP_PERMISSION_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"User Group Permission API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_user_group_permission_tools(mcp: FastMCP) -> None:
    """Register Aladdin User Group Permission API tools with the MCP server."""

    @mcp.tool()
    def list_user_group_permissions(
        parent: str,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """List permissions for a user group.

        Args:
            parent: The user group identifier (e.g. the user group name).
            page_size: Maximum number of permissions to return per page.
            page_token: Token for retrieving the next page of results.
        """
        params: dict[str, Any] = {}
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token is not None:
            params["pageToken"] = page_token

        return _call_user_group_permission_api(
            f"/userGroups/{parent}/userGroupPermissions",
            http_method="get",
            params=params if params else None,
        )

    @mcp.tool()
    def batch_create_user_group_permissions(
        parent: str,
        permissions: list[dict[str, str]],
    ) -> str:
        """Add permissions to a user group in batch.

        A maximum of 100 permissions can be added in a single batch.

        Args:
            parent: The user group identifier to add permissions to.
            permissions: List of permission dicts, each with:
                         - permissionId (str, required): The permission type.
                         - permissionGroup (str, required): The permission group scope
                           (e.g. PORTFOLIO, PORTGROUP, NONE, or a tbl_desc value).
        """
        requests: list[dict[str, Any]] = [
            {"userGroupPermission": perm} for perm in permissions
        ]
        body: dict[str, Any] = {"requests": requests}

        return _call_user_group_permission_api(
            f"/userGroups/{parent}/userGroupPermissions:batchCreate",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def batch_delete_user_group_permissions(
        parent: str,
        permissions: list[dict[str, str]],
    ) -> str:
        """Remove permissions from a user group in batch.

        A maximum of 100 permissions can be removed in a single batch.

        Args:
            parent: The user group identifier to remove permissions from.
            permissions: List of permission dicts, each with:
                         - permissionId (str, required): The permission type.
                         - permissionGroup (str, required): The permission group scope
                           (e.g. PORTFOLIO, PORTGROUP, NONE, or a tbl_desc value).
        """
        delete_requests: list[dict[str, Any]] = [
            {"userGroupPermission": perm} for perm in permissions
        ]
        body: dict[str, Any] = {"deleteRequests": delete_requests}

        return _call_user_group_permission_api(
            f"/userGroups/{parent}/userGroupPermissions:batchDelete",
            http_method="post",
            request_body=body,
        )
