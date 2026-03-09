"""MCP tools for the Aladdin Corporate Action API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_CORPORATE_ACTION_BASE_PATH = "/api/investment-operations/asset-lifecycle/corporate-action/v1/"

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


def _call_corporate_action_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Corporate Action API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_CORPORATE_ACTION_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Corporate Action API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_corporate_action_tools(mcp: FastMCP) -> None:
    """Register Aladdin Corporate Action API tools with the MCP server."""

    @mcp.tool()
    def get_corporate_action(
        id: str,
        corporate_action_view: str | None = None,
    ) -> str:
        """Get a corporate action by its ID.

        A corporate action is an event triggered by a public company that
        changes an equity or fixed income security issued by the company.

        Args:
            id: Corporate action ID.
            corporate_action_view: View of the corporate action resource.
                Defaults to 'CORPORATE_ACTION_VIEW_FULL' if not specified.
                Valid values: CORPORATE_ACTION_VIEW_UNSPECIFIED,
                CORPORATE_ACTION_VIEW_FULL.
        """
        params: dict[str, Any] | None = None
        if corporate_action_view is not None:
            params = {"corporateActionView": corporate_action_view}

        return _call_corporate_action_api(
            f"/corporateActions/{id}",
            http_method="get",
            params=params,
        )

    @mcp.tool()
    def filter_corporate_actions(
        ids: list[str] | None = None,
        external_corporate_action_ids: list[str] | None = None,
        asset_ids: list[str] | None = None,
        corporate_action_types: list[str] | None = None,
        corporate_action_sub_types: list[str] | None = None,
        lifecycle_date: str | None = None,
        corporate_action_data_sources: list[str] | None = None,
        corporate_action_workflow_states: list[str] | None = None,
        start_processing_date: str | None = None,
        end_processing_date: str | None = None,
        start_expiration_date: str | None = None,
        end_expiration_date: str | None = None,
        start_payable_date: str | None = None,
        end_payable_date: str | None = None,
        start_modify_time: str | None = None,
        end_modify_time: str | None = None,
        voluntary_mandatory_code: str | None = None,
        portfolio_group_name: str | None = None,
        page_token: str | None = None,
        page_size: int | None = None,
        corporate_action_view: str | None = None,
    ) -> str:
        """Filter corporate actions by various criteria.

        A corporate action is an event triggered by a public company that
        changes an equity or fixed income security issued by the company.
        There are two main categories: Mandatory and Voluntary.

        If corporate action IDs are provided, all other query criteria fields
        are ignored.

        Args:
            ids: Internal corporate action IDs.
            external_corporate_action_ids: External corporate action IDs.
            asset_ids: Asset IDs related to corporate actions.
            corporate_action_types: Corporate action types to filter by.
            corporate_action_sub_types: Corporate action sub-types to filter by.
            lifecycle_date: Lifecycle date (checked against lifecycle start/end).
                Defaults to today. Date is in Aladdin Server timezone.
            corporate_action_data_sources: Vendor or custodian that provided
                the corporate action feed. 'COMPOSITE' represents the gold
                copy of the Aladdin Record.
            corporate_action_workflow_states: Workflow states to filter by.
            start_processing_date: Start processing date (Aladdin Server timezone).
            end_processing_date: End processing date (Aladdin Server timezone).
            start_expiration_date: Start expiration date (Aladdin Server timezone).
            end_expiration_date: End expiration date (Aladdin Server timezone).
            start_payable_date: Start payable date (Aladdin Server timezone).
            end_payable_date: End payable date (Aladdin Server timezone).
            start_modify_time: Start modify time (Aladdin Server timezone).
            end_modify_time: End modify time (Aladdin Server timezone).
            voluntary_mandatory_code: Category filter - Voluntary (V) or
                Mandatory (M).
            portfolio_group_name: Portfolio group containing asset IDs related
                to corporate action events.
            page_token: Page token from a previous FilterCorporateActions call
                for pagination.
            page_size: Maximum number of corporate actions to return.
            corporate_action_view: View of the corporate action resource.
                Valid values: CORPORATE_ACTION_VIEW_UNSPECIFIED,
                CORPORATE_ACTION_VIEW_FULL.
        """
        query: dict[str, Any] = {}
        if ids is not None:
            query["ids"] = ids
        if external_corporate_action_ids is not None:
            query["externalCorporateActionIds"] = external_corporate_action_ids
        if asset_ids is not None:
            query["assetIds"] = asset_ids
        if corporate_action_types is not None:
            query["corporateActionTypes"] = corporate_action_types
        if corporate_action_sub_types is not None:
            query["corporateActionSubTypes"] = corporate_action_sub_types
        if lifecycle_date is not None:
            query["lifecycleDate"] = lifecycle_date
        if corporate_action_data_sources is not None:
            query["corporateActionDataSources"] = corporate_action_data_sources
        if corporate_action_workflow_states is not None:
            query["corporateActionWorkflowStates"] = corporate_action_workflow_states
        if start_processing_date is not None:
            query["startProcessingDate"] = start_processing_date
        if end_processing_date is not None:
            query["endProcessingDate"] = end_processing_date
        if start_expiration_date is not None:
            query["startExpirationDate"] = start_expiration_date
        if end_expiration_date is not None:
            query["endExpirationDate"] = end_expiration_date
        if start_payable_date is not None:
            query["startPayableDate"] = start_payable_date
        if end_payable_date is not None:
            query["endPayableDate"] = end_payable_date
        if start_modify_time is not None:
            query["startModifyTime"] = start_modify_time
        if end_modify_time is not None:
            query["endModifyTime"] = end_modify_time
        if voluntary_mandatory_code is not None:
            query["voluntaryMandatoryCode"] = voluntary_mandatory_code
        if portfolio_group_name is not None:
            query["portfolioGroupName"] = portfolio_group_name

        body: dict[str, Any] = {}
        if query:
            body["corporateActionQuery"] = query
        if page_token is not None:
            body["pageToken"] = page_token
        if page_size is not None:
            body["pageSize"] = page_size
        if corporate_action_view is not None:
            body["corporateActionView"] = corporate_action_view

        return _call_corporate_action_api(
            "/corporateActions:filter",
            http_method="post",
            request_body=body,
        )
