"""MCP tools for the Aladdin Compliance Violation API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_VIOLATION_BASE_PATH = "/api/compliance/state/violation/v1/"

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


def _call_violation_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Violation API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_VIOLATION_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Violation API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_violation_tools(mcp: FastMCP) -> None:
    """Register Aladdin Compliance Violation API tools with the MCP server."""

    @mcp.tool()
    def get_violation(id: str) -> str:
        """Get a compliance violation by its ID.

        Retrieves the full violation record including details, resolution status,
        and associated metadata.

        Args:
            id: The unique identifier of the violation to retrieve.
        """
        return _call_violation_api(
            f"/violations/{id}",
            http_method="get",
        )

    @mcp.tool()
    def add_violation_detail(
        id: str,
        violation_detail: str,
        modification_time: str,
        cause_type: str | None = None,
    ) -> str:
        """Add a new detail and cause to an existing compliance violation.

        Posts the updated violation detail consisting of the detail text and
        an optional cause type describing the root cause.

        Args:
            id: The unique identifier of the violation to update.
            violation_detail: Further details on the violation, including any
                              transactions or positions that are part of it.
            modification_time: The last modified time (ISO 8601 date-time) of the
                               violation you intend to update. Used to validate that the
                               violation has not already been altered by someone else.
            cause_type: The root cause of the violation.
        """
        body: dict[str, Any] = {
            "violationDetail": violation_detail,
            "modificationTime": modification_time,
        }
        if cause_type is not None:
            body["causeType"] = cause_type

        return _call_violation_api(
            f"/violation/{id}/details:add",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def add_violation_resolution(
        id: str,
        modification_time: str,
        resolution_status: str | None = None,
        resolution_comment: str | None = None,
        violation_disposition: str | None = None,
    ) -> str:
        """Add a resolution update to an existing compliance violation.

        Updates the resolution state and/or adds resolution comments to a violation.

        Args:
            id: The unique identifier of the violation to update.
            modification_time: The last modified time (ISO 8601 date-time) of the
                               violation you intend to update. Used to validate that the
                               violation has not already been altered by someone else.
            resolution_status: State to move this violation to. Valid values are:
                               COMPLIANCE_RESOLUTIONS_STATE_UNSPECIFIED,
                               COMPLIANCE_RESOLUTIONS_STATE_ACTION_REQUIRED,
                               COMPLIANCE_RESOLUTIONS_STATE_ACTION_TAKEN,
                               COMPLIANCE_RESOLUTIONS_STATE_WORKING,
                               COMPLIANCE_RESOLUTIONS_STATE_CLOSED.
            resolution_comment: Resolution comments for the violation. Appended to
                                existing comments.
            violation_disposition: Disposition value, populated when a violation is
                                   being closed.
        """
        body: dict[str, Any] = {
            "modificationTime": modification_time,
        }
        if resolution_status is not None:
            body["resolutionStatus"] = resolution_status
        if resolution_comment is not None:
            body["resolutionComment"] = resolution_comment
        if violation_disposition is not None:
            body["violationDisposition"] = violation_disposition

        return _call_violation_api(
            f"/violation/{id}/resolutions:add",
            http_method="post",
            request_body=body,
        )
