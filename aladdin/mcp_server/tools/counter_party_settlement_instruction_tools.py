"""MCP tools for the Aladdin Counter Party Settlement Instruction API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_CPSI_BASE_PATH = "/api/investment-operations/reference-data/broker/v1/"

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
    """Helper to call a Counter Party Settlement Instruction API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_CPSI_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"CPSI API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_counter_party_settlement_instruction_tools(mcp: FastMCP) -> None:
    """Register Aladdin Counter Party Settlement Instruction API tools with the MCP server."""

    @mcp.tool()
    def get_counter_party_settlement_instruction(
        id: str,
    ) -> str:
        """Get a Counter Party Settlement Instruction by its settle code.

        Args:
            id: Id of the Counterparty Settlement instruction.
        """
        return _call_api(
            f"/counterPartySettlementInstructions/{id}",
            http_method="get",
        )

    @mcp.tool()
    def delete_counter_party_settlement_instruction(
        id: str,
        broker_id: str | None = None,
        broker_ticker: str | None = None,
    ) -> str:
        """Soft-delete a Counter Party Settlement Instruction by setting its entity value to -9999.

        Args:
            id: Id of the counter party settlement instruction to be soft deleted.
            broker_id: Aladdin Broker Identifier (Numeric). Not supported currently.
            broker_ticker: Broker ticker.
        """
        params: dict[str, Any] = {}
        if broker_id is not None:
            params["brokerId"] = broker_id
        if broker_ticker is not None:
            params["brokerTicker"] = broker_ticker

        return _call_api(
            f"/counterPartySettlementInstructions/{id}",
            http_method="delete",
            params=params or None,
        )

    @mcp.tool()
    def batch_create_counter_party_settlement_instructions(
        requests: list[dict[str, Any]],
        broker_ticker: str | None = None,
        broker_id: str | None = None,
        skip_bql_validation: bool | None = None,
        is_generic_template: bool | None = None,
    ) -> str:
        """Create one or more Counter Party Settlement Instructions (max 100 per request).

        Required fields per instruction: brokerTicker, deliveryName, settlementParties.
        Users need permissions under permType='brkrSettlm'.

        Args:
            requests: List of create request dicts. Each should contain a
                      'counterPartySettlementInstruction' dict and optionally 'autoApproved' (bool).
            broker_ticker: Broker ticker.
            broker_id: Aladdin Broker Identifier (Numeric). Not supported currently.
            skip_bql_validation: Skip BQL validation for the request.
            is_generic_template: Set true to create instructions without actual template
                                 definitions in settlement parties map.
        """
        body: dict[str, Any] = {"requests": requests}
        if broker_ticker is not None:
            body["brokerTicker"] = broker_ticker
        if broker_id is not None:
            body["brokerId"] = broker_id
        if skip_bql_validation is not None:
            body["skipBqlValidation"] = skip_bql_validation
        if is_generic_template is not None:
            body["isGenericTemplate"] = is_generic_template

        return _call_api(
            "/counterPartySettlementInstructions:batchCreate",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def batch_update_counter_party_settlement_instructions(
        requests: list[dict[str, Any]],
        broker_ticker: str | None = None,
        broker_id: str | None = None,
        skip_bql_validation: bool | None = None,
        is_generic_template: bool | None = None,
    ) -> str:
        """Batch update Counter Party Settlement Instructions.

        Required fields per instruction: id, brokerTicker, deliveryName, settlementParties.
        Users need permissions under permType='brkrSettlm'.

        Args:
            requests: List of update request dicts. Each should contain a
                      'counterPartySettlementInstruction' dict with the fields to update.
            broker_ticker: Broker ticker.
            broker_id: Aladdin Broker Identifier (Numeric). Not supported currently.
            skip_bql_validation: Skip BQL validation for the request.
            is_generic_template: Set true to update instructions without actual template
                                 definitions in settlement parties map.
        """
        body: dict[str, Any] = {"requests": requests}
        if broker_ticker is not None:
            body["brokerTicker"] = broker_ticker
        if broker_id is not None:
            body["brokerId"] = broker_id
        if skip_bql_validation is not None:
            body["skipBqlValidation"] = skip_bql_validation
        if is_generic_template is not None:
            body["isGenericTemplate"] = is_generic_template

        return _call_api(
            "/counterPartySettlementInstructions:batchUpdate",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def batch_update_counter_party_settlement_instructions_statuses(
        requests: list[dict[str, Any]],
        settlement_instruction_state: str | None = None,
    ) -> str:
        """Update status for multiple Counter Party Settlement Instructions.

        Args:
            requests: List of status update request dicts. Each should contain 'id' (str)
                      of the Counterparty Settlement instruction.
            settlement_instruction_state: The status to be updated for all counterparty
                                          settlement instructions with the specified settle code.
        """
        body: dict[str, Any] = {"requests": requests}
        if settlement_instruction_state is not None:
            body["settlementInstructionState"] = settlement_instruction_state

        return _call_api(
            "/counterPartySettlementInstructions:batchUpdateStatuses",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def batch_validate_counter_party_settlement_instructions(
        requests: list[dict[str, Any]],
        action_type: str | None = None,
        broker_ticker: str | None = None,
        broker_id: str | None = None,
        skip_bql_validation: bool | None = None,
        is_generic_template: bool | None = None,
    ) -> str:
        """Validate multiple Counter Party Settlement Instruction requests for create and update API calls.

        Args:
            requests: List of validate request dicts. Each should contain a
                      'counterPartySettlementInstruction' dict.
            action_type: Enum determining whether the request is a create or update request
                         for validation purposes.
            broker_ticker: Broker ticker.
            broker_id: Aladdin Broker Identifier (Numeric). Not supported currently.
            skip_bql_validation: Skip BQL validation for the request.
            is_generic_template: Set true to validate instructions without actual template
                                 definitions in settlement parties map.
        """
        body: dict[str, Any] = {"requests": requests}
        if action_type is not None:
            body["actionType"] = action_type
        if broker_ticker is not None:
            body["brokerTicker"] = broker_ticker
        if broker_id is not None:
            body["brokerId"] = broker_id
        if skip_bql_validation is not None:
            body["skipBqlValidation"] = skip_bql_validation
        if is_generic_template is not None:
            body["isGenericTemplate"] = is_generic_template

        return _call_api(
            "/counterPartySettlementInstructions:batchValidate",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def filter_counter_party_settlement_instructions(
        counterparty_settlement_instruction_query: dict[str, Any],
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter Counter Party Settlement Instructions based on a single broker ticker or advanced criteria.

        Supports basic filtering by broker ticker and/or loadDefunct flag, or advanced
        filtering by list of tickers, BrokerType, entity, etc.

        Args:
            counterparty_settlement_instruction_query: Query dict used to filter instructions.
                                                       Should include filter criteria such as
                                                       broker ticker, filter type, etc.
            page_size: Maximum number of instructions to return. If unspecified (0),
                       the complete list is returned.
            page_token: Page token from a previous call for pagination.
        """
        body: dict[str, Any] = {
            "counterpartySettlementInstructionQuery": counterparty_settlement_instruction_query,
        }
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api(
            "/counterPartySettlementInstructions:filter",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def search_counter_party_settlement_instructions(
        search: str,
        counter_party_settlement_instructions_search_type: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Search Counter Party Settlement Instructions based on an input query string.

        Args:
            search: Search string (at least two characters).
            counter_party_settlement_instructions_search_type: Search type enum. One of:
                COUNTER_PARTY_SETTLEMENT_INSTRUCTIONS_SEARCH_TYPE_UNSPECIFIED (defaults to BIC),
                COUNTER_PARTY_SETTLEMENT_INSTRUCTIONS_SEARCH_TYPE_BIC.
            page_size: Max number of results to return. Maximum is 100; values above
                       100 are coerced to 100. Default is 100.
            page_token: Page token from a previous call (pagination not supported currently).
        """
        params: dict[str, Any] = {"search": search}
        if counter_party_settlement_instructions_search_type is not None:
            params["counterPartySettlementInstructionsSearchType"] = (
                counter_party_settlement_instructions_search_type
            )
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token is not None:
            params["pageToken"] = page_token

        return _call_api(
            "/counterPartySettlementInstructions:search",
            http_method="get",
            params=params,
        )

    @mcp.tool()
    def undelete_counter_party_settlement_instruction(
        id: str,
        broker_ticker: str | None = None,
        broker_id: str | None = None,
    ) -> str:
        """Reverse a soft delete on a Counter Party Settlement Instruction by setting its entity value to 9999.

        Args:
            id: Id of the counter party settlement instruction to be undeleted.
            broker_ticker: Broker ticker.
            broker_id: Aladdin Broker Identifier (Numeric). Not supported currently.
        """
        body: dict[str, Any] = {"id": id}
        if broker_ticker is not None:
            body["brokerTicker"] = broker_ticker
        if broker_id is not None:
            body["brokerId"] = broker_id

        return _call_api(
            "/counterPartySettlementInstructions:undelete",
            http_method="post",
            request_body=body,
        )
