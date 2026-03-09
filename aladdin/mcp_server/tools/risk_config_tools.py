"""MCP tools for the Aladdin Risk Governance Configuration API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_RISK_CONFIG_BASE_PATH = "/api/analytics/oversight/governance/v1/"

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
    """Helper to call a Risk Config API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_RISK_CONFIG_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Risk Config API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_risk_config_tools(mcp: FastMCP) -> None:
    """Register Aladdin Risk Config API tools with the MCP server."""

    @mcp.tool()
    def list_risk_config(
        filter: str | None = None,
        page_token: str | None = None,
        page_size: int | None = None,
    ) -> str:
        """List risk governance configuration records.

        Args:
            filter: Optional filter string to narrow results.
            page_token: Token for paginating through results.
            page_size: Maximum number of records to return per page.
        """
        params: dict[str, Any] = {}
        if filter is not None:
            params["filter"] = filter
        if page_token is not None:
            params["pageToken"] = page_token
        if page_size is not None:
            params["pageSize"] = page_size

        return _call_api("/config", http_method="get", params=params or None)

    @mcp.tool()
    def create_risk_config(
        config_type: str,
        config_entity_id: str,
        config_entity_type: str | None = None,
        summary: str | None = None,
        config_record: dict[str, Any] | None = None,
    ) -> str:
        """Create a new risk governance configuration record.

        Args:
            config_type: Configuration record type (e.g. 'CLOSE_OUT_REASON').
                         Must be unique for a given configuration family.
            config_entity_id: The ID of the entity this configuration record is for.
            config_entity_type: Entity type for the configuration. One of:
                                CONFIG_ENTITY_TYPE_UNSPECIFIED, CONFIG_ENTITY_TYPE_MASTER,
                                CONFIG_ENTITY_TYPE_RULE, CONFIG_ENTITY_TYPE_EVALUATOR,
                                CONFIG_ENTITY_TYPE_PORTFOLIO, CONFIG_ENTITY_TYPE_REFERENCE.
            summary: Description for this configuration record.
            config_record: Configuration record object. Can contain keys such as
                           genericConfigRecord (dict), displayConfigRecord (dict),
                           displayValueList (dict), referenceConfigRecord (dict),
                           customMetricConfigRecord (dict).
        """
        body: dict[str, Any] = {
            "configType": config_type,
            "configEntityId": config_entity_id,
        }
        if config_entity_type is not None:
            body["configEntityType"] = config_entity_type
        if summary is not None:
            body["summary"] = summary
        if config_record is not None:
            body["configRecord"] = config_record

        return _call_api("/config", http_method="post", request_body=body)

    @mcp.tool()
    def list_risk_config_revisions(
        risk_config_id: str,
        page_token: str | None = None,
        page_size: int | None = None,
    ) -> str:
        """Retrieve revision history for a risk configuration record.

        Args:
            risk_config_id: The unique ID of the risk configuration to get revisions for.
            page_token: Token for paginating through results.
            page_size: Maximum number of revisions to return per page.
        """
        params: dict[str, Any] = {"riskConfigId": risk_config_id}
        if page_token is not None:
            params["pageToken"] = page_token
        if page_size is not None:
            params["pageSize"] = page_size

        return _call_api("/config:listRevisions", http_method="get", params=params)

    @mcp.tool()
    def resolve_risk_config(
        filter: str | None = None,
        page_token: str | None = None,
        page_size: int | None = None,
    ) -> str:
        """List resolved risk governance configurations.

        Resolved configurations include populated reference config records
        with their resolved nodes.

        Args:
            filter: Optional filter string to narrow results.
            page_token: Token for paginating through results.
            page_size: Maximum number of records to return per page.
        """
        params: dict[str, Any] = {}
        if filter is not None:
            params["filter"] = filter
        if page_token is not None:
            params["pageToken"] = page_token
        if page_size is not None:
            params["pageSize"] = page_size

        return _call_api("/config:resolve", http_method="get", params=params or None)

    @mcp.tool()
    def retrieve_risk_config_by_id(
        config_ids: list[str] | None = None,
        compound_keys: list[dict[str, Any]] | None = None,
    ) -> str:
        """Bulk retrieve risk configuration records by IDs or compound keys.

        Provide either config_ids or compound_keys (not both).

        Args:
            config_ids: List of configuration record IDs to retrieve.
            compound_keys: List of compound key objects for lookup. Each dict can have:
                           configType (str, required) - e.g. 'CLOSE_OUT_REASON',
                           configEntityType (str) - e.g. 'CONFIG_ENTITY_TYPE_MASTER',
                           configEntityIds (list[str], required) - entity IDs to match.
        """
        body: dict[str, Any] = {}
        if config_ids is not None:
            body["retrieveRiskConfigRequestConfigId"] = {"configIds": config_ids}
        if compound_keys is not None:
            body["retrieveRiskConfigRequestCompoundKey"] = {
                "retrieveRiskConfigRequestCompoundKeyItems": compound_keys,
            }

        return _call_api(
            "/config:retrieveRiskConfigById",
            http_method="post",
            request_body=body,
        )
