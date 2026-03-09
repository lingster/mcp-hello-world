"""MCP tools for the Aladdin Account Info API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_BASE_PATH = "/api/investment-operations/reference-data/account-info/v1/"

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
    """Helper to call an Account Info API endpoint and return JSON string."""
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
        logger.error(f"Account Info API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_account_info_tools(mcp: FastMCP) -> None:
    """Register Aladdin Account Info API tools with the MCP server."""

    @mcp.tool()
    def filter_account_infos(
        ids: list[str] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter account info based on a list of account codes or other custom filter criteria.

        Args:
            ids: List of account codes for which account info data is to be retrieved.
            page_size: The maximum number of account infos to return. If unspecified
                       (i.e. 0), the complete list of account infos will be returned.
            page_token: A page token received from a previous FilterAccountInfos call.
                        Provide this to retrieve the subsequent page.
        """
        body: dict[str, Any] = {}
        if ids is not None:
            body["query"] = {"ids": ids}
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api("/accountInfos:filter", http_method="post", request_body=body)

    @mcp.tool()
    def search_account_infos(
        search: str,
        acct_info_search_type: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Search account info based on an input query string.

        Args:
            search: Search string (at least two characters).
            acct_info_search_type: Account info search type. One of
                ACCOUNT_INFO_SEARCH_TYPE_UNSPECIFIED (default) or
                ACCOUNT_INFO_SEARCH_TYPE_ACCOUNT_NAME (searches accountName field).
            page_size: The maximum number of results to return. Max 100; values above
                       100 will be coerced to 100. Default is 100.
            page_token: A page token received from a previous call (pagination is not
                        currently supported).
        """
        params: dict[str, Any] = {"search": search}
        if acct_info_search_type is not None:
            params["acctInfoSearchType"] = acct_info_search_type
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token is not None:
            params["pageToken"] = page_token

        return _call_api("/accountInfos:search", http_method="get", params=params)
