"""MCP tools for the Aladdin Collateral Statement API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_COLLATERAL_STATEMENT_BASE_PATH = (
    "/api/investment-operations/collateral-management/collateral-statement/v1/"
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


def _call_collateral_statement_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Collateral Statement API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_COLLATERAL_STATEMENT_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(
            f"Collateral Statement API call failed: {http_method.upper()} {endpoint_path}: {e}"
        )
        return json.dumps({"error": str(e)})


def register_collateral_statement_tools(mcp: FastMCP) -> None:
    """Register Aladdin Collateral Statement API tools with the MCP server."""

    @mcp.tool()
    def get_collateral_statement(statement_id: str) -> str:
        """Retrieve a single collateral statement and detail record by its statement ID.

        Args:
            statement_id: The unique statement ID to look up.
        """
        return _call_collateral_statement_api(
            f"/collateralStatement/{statement_id}",
            http_method="get",
        )

    @mcp.tool()
    def filter_collateral_statements(
        statement_date: str,
        portfolio_id: str | None = None,
        broker_id: str | None = None,
        statement_type: str | None = None,
        agreement_type: str | None = None,
        extern_entity: str | None = None,
        portfolio_ticker: str | None = None,
        broker_short_name: str | None = None,
        portfolio_group_id: str | None = None,
        modified_after_time: str | None = None,
        statement_detail_enrichment_flag: bool | None = None,
        asset_enrichment_flag: bool | None = None,
        uncollateral_flag: bool | None = None,
        cleared_flag: bool | None = None,
        exclude_collateral_pledge_held_flag: bool | None = None,
        bilateral_flag: bool | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter collateral statement and detail records by various criteria.

        Args:
            statement_date: Required. Statement date to filter by (YYYY-MM-DD format).
            portfolio_id: Filter by Aladdin portfolio code.
            broker_id: Filter by Aladdin broker code.
            statement_type: Filter by DECO statement type. Valid values include:
                DECO_STATEMENT_TYPE_UNSPECIFIED, DECO_STATEMENT_TYPE_A (cleared),
                DECO_STATEMENT_TYPE_B (exchange traded derivatives),
                DECO_STATEMENT_TYPE_C (cleared), DECO_STATEMENT_TYPE_D (OTC bilateral),
                DECO_STATEMENT_TYPE_E (exchange traded derivatives),
                DECO_STATEMENT_TYPE_L (Sec Lending Cash),
                DECO_STATEMENT_TYPE_R (CFD rate reset),
                DECO_STATEMENT_TYPE_S (substitution),
                DECO_STATEMENT_TYPE_U (OTC bilateral),
                DECO_STATEMENT_TYPE_H (Sec Lending Non Cash),
                DECO_STATEMENT_TYPE_O (Cleared Repo),
                DECO_STATEMENT_TYPE_M (End-of-day),
                DECO_STATEMENT_TYPE_X (cancelled),
                DECO_STATEMENT_TYPE_UMR (bilateral).
            agreement_type: Filter by DECO agreement type (e.g. DECO_AGREEMENT_TYPE_ISDA,
                DECO_AGREEMENT_TYPE_GMRA, DECO_AGREEMENT_TYPE_FUT, etc.).
            extern_entity: Filter by counterparty external entity value.
            portfolio_ticker: Filter by portfolio name/ticker.
            broker_short_name: Filter by broker short name.
            portfolio_group_id: Get statements for a portfolio group.
            modified_after_time: Filter for statements generated after a given timestamp
                (ISO 8601 date-time format).
            statement_detail_enrichment_flag: Flag to control the level of enrichment
                of the collateral data.
            asset_enrichment_flag: Flag to control the level of enrichment of the
                collateral asset data.
            uncollateral_flag: Flag to extract uncollateralized statements.
            cleared_flag: Flag to extract uncleared statements only.
            exclude_collateral_pledge_held_flag: Flag to exclude collateral pledge held.
            bilateral_flag: Flag to extract bilateral report (excludes cancelled statements).
            page_size: Max number of records to return (default 500, max 2000).
            page_token: Page token from a previous call for pagination.
        """
        query: dict[str, Any] = {"statementDate": statement_date}
        if portfolio_id is not None:
            query["portfolioId"] = portfolio_id
        if broker_id is not None:
            query["brokerId"] = broker_id
        if statement_type is not None:
            query["statementType"] = statement_type
        if agreement_type is not None:
            query["agreementType"] = agreement_type
        if extern_entity is not None:
            query["externEntity"] = extern_entity
        if portfolio_ticker is not None:
            query["portfolioTicker"] = portfolio_ticker
        if broker_short_name is not None:
            query["brokerShortName"] = broker_short_name
        if portfolio_group_id is not None:
            query["portfolioGroupId"] = portfolio_group_id
        if modified_after_time is not None:
            query["modifiedAfterTime"] = modified_after_time
        if statement_detail_enrichment_flag is not None:
            query["statementDetailEnrichmentFlag"] = statement_detail_enrichment_flag
        if asset_enrichment_flag is not None:
            query["assetEnrichmentFlag"] = asset_enrichment_flag
        if uncollateral_flag is not None:
            query["uncollateralFlag"] = uncollateral_flag
        if cleared_flag is not None:
            query["clearedFlag"] = cleared_flag
        if exclude_collateral_pledge_held_flag is not None:
            query["excludeCollateralPledgeHeldFlag"] = exclude_collateral_pledge_held_flag
        if bilateral_flag is not None:
            query["bilateralFlag"] = bilateral_flag

        body: dict[str, Any] = {"query": query}
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_collateral_statement_api(
            "/collateralStatements:filter",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def get_collateral_statement_long_running_operation(operation_id: str) -> str:
        """Poll the state of a long-running collateral statement operation.

        Use this to check the status/result of a previously submitted filter request
        that returned a long-running operation.

        Args:
            operation_id: The unique ID of the long-running operation to poll.
        """
        return _call_collateral_statement_api(
            f"/longRunningOperations/{operation_id}",
            http_method="get",
        )
