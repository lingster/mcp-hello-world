"""MCP tools for the Aladdin User Group API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_USER_GROUP_BASE_PATH = "/api/platform/access/user-group/v1/"

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


def _call_user_group_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a User Group API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_USER_GROUP_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"User Group API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_user_group_tools(mcp: FastMCP) -> None:
    """Register Aladdin User Group API tools with the MCP server."""

    @mcp.tool()
    def create_user_group(
        id: str,
        group_description: str = "",
        root_group_id: str | None = None,
        node_type: str | None = None,
        auth_user_group: str | None = None,
        parent_user_group_id: str | None = None,
    ) -> str:
        """Create a new Aladdin User Group.

        Prerequisite: You must have the Aladdin Permission PERMS_GROUP_CREATE
        or MOD_PERMS.

        Args:
            id: The name of the User Group.
            group_description: The description of the User Group.
            root_group_id: The Root User Group - required for Node Type G.
            node_type: The Node Type. One of: NODE_TYPE_UNSPECIFIED,
                       NODE_TYPE_USER_GROUP, NODE_TYPE_INTERNAL,
                       NODE_TYPE_ROOT, NODE_TYPE_OTHER.
            auth_user_group: The Authorization User Group.
            parent_user_group_id: The Parent User Group - required for Node Type G.
        """
        body: dict[str, Any] = {"id": id}
        if group_description:
            body["groupDescription"] = group_description
        if root_group_id is not None:
            body["rootGroupId"] = root_group_id
        if node_type is not None:
            body["nodeType"] = node_type
        if auth_user_group is not None:
            body["authUserGroup"] = auth_user_group
        if parent_user_group_id is not None:
            body["parentUserGroupId"] = parent_user_group_id

        return _call_user_group_api("/userGroups", http_method="post", request_body=body)

    @mcp.tool()
    def get_user_group(user_group_id: str) -> str:
        """Get details for a specified User Group.

        Args:
            user_group_id: The unique ID of the User Group to retrieve.
        """
        return _call_user_group_api(
            f"/userGroups/{user_group_id}",
            http_method="get",
        )

    @mcp.tool()
    def delete_user_group(user_group_id: str) -> str:
        """Delete a User Group.

        Prerequisite: You must have the Aladdin Permission PERMS_GROUP_DELETE
        or MOD_PERMS. The User Group should not have active users and/or
        active children.

        Args:
            user_group_id: The unique ID of the User Group to delete.
        """
        return _call_user_group_api(
            f"/userGroups/{user_group_id}",
            http_method="delete",
        )

    @mcp.tool()
    def update_user_group(
        user_group_id: str,
        group_description: str | None = None,
        root_group_id: str | None = None,
        node_type: str | None = None,
        auth_user_group: str | None = None,
        parent_user_group_id: str | None = None,
        update_mask: str | None = None,
    ) -> str:
        """Update an existing User Group.

        Prerequisite: You must have the Aladdin Permission PERMS_GROUP_CREATE
        or MOD_PERMS. Fields that can be updated: group_description,
        auth_user_group, parent_user_group_id, root_group_id.

        Args:
            user_group_id: The unique ID of the User Group to update.
            group_description: New description for the User Group.
            root_group_id: New Root User Group.
            node_type: The Node Type. One of: NODE_TYPE_UNSPECIFIED,
                       NODE_TYPE_USER_GROUP, NODE_TYPE_INTERNAL,
                       NODE_TYPE_ROOT, NODE_TYPE_OTHER.
            auth_user_group: New Authorization User Group.
            parent_user_group_id: New Parent User Group.
            update_mask: Comma-separated list of fields to update
                         (e.g. "groupDescription,authUserGroup").
        """
        body: dict[str, Any] = {"id": user_group_id}
        if group_description is not None:
            body["groupDescription"] = group_description
        if root_group_id is not None:
            body["rootGroupId"] = root_group_id
        if node_type is not None:
            body["nodeType"] = node_type
        if auth_user_group is not None:
            body["authUserGroup"] = auth_user_group
        if parent_user_group_id is not None:
            body["parentUserGroupId"] = parent_user_group_id

        params: dict[str, Any] | None = None
        if update_mask is not None:
            params = {"updateMask": update_mask}

        return _call_user_group_api(
            f"/userGroups/{user_group_id}",
            http_method="patch",
            request_body=body,
            params=params,
        )

    @mcp.tool()
    def filter_user_groups(
        user_id: str | None = None,
        permission_id: str | None = None,
        membership_type: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter User Groups by user or permission.

        Returns a list of User Groups for a user or permission. Returns all
        User Groups if a user or permission is not specified.

        Args:
            user_id: User ID to retrieve all User Groups the user is in.
            permission_id: Permission ID to retrieve all User Groups the
                           permission is applied to.
            membership_type: Membership Type filter, used with user_id.
                             One of: MEMBERSHIP_TYPE_UNSPECIFIED,
                             MEMBERSHIP_TYPE_DIRECT, MEMBERSHIP_TYPE_INDIRECT.
            page_size: Maximum number of records to return (default 1000).
            page_token: Page token from a previous call for pagination.
        """
        body: dict[str, Any] = {}
        user_group_query: dict[str, Any] = {}
        if user_id is not None:
            user_group_query["userId"] = user_id
        if permission_id is not None:
            user_group_query["permissionId"] = permission_id
        if membership_type is not None:
            user_group_query["membershipType"] = membership_type
        if user_group_query:
            body["userGroupQuery"] = user_group_query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_user_group_api("/userGroups:filter", http_method="post", request_body=body)
