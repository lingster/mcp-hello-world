"""MCP tools for the Aladdin Broker Entities Audit API."""

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
    """Helper to call an Audit API endpoint and return JSON string."""
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
        logger.error(f"Audit API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_audit_tools(mcp: FastMCP) -> None:
    """Register Aladdin Broker Audit API tools with the MCP server."""

    @mcp.tool()
    def filter_entity_revisions(
        entity_definition: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        defunct: bool | None = None,
        broker_audit_criterion: dict[str, Any] | None = None,
        broker_desk_audit_criterion: dict[str, Any] | None = None,
        broker_external_alias_audit_criterion: dict[str, Any] | None = None,
        broker_confirm_routing_audit_criterion: dict[str, Any] | None = None,
        counter_party_settlement_instruction_audit_criterion: dict[str, Any] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter audit data for broker entities.

        Retrieves audit revision history for broker-related entities such as
        brokers, broker desks, broker external aliases, broker confirm routings,
        and counterparty settlement instructions.

        Args:
            entity_definition: The audit entity type to filter on. One of:
                AUDIT_ENTITY_DEFINITION_UNSPECIFIED,
                AUDIT_ENTITY_DEFINITION_BROKER,
                AUDIT_ENTITY_DEFINITION_BROKER_DESK,
                AUDIT_ENTITY_DEFINITION_BROKER_CONFIRM_ROUTING,
                AUDIT_ENTITY_DEFINITION_BROKER_EXTERNAL_ALIAS,
                AUDIT_ENTITY_DEFINITION_COUNTER_PARTY_SETTLEMENT_INSTRUCTION.
            start_date: Start of date range for audit records (date string, e.g. "2024-01-01").
            end_date: End of date range for audit records (date string, e.g. "2024-12-31").
            defunct: If true, load only defunct counterparties and associated data.
            broker_audit_criterion: Criteria for broker entity audit. Dict with keys:
                brokerTickers (list[str]) - broker tickers to filter on,
                brokerType (str) - broker type filter.
            broker_desk_audit_criterion: Criteria for broker desk audit. Dict with keys:
                brokerTickers (list[str]) - broker tickers to filter on.
            broker_external_alias_audit_criterion: Criteria for broker external alias audit.
                Dict with keys: brokerTickers (list[str]) - broker tickers to filter on.
            broker_confirm_routing_audit_criterion: Criteria for broker confirm routing audit.
                Dict with keys: brokerTickers (list[str]) - broker tickers to filter on.
            counter_party_settlement_instruction_audit_criterion: Criteria for counterparty
                settlement instruction audit. Dict with keys:
                brokerTickers (list[str]) - broker tickers to filter on,
                deliveryName (str) - delivery name filter.
            page_size: Max number of audit records to return (max 500, default 500).
            page_token: Page token from a previous call for pagination.
        """
        query: dict[str, Any] = {}
        if entity_definition is not None:
            query["entityDefinition"] = entity_definition
        if start_date is not None:
            query["startDate"] = start_date
        if end_date is not None:
            query["endDate"] = end_date
        if defunct is not None:
            query["defunct"] = defunct
        if broker_audit_criterion is not None:
            query["brokerAuditCriterion"] = broker_audit_criterion
        if broker_desk_audit_criterion is not None:
            query["brokerDeskAuditCriterion"] = broker_desk_audit_criterion
        if broker_external_alias_audit_criterion is not None:
            query["brokerExternalAliasAuditCriterion"] = broker_external_alias_audit_criterion
        if broker_confirm_routing_audit_criterion is not None:
            query["brokerConfirmRoutingAuditCriterion"] = broker_confirm_routing_audit_criterion
        if counter_party_settlement_instruction_audit_criterion is not None:
            query["counterPartySettlementInstructionAuditCriterion"] = (
                counter_party_settlement_instruction_audit_criterion
            )

        body: dict[str, Any] = {}
        if query:
            body["query"] = query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api("/entityRevisions:filter", http_method="post", request_body=body)
