"""MCP tools for the Aladdin Token API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_TOKEN_BASE_PATH = "/api/platform/infrastructure/token/v1/"

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


def _call_token_api(
    endpoint_path: str,
    http_method: str = "get",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Token API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_TOKEN_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Token API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_token_tools(mcp: FastMCP) -> None:
    """Register Aladdin Token API tools with the MCP server."""

    @mcp.tool()
    def generate_authorization_url(
        application_name: str,
        redirect_uri: str,
        user: str,
    ) -> str:
        """Generate an Okta authorization URL for a user to consent to an application accessing third-party services.

        Follow the returned authorization URL to authenticate and provide consent.
        The resultant access and refresh token will then be available via generate_token.

        Args:
            application_name: The OAuth2 application client name.
            redirect_uri: The URI to be redirected to after authorization is complete.
            user: The user requesting the token.
        """
        params: dict[str, Any] = {
            "applicationName": application_name,
            "redirectUri": redirect_uri,
            "user": user,
        }
        return _call_token_api(
            "/authorizationUrl:generate",
            http_method="get",
            params=params,
        )

    @mcp.tool()
    def check_token_exists(
        application_name: str,
        user: str,
    ) -> str:
        """Check whether a token is stored by the token service for a specific user and application.

        Args:
            application_name: The OAuth2 application client name.
            user: The user to check token existence for.
        """
        params: dict[str, Any] = {
            "applicationName": application_name,
            "user": user,
        }
        return _call_token_api(
            "/token:checkTokenExists",
            http_method="get",
            params=params,
        )

    @mcp.tool()
    def generate_token(
        application_name: str,
    ) -> str:
        """Retrieve an access token for the authorized user.

        If no access token is available, complete the Authorization Code Flow
        beginning with generate_authorization_url first.

        Args:
            application_name: The OAuth2 application client name.
        """
        params: dict[str, Any] = {
            "applicationName": application_name,
        }
        return _call_token_api(
            "/token:generate",
            http_method="get",
            params=params,
        )
