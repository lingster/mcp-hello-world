"""MCP tools for the Aladdin Broker External Alias API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_BASE_PATH = "/api/investment-operations/reference-data/broker/v1/"

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
    """Helper to call a Broker External Alias API endpoint and return JSON string."""
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
        logger.error(f"Broker External Alias API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def _build_alias_dicts(aliases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize broker external alias dicts into the request wrapper format.

    Each entry is wrapped as ``{"brokerExternalAlias": { ... }}`` after
    filtering out ``None`` values.
    """
    wrapped: list[dict[str, Any]] = []
    for alias in aliases:
        entry: dict[str, Any] = {}
        for key in (
            "id",
            "brokerDeskId",
            "brokerExternalOrganisationId",
            "externalAlias",
            "alternateInfo1",
            "alternateInfo2",
        ):
            if alias.get(key) is not None:
                entry[key] = alias[key]
        wrapped.append({"brokerExternalAlias": entry})
    return wrapped


def register_broker_external_alias_tools(mcp: FastMCP) -> None:
    """Register Aladdin Broker External Alias API tools with the MCP server."""

    @mcp.tool()
    def batch_create_broker_external_aliases(
        requests: list[dict[str, Any]],
        broker_ticker: str | None = None,
        id: str | None = None,
    ) -> str:
        """Create one or more broker external aliases (max 100 per request).

        Required fields per alias: brokerTicker, brokerExternalOrganisationId, externalAlias.
        Users need permissions under permType='brkrAka'.

        Args:
            requests: List of broker external alias dicts to create. Each dict can have:
                      id (str), brokerDeskId (str), brokerExternalOrganisationId (str, required),
                      externalAlias (str, required), alternateInfo1 (str), alternateInfo2 (str).
            broker_ticker: Broker ticker (top-level, shared across all requests).
            id: Aladdin Broker Identifier (numeric, not currently supported).
        """
        body: dict[str, Any] = {
            "requests": _build_alias_dicts(requests),
        }
        if broker_ticker is not None:
            body["brokerTicker"] = broker_ticker
        if id is not None:
            body["id"] = id

        return _call_api("/brokerExternalAliases:batchCreate", http_method="post", request_body=body)

    @mcp.tool()
    def batch_remove_broker_external_aliases(
        requests: list[dict[str, Any]],
        broker_ticker: str | None = None,
        id: str | None = None,
    ) -> str:
        """Delete one or more broker external aliases (max 100 per request).

        Required fields per alias: brokerTicker, brokerExternalOrganisationId, externalAlias.
        Users need permissions under permType='brkrAka'.

        Args:
            requests: List of broker external alias dicts to remove. Each dict can have:
                      id (str), brokerDeskId (str), brokerExternalOrganisationId (str, required),
                      externalAlias (str, required), alternateInfo1 (str), alternateInfo2 (str).
            broker_ticker: Broker ticker (top-level, shared across all requests).
            id: Aladdin Broker Identifier (numeric, not currently supported).
        """
        body: dict[str, Any] = {
            "requests": _build_alias_dicts(requests),
        }
        if broker_ticker is not None:
            body["brokerTicker"] = broker_ticker
        if id is not None:
            body["id"] = id

        return _call_api("/brokerExternalAliases:batchRemove", http_method="post", request_body=body)

    @mcp.tool()
    def batch_update_broker_external_aliases(
        requests: list[dict[str, Any]],
        broker_ticker: str | None = None,
        id: str | None = None,
    ) -> str:
        """Batch update broker external aliases (max 100 per request).

        Required fields per alias: brokerTicker, brokerExternalOrganisationId, externalAlias.
        Users need permissions under permType='brkrAka'.

        Args:
            requests: List of broker external alias dicts to update. Each dict can have:
                      id (str), brokerDeskId (str), brokerExternalOrganisationId (str, required),
                      externalAlias (str, required), alternateInfo1 (str), alternateInfo2 (str).
            broker_ticker: Broker ticker (top-level, shared across all requests).
            id: Aladdin Broker Identifier (numeric, not currently supported).
        """
        body: dict[str, Any] = {
            "requests": _build_alias_dicts(requests),
        }
        if broker_ticker is not None:
            body["brokerTicker"] = broker_ticker
        if id is not None:
            body["id"] = id

        return _call_api("/brokerExternalAliases:batchUpdate", http_method="post", request_body=body)

    @mcp.tool()
    def batch_validate_broker_external_aliases(
        requests: list[dict[str, Any]],
        action_type: str = "ACTION_TYPE_UNSPECIFIED",
        broker_ticker: str | None = None,
        broker_id: str | None = None,
    ) -> str:
        """Validate multiple broker external alias requests for create or update API calls.

        Args:
            requests: List of broker external alias dicts to validate. Each dict can have:
                      id (str), brokerDeskId (str), brokerExternalOrganisationId (str),
                      externalAlias (str), alternateInfo1 (str), alternateInfo2 (str).
            action_type: Validation action type. One of:
                         ACTION_TYPE_UNSPECIFIED, ACTION_TYPE_CREATE, ACTION_TYPE_UPDATE.
            broker_ticker: Broker ticker (top-level, shared across all requests).
            broker_id: Aladdin Broker Identifier (numeric, not currently supported).
        """
        body: dict[str, Any] = {
            "requests": _build_alias_dicts(requests),
            "actionType": action_type,
        }
        if broker_ticker is not None:
            body["brokerTicker"] = broker_ticker
        if broker_id is not None:
            body["brokerId"] = broker_id

        return _call_api("/brokerExternalAliases:batchValidate", http_method="post", request_body=body)

    @mcp.tool()
    def filter_broker_external_aliases(
        broker_ticker: str | None = None,
        broker_id: str | None = None,
        load_defunct: bool | None = None,
        filter_type: str = "FILTER_TYPE_UNSPECIFIED",
        broker_tickers: list[str] | None = None,
        broker_type: str | None = None,
        broker_entity: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter broker external aliases by broker ticker, type, entity, or other criteria.

        Supports basic filtering (single broker ticker) and advanced filtering
        (combination of broker tickers list, broker type, and broker entity).

        Args:
            broker_ticker: Broker ticker for basic filtering.
            broker_id: Aladdin Broker Identifier (numeric, not currently supported).
            load_defunct: If true, load all aliases including defunct; otherwise only non-defunct.
            filter_type: Filter mode. One of:
                         FILTER_TYPE_UNSPECIFIED, FILTER_TYPE_BASIC,
                         FILTER_TYPE_ADVANCE, FILTER_TYPE_ID.
            broker_tickers: List of broker tickers for advanced filtering.
            broker_type: Broker type for advanced filtering.
            broker_entity: Broker entity for advanced filtering.
            page_size: Maximum number of results to return. 0 returns all.
            page_token: Page token from a previous call for pagination.
        """
        query: dict[str, Any] = {}
        if broker_ticker is not None:
            query["brokerTicker"] = broker_ticker
        if broker_id is not None:
            query["id"] = broker_id
        if load_defunct is not None:
            query["loadDefunct"] = load_defunct
        if filter_type != "FILTER_TYPE_UNSPECIFIED":
            query["filterType"] = filter_type

        extended_query: dict[str, Any] = {}
        if broker_tickers is not None:
            extended_query["brokerTickers"] = broker_tickers
        if broker_type is not None:
            extended_query["brokerType"] = broker_type
        if broker_entity is not None:
            extended_query["brokerEntity"] = broker_entity
        if extended_query:
            query["brokerExternalAliasExtendedQuery"] = extended_query

        body: dict[str, Any] = {}
        if query:
            body["brokerExternalAliasQuery"] = query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api("/brokerExternalAliases:filter", http_method="post", request_body=body)

    @mcp.tool()
    def retrieve_broker_external_alias(
        broker_external_organisation_id: str,
        external_alias: str,
    ) -> str:
        """Retrieve an exact-match broker external alias by organisation ID and alias value.

        Args:
            broker_external_organisation_id: External organisation identifier to search for.
            external_alias: External alias (extern id) value to search for.
        """
        params: dict[str, Any] = {
            "brokerExternalOrganisationId": broker_external_organisation_id,
            "externalAlias": external_alias,
        }
        return _call_api(
            "/brokerExternalAliases:retrieveBrokerExternalAlias",
            http_method="get",
            params=params,
        )
