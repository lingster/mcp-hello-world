"""MCP tools for the Aladdin Risk Exception API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_RISK_EXCEPTION_BASE_PATH = "/api/analytics/oversight/governance/v1/"

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
    """Helper to call a Risk Exception API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_RISK_EXCEPTION_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Risk Exception API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_risk_exception_tools(mcp: FastMCP) -> None:
    """Register Aladdin Risk Exception API tools with the MCP server."""

    @mcp.tool()
    def list_risk_exceptions(
        report_time: str | None = None,
        begin_range_date: str | None = None,
        end_range_date: str | None = None,
        read_mask: str | None = None,
        page_token: str | None = None,
        page_size: int | None = None,
        filter: str | None = None,
        order_by: str | None = None,
        facet_fields: list[str] | None = None,
    ) -> str:
        """Lists the latest state of ongoing risk exceptions.

        Retrieve exceptions matching the parameters provided.

        Args:
            report_time: Retrieves exceptions as they appeared at the specified
                         point in time (UTC, date-time). If absent, current UTC
                         server time is used.
            begin_range_date: Retrieves historical exception records with business
                              validity after this date (exclusive, yyyy-MM-dd).
                              Used with end_range_date for time series retrieval.
            end_range_date: Retrieves historical exception records with business
                            validity up to and including this date (inclusive,
                            yyyy-MM-dd). Used with begin_range_date.
            read_mask: Comma-separated field mask to restrict which fields are
                       returned. Field names should be in camelCase.
            page_token: Offset value for pagination into the result set.
            page_size: Number of entries to return (max 1000, default 1000).
            filter: AIP-160 style filter string.
            order_by: Ordering string, e.g. "fieldName:asc" or "fieldName:desc".
            facet_fields: List of field names for facet search.
        """
        params: dict[str, Any] = {}
        if report_time is not None:
            params["reportTime"] = report_time
        if begin_range_date is not None:
            params["beginRangeDate"] = begin_range_date
        if end_range_date is not None:
            params["endRangeDate"] = end_range_date
        if read_mask is not None:
            params["readMask"] = read_mask
        if page_token is not None:
            params["pageToken"] = page_token
        if page_size is not None:
            params["pageSize"] = page_size
        if filter is not None:
            params["filter"] = filter
        if order_by is not None:
            params["orderBy"] = order_by
        if facet_fields is not None:
            params["facetFields"] = facet_fields

        return _call_api("/exceptions", http_method="get", params=params or None)

    @mcp.tool()
    def get_longrunning_operation(operation_id: str) -> str:
        """Get the latest state of a long-running operation for an exception bulk request.

        Args:
            operation_id: The ID of the long-running operation.
        """
        return _call_api(
            f"/exceptions/longrunningoperations/{operation_id}",
            http_method="get",
        )

    @mcp.tool()
    def create_risk_exception(
        as_of_date: str,
        external_id: str,
        scope_id: str,
        scope_type: str,
        entity_id: str,
        entity_type: str,
        rule_id: str,
        rule_version: str,
        valid_begin_date: str | None = None,
        valid_end_date: str | None = None,
        modifier: str | None = None,
        workflow_id: str | None = None,
        scope: str | None = None,
        entity: str | None = None,
        evaluation_state: str | None = None,
        rule_priority: int | None = None,
        exception_tier: str | None = None,
        evaluation_results: list[dict[str, Any]] | None = None,
        exception_details: dict[str, str] | None = None,
    ) -> str:
        """Create, update, or close a risk exception.

        Based on the aggregate Evaluation State of the Exception provided.

        Args:
            as_of_date: Effective date for the exception record (yyyy-MM-dd).
            external_id: Unique user-specified identifier for the exception.
            scope_id: Unique identifier of the scope (e.g. portfolio code).
            scope_type: Scope of the exception: GLOBAL, PORTFOLIO_GROUP,
                        PORTFOLIO, or OTHER.
            entity_id: Unique identifier of the entity (e.g. issuer code).
            entity_type: Type of entity: PORTFOLIO_GROUP, PORTFOLIO, SECTOR,
                         FACTOR, ISSUER, SECURITY, or OTHER.
            rule_id: ID of the Rule the exception is based on.
            rule_version: Version of the Rule the exception is based on.
            valid_begin_date: Date the exception record becomes valid (yyyy-MM-dd).
            valid_end_date: Date the exception record stops being valid (yyyy-MM-dd).
            modifier: Identifier of the modifier of the exception.
            workflow_id: Workflow ID associated with the exception.
            scope: Name of the scope (e.g. portfolio name).
            entity: Name of the entity the exception concerns.
            evaluation_state: Status set by evaluation: BREACH, WARNING, or OK.
            rule_priority: Priority ranking from the rule (integer).
            exception_tier: Visibility tier/level (e.g. Prime/Prod, Beta, Testing).
            evaluation_results: List of condition result dicts from rule evaluation.
            exception_details: Additional key-value details for context.
        """
        body: dict[str, Any] = {
            "externalId": external_id,
            "scopeId": scope_id,
            "scopeType": scope_type,
            "entityId": entity_id,
            "entityType": entity_type,
            "ruleId": rule_id,
            "ruleVersion": rule_version,
        }
        if valid_begin_date is not None:
            body["validBeginDate"] = valid_begin_date
        if valid_end_date is not None:
            body["validEndDate"] = valid_end_date
        if modifier is not None:
            body["modifier"] = modifier
        if workflow_id is not None:
            body["workflowId"] = workflow_id
        if scope is not None:
            body["scope"] = scope
        if entity is not None:
            body["entity"] = entity
        if evaluation_state is not None:
            body["evaluationState"] = evaluation_state
        if rule_priority is not None:
            body["rulePriority"] = rule_priority
        if exception_tier is not None:
            body["exceptionTier"] = exception_tier
        if evaluation_results is not None:
            body["evaluationResults"] = evaluation_results
        if exception_details is not None:
            body["exceptionDetails"] = exception_details

        return _call_api(
            f"/exceptions/{as_of_date}",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def batch_create_risk_exceptions(
        requests: list[dict[str, Any]],
    ) -> str:
        """Bulk create, update, or close risk exceptions.

        Returns a long-running operation. Use get_longrunning_operation to poll
        for completion.

        Args:
            requests: List of exception request dicts. Each dict should contain:
                      - asOfDate (str, required): Effective date (yyyy-MM-dd).
                      - riskException (dict): The risk exception record with fields
                        such as externalId, scopeId, scopeType, entityId, entityType,
                        ruleId, ruleVersion, evaluationState, etc.
        """
        body: dict[str, Any] = {"requests": requests}
        return _call_api("/exceptions:batchCreate", http_method="post", request_body=body)

    @mcp.tool()
    def filter_risk_exceptions(
        report_time: str | None = None,
        begin_range_date: str | None = None,
        end_range_date: str | None = None,
        read_mask: str | None = None,
        filter: str | None = None,
        order_by: str | None = None,
        page_token: str | None = None,
        page_size: int | None = None,
    ) -> str:
        """Retrieve risk exceptions using flexible query-based filtering.

        Args:
            report_time: Retrieves exceptions as they appeared at the specified
                         point in time (UTC, date-time).
            begin_range_date: Historical records with business validity after
                              this date (exclusive, yyyy-MM-dd).
            end_range_date: Historical records with business validity up to and
                            including this date (inclusive, yyyy-MM-dd).
            read_mask: Comma-separated field mask to restrict returned fields
                       (camelCase field names).
            filter: AIP-160 style filter string.
            order_by: Ordering string, e.g. "fieldName:asc" or "fieldName:desc".
            page_token: Token from a previous call for pagination.
            page_size: Number of entries to return (max 1000, default 1000).
        """
        query: dict[str, Any] = {}
        if report_time is not None:
            query["reportTime"] = report_time
        if begin_range_date is not None:
            query["beginRangeDate"] = begin_range_date
        if end_range_date is not None:
            query["endRangeDate"] = end_range_date
        if read_mask is not None:
            query["readMask"] = read_mask
        if filter is not None:
            query["filter"] = filter
        if order_by is not None:
            query["orderBy"] = order_by

        body: dict[str, Any] = {}
        if query:
            body["query"] = query
        if page_token is not None:
            body["pageToken"] = page_token
        if page_size is not None:
            body["pageSize"] = page_size

        return _call_api("/exceptions:filter", http_method="post", request_body=body)

    @mcp.tool()
    def retrieve_risk_exceptions_by_id(
        exception_ids: list[str],
    ) -> str:
        """Bulk retrieve risk exceptions by their unique IDs.

        Designed to complement the more flexible filtering capabilities of the
        list and filter operations.

        Args:
            exception_ids: List of exception ID strings to retrieve.
        """
        body: dict[str, Any] = {"exceptionIds": exception_ids}
        return _call_api(
            "/exceptions:retrieveRiskExceptionsById",
            http_method="post",
            request_body=body,
        )
