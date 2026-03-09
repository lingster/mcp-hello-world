"""MCP tools for the Aladdin Abor Lot API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_BASE_PATH = "/api/accounting/transactions/abor-lot/v1/"

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
    """Helper to call an Abor Lot API endpoint and return JSON string."""
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
        logger.error(f"Abor Lot API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_abor_lot_tools(mcp: FastMCP) -> None:
    """Register Aladdin Abor Lot API tools with the MCP server."""

    @mcp.tool()
    def filter_abor_lots(
        portfolio_id: str,
        bases: list[str],
        last_valuation_date: str | None = None,
        snap_time: str | None = None,
    ) -> str:
        """Filter ABOR lots with AborLotSettings for a given portfolio.

        Retrieves AborLots from the ledger_a_summary table matching the
        specified portfolio and basis criteria.

        Args:
            portfolio_id: The portfolio ID to filter AborLots by (required).
            bases: List of basis strings to filter AborLot properties (required).
            last_valuation_date: Last valuation date to filter AborLots (format: YYYY-MM-DD).
            snap_time: Snap time / end date to filter AborLots (format: RFC 3339 date-time).
        """
        query: dict[str, Any] = {
            "portfolioId": portfolio_id,
            "bases": bases,
        }
        if last_valuation_date is not None:
            query["lastValuationDate"] = last_valuation_date
        if snap_time is not None:
            query["snapTime"] = snap_time

        body: dict[str, Any] = {"query": query}

        return _call_api("/aborLots:filter", http_method="post", request_body=body)
