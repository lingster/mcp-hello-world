"""MCP tools for the Aladdin Restricted Asset API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_RESTRICTED_ASSET_BASE_PATH = "/api/portfolio/configuration/restricted-asset/v1/"

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


def _call_restricted_asset_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Restricted Asset API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_RESTRICTED_ASSET_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Restricted Asset API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def _build_restricted_asset_dict(asset: dict[str, Any]) -> dict[str, Any]:
    """Normalize a restricted asset dict, filtering out None values."""
    entry: dict[str, Any] = {}
    if asset.get("id"):
        entry["id"] = asset["id"]
    if asset.get("cusip"):
        entry["cusip"] = asset["cusip"]
    if asset.get("endDate"):
        entry["endDate"] = asset["endDate"]
    if asset.get("restrictedAmount") is not None:
        entry["restrictedAmount"] = asset["restrictedAmount"]
    if asset.get("purpose"):
        entry["purpose"] = asset["purpose"]
    if asset.get("state"):
        entry["state"] = asset["state"]
    if asset.get("restrictionCode"):
        entry["restrictionCode"] = asset["restrictionCode"]
    if asset.get("source"):
        entry["source"] = asset["source"]
    return entry


def register_restricted_asset_tools(mcp: FastMCP) -> None:
    """Register Aladdin Restricted Asset API tools with the MCP server."""

    @mcp.tool()
    def list_restricted_assets(
        parent: str,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """List restricted assets for a portfolio.

        Retrieves current or future restricted assets by portfolio ID.
        The maximum number of restricted assets returned in one call is 10000.
        Use pagination to limit the number of records returned.

        Args:
            parent: The portfolio ID to list restricted assets for.
            page_size: Maximum number of restricted assets to return (max 10000).
                       A value less than 1 returns all records.
            page_token: Page token from a previous ListRestrictedAssets call
                        to retrieve the next page.
        """
        params: dict[str, Any] = {}
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token is not None:
            params["pageToken"] = page_token

        return _call_restricted_asset_api(
            f"/portfolios/{parent}/restrictedAssets",
            http_method="get",
            params=params if params else None,
        )

    @mcp.tool()
    def batch_create_restricted_assets(
        restricted_assets: list[dict[str, Any]],
    ) -> str:
        """Create new restricted assets for given portfolios.

        The maximum number of restricted assets that can be created in one call is 1000.
        Permissions Required: asReAsMOD

        Args:
            restricted_assets: List of restricted asset dicts to create. Each dict should contain:
                - id (dict): Composite ID with portfolioId (str, required),
                  startDate (str date, required), investmentNumber (int, optional).
                - cusip (str, required): The CUSIP identifier.
                - restrictedAmount (float, required): Amount of security to restrict.
                - purpose (str, required): Why the security is restricted.
                  Must be a valid purpose from the Aladdin RestrAssetReas table (case sensitive).
                - state (str, required): RESTRICTED_ASSET_STATE_YES or RESTRICTED_ASSET_STATE_NO.
                - endDate (str date, optional): Date the security comes off restriction.
                - restrictionCode (str, optional): User-defined restriction code.
                - source (str, optional): Link to external source where restriction originated.
        """
        requests: list[dict[str, Any]] = [
            {"restrictedAsset": _build_restricted_asset_dict(asset)}
            for asset in restricted_assets
        ]
        body: dict[str, Any] = {"requests": requests}
        return _call_restricted_asset_api(
            "/restrictedAssets:batchCreate",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def batch_terminate_restricted_assets(
        termination_requests: list[dict[str, Any]],
    ) -> str:
        """Terminate restricted assets for given portfolios.

        The maximum number of restricted assets that can be terminated in one call is 1000.
        Permissions Required: asReAsMOD

        Args:
            termination_requests: List of termination request dicts. Each dict should contain:
                - id (dict): Composite ID with portfolioId (str, required),
                  startDate (str date, required), investmentNumber (int, optional).
                - terminationDate (str date, optional): The termination date.
                  Cannot point to the past. If not provided, the current date is used.
        """
        requests: list[dict[str, Any]] = []
        for req in termination_requests:
            entry: dict[str, Any] = {}
            if req.get("id"):
                entry["id"] = req["id"]
            if req.get("terminationDate"):
                entry["terminationDate"] = req["terminationDate"]
            requests.append(entry)

        body: dict[str, Any] = {"requests": requests}
        return _call_restricted_asset_api(
            "/restrictedAssets:batchTerminate",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def batch_update_restricted_assets(
        restricted_assets: list[dict[str, Any]],
        update_mask: str | None = None,
    ) -> str:
        """Update existing restricted assets for given portfolios.

        The maximum number of restricted assets that can be updated in one call is 1000.
        Permissions Required: asReAsMOD

        Args:
            restricted_assets: List of restricted asset dicts to update. Each dict should contain:
                - id (dict): Composite ID with portfolioId (str, required),
                  startDate (str date, required), investmentNumber (int, optional).
                - cusip (str, required): The CUSIP identifier.
                - restrictedAmount (float, required): Amount of security to restrict.
                - purpose (str, required): Why the security is restricted.
                - state (str, required): RESTRICTED_ASSET_STATE_YES or RESTRICTED_ASSET_STATE_NO.
                - endDate (str date, optional): Date the security comes off restriction.
                - restrictionCode (str, optional): User-defined restriction code.
                - source (str, optional): Link to external source where restriction originated.
            update_mask: Comma-separated list of fields to update (currently not supported by API).
        """
        requests: list[dict[str, Any]] = []
        for asset in restricted_assets:
            entry: dict[str, Any] = {
                "restrictedAsset": _build_restricted_asset_dict(asset),
            }
            if update_mask is not None:
                entry["updateMask"] = update_mask
            requests.append(entry)

        body: dict[str, Any] = {"requests": requests}
        return _call_restricted_asset_api(
            "/restrictedAssets:batchUpdate",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def batch_upsert_restricted_assets(
        restricted_assets: list[dict[str, Any]],
        update_mask: str | None = None,
    ) -> str:
        """Upsert restricted assets for given portfolios.

        Creates new restricted assets or updates existing ones. Sets the end date to
        closed and adds new restricted assets by setting new values.
        The maximum number of restricted assets that can be upserted in one call is 1000.
        Permissions Required: asReAsMOD

        Args:
            restricted_assets: List of restricted asset dicts to upsert. Each dict should contain:
                - id (dict): Composite ID with portfolioId (str, required),
                  startDate (str date, required), investmentNumber (int, optional).
                - cusip (str, required): The CUSIP identifier.
                - restrictedAmount (float, required): Amount of security to restrict.
                - purpose (str, required): Why the security is restricted.
                - state (str, required): RESTRICTED_ASSET_STATE_YES or RESTRICTED_ASSET_STATE_NO.
                - endDate (str date, optional): Date the security comes off restriction.
                - restrictionCode (str, optional): User-defined restriction code.
                - source (str, optional): Link to external source where restriction originated.
            update_mask: Comma-separated list of fields to upsert (currently not supported by API).
        """
        requests: list[dict[str, Any]] = []
        for asset in restricted_assets:
            entry: dict[str, Any] = {
                "restrictedAsset": _build_restricted_asset_dict(asset),
            }
            if update_mask is not None:
                entry["updateMask"] = update_mask
            requests.append(entry)

        body: dict[str, Any] = {"requests": requests}
        return _call_restricted_asset_api(
            "/restrictedAssets:batchUpsert",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def filter_restricted_assets(
        portfolio_code: str | None = None,
        ticker: str | None = None,
        cusip: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        restricted_amount: float | None = None,
        author: str | None = None,
        entry_date: str | None = None,
        purpose: str | None = None,
        state: str | None = None,
        restriction_code: str | None = None,
        source: str | None = None,
        investment_numbers: list[int] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter restricted assets based on various parameters.

        You must specify either a portfolio_code or ticker to filter by.
        The maximum number of restricted assets returned in one call is 10000.

        Args:
            portfolio_code: Portfolio code to filter by.
            ticker: Ticker/portfolio name to filter by.
            cusip: CUSIP identifier to filter by.
            start_date: Start date filter (YYYY-MM-DD) for when security starts being restricted.
            end_date: End date filter (YYYY-MM-DD) for when security comes off restriction.
            restricted_amount: Restricted amount filter.
            author: Author who entered the restriction.
            entry_date: Entry date filter (YYYY-MM-DD).
            purpose: Purpose/reason for restriction.
            state: State filter (RESTRICTED_ASSET_STATE_UNSPECIFIED,
                   RESTRICTED_ASSET_STATE_YES, RESTRICTED_ASSET_STATE_NO).
            restriction_code: User-defined restriction code.
            source: External source where restriction originated.
            investment_numbers: List of investment numbers to filter by.
            page_size: Maximum number of restricted assets to return (max 10000).
            page_token: Page token from a previous FilterRestrictedAssets call.
        """
        query: dict[str, Any] = {}
        if portfolio_code is not None:
            query["portfolioCode"] = portfolio_code
        if ticker is not None:
            query["ticker"] = ticker
        if cusip is not None:
            query["cusip"] = cusip
        if start_date is not None:
            query["startDate"] = start_date
        if end_date is not None:
            query["endDate"] = end_date
        if restricted_amount is not None:
            query["restrictedAmount"] = restricted_amount
        if author is not None:
            query["author"] = author
        if entry_date is not None:
            query["entryDate"] = entry_date
        if purpose is not None:
            query["purpose"] = purpose
        if state is not None:
            query["state"] = state
        if restriction_code is not None:
            query["restrictionCode"] = restriction_code
        if source is not None:
            query["source"] = source
        if investment_numbers is not None:
            query["investmentNumbers"] = investment_numbers

        body: dict[str, Any] = {}
        if query:
            body["query"] = query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_restricted_asset_api(
            "/restrictedAssets:filter",
            http_method="post",
            request_body=body,
        )
