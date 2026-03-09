"""MCP tools for the Aladdin Counter Party Settlement Instruction Template API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_COUNTER_PARTY_SETTLEMENT_INSTRUCTION_TEMPLATE_BASE_PATH = (
    "/api/investment-operations/reference-data/broker/v1/"
)

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
    """Helper to call a Counter Party Settlement Instruction Template API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_COUNTER_PARTY_SETTLEMENT_INSTRUCTION_TEMPLATE_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(
            f"Counter Party Settlement Instruction Template API call failed: "
            f"{http_method.upper()} {endpoint_path}: {e}"
        )
        return json.dumps({"error": str(e)})


def register_counter_party_settlement_instruction_template_tools(mcp: FastMCP) -> None:
    """Register Aladdin Counter Party Settlement Instruction Template API tools with the MCP server."""

    @mcp.tool()
    def get_counter_party_settlement_instruction_template(
        id: str,
    ) -> str:
        """Get a Counter Party Settlement Instruction Template by delivery method.

        Retrieves settlement instruction template information for a broker or account
        based on the delivery method identifier (e.g. fax). See decode named BRKR_DELIV_T.

        Args:
            id: Delivery method identifier. The method of delivery (e.g. fax).
                Please see decode named BRKR_DELIV_T.
        """
        return _call_api(
            f"/counterPartySettlementInstructionTemplates/{id}",
            http_method="get",
        )
