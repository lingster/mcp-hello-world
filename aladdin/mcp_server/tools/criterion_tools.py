"""MCP tools for the Aladdin Criterion API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_CRITERION_BASE_PATH = "/api/investment-research/surveillance/criterion/v1/"

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


def _call_criterion_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Criterion API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_CRITERION_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Criterion API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_criterion_tools(mcp: FastMCP) -> None:
    """Register Aladdin Criterion API tools with the MCP server."""

    @mcp.tool()
    def create_criterion(
        criteria: str,
        owner_id: str,
        criterion_type: str | None = None,
        list_id: str | None = None,
        entity_id: dict[str, Any] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        recipients: list[dict[str, Any]] | None = None,
        alert_frequency: int | None = None,
        alert_frequency_unit: str | None = None,
        rolling: bool | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> str:
        """Create a new criterion. Returns AlreadyExists if it already exists.

        Args:
            criteria: The criterion expression string
                      (e.g. "price > 55 AND oas = 75").
            owner_id: The user ID who owns the criterion.
            criterion_type: Type of criterion (e.g. CRITERION_TYPE_UNSPECIFIED).
            list_id: Associated list ID.
            entity_id: Entity identifier dict with optional keys:
                       issuer (str), assetId (str), investmentStrategyId (str).
            start_date: Start date in RFC 3339 / ISO 8601 format.
            end_date: End date in RFC 3339 / ISO 8601 format.
            recipients: List of notification recipients. Each dict has:
                        recipientType (str), recipientValue (str).
            alert_frequency: Frequency value for alerts.
            alert_frequency_unit: Frequency unit (e.g. NOTIFICATION_FREQUENCY_UNSPECIFIED).
            rolling: Whether the criterion is rolling.
            parameters: Arbitrary key/value parameters for the criterion.
        """
        body: dict[str, Any] = {
            "criteria": criteria,
            "ownerId": owner_id,
        }
        if criterion_type is not None:
            body["type"] = criterion_type
        if list_id is not None:
            body["listId"] = list_id
        if entity_id is not None:
            body["entityId"] = entity_id
        if start_date is not None:
            body["startDate"] = start_date
        if end_date is not None:
            body["endDate"] = end_date
        if recipients is not None:
            body["recipients"] = recipients
        if alert_frequency is not None:
            body["alertFrequency"] = alert_frequency
        if alert_frequency_unit is not None:
            body["alertFrequencyUnit"] = alert_frequency_unit
        if rolling is not None:
            body["rolling"] = rolling
        if parameters is not None:
            body["parameters"] = parameters

        return _call_criterion_api("/criteria", http_method="post", request_body=body)

    @mcp.tool()
    def get_criterion(criterion_id: str) -> str:
        """Retrieve a criterion by its ID.

        Args:
            criterion_id: The unique ID of the criterion to retrieve.
        """
        return _call_criterion_api(
            f"/criteria/{criterion_id}",
            http_method="get",
        )

    @mcp.tool()
    def delete_criterion(criterion_id: str) -> str:
        """Delete a criterion. Returns NotFound if not present.

        Args:
            criterion_id: The unique ID of the criterion to delete.
        """
        return _call_criterion_api(
            f"/criteria/{criterion_id}",
            http_method="delete",
        )

    @mcp.tool()
    def update_criterion(
        criterion_id: str,
        criteria: str | None = None,
        owner_id: str | None = None,
        criterion_type: str | None = None,
        list_id: str | None = None,
        entity_id: dict[str, Any] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        recipients: list[dict[str, Any]] | None = None,
        alert_frequency: int | None = None,
        alert_frequency_unit: str | None = None,
        rolling: bool | None = None,
        parameters: dict[str, Any] | None = None,
        update_mask: str | None = None,
    ) -> str:
        """Update an existing criterion. Returns NotFound if not present.

        Only the fields provided will be updated. Use update_mask to specify
        exactly which fields to update.

        Args:
            criterion_id: The unique ID of the criterion to update.
            criteria: The criterion expression string.
            owner_id: New owner user ID.
            criterion_type: Type of criterion.
            list_id: Associated list ID.
            entity_id: Entity identifier dict with optional keys:
                       issuer (str), assetId (str), investmentStrategyId (str).
            start_date: Start date in RFC 3339 / ISO 8601 format.
            end_date: End date in RFC 3339 / ISO 8601 format.
            recipients: List of notification recipients. Each dict has:
                        recipientType (str), recipientValue (str).
            alert_frequency: Frequency value for alerts.
            alert_frequency_unit: Frequency unit.
            rolling: Whether the criterion is rolling.
            parameters: Arbitrary key/value parameters for the criterion.
            update_mask: Comma-separated list of fields to update
                         (e.g. "criteria,ownerId").
        """
        body: dict[str, Any] = {"id": criterion_id}
        if criteria is not None:
            body["criteria"] = criteria
        if owner_id is not None:
            body["ownerId"] = owner_id
        if criterion_type is not None:
            body["type"] = criterion_type
        if list_id is not None:
            body["listId"] = list_id
        if entity_id is not None:
            body["entityId"] = entity_id
        if start_date is not None:
            body["startDate"] = start_date
        if end_date is not None:
            body["endDate"] = end_date
        if recipients is not None:
            body["recipients"] = recipients
        if alert_frequency is not None:
            body["alertFrequency"] = alert_frequency
        if alert_frequency_unit is not None:
            body["alertFrequencyUnit"] = alert_frequency_unit
        if rolling is not None:
            body["rolling"] = rolling
        if parameters is not None:
            body["parameters"] = parameters

        query_params: dict[str, Any] | None = None
        if update_mask is not None:
            query_params = {"updateMask": update_mask}

        return _call_criterion_api(
            f"/criteria/{criterion_id}",
            http_method="patch",
            request_body=body,
            params=query_params,
        )

    @mcp.tool()
    def batch_delete_criteria(
        criterion_ids: list[str] | None = None,
        types: list[str] | None = None,
        list_ids: list[str] | None = None,
        owner_ids: list[str] | None = None,
        entity_ids: list[dict[str, Any]] | None = None,
    ) -> str:
        """Batch delete criteria for given conditions.

        Provide one or more filter parameters to identify which criteria to
        delete in bulk.

        Args:
            criterion_ids: List of criterion IDs to delete.
            types: List of criterion types to delete.
            list_ids: List of list IDs whose criteria should be deleted.
            owner_ids: List of owner user IDs whose criteria should be deleted.
            entity_ids: List of entity ID dicts to delete criteria for.
                        Each dict can have: issuer (str), assetId (str),
                        investmentStrategyId (str).
        """
        body: dict[str, Any] = {}
        if criterion_ids is not None:
            body["criterionIds"] = criterion_ids
        if types is not None:
            body["types"] = types
        if list_ids is not None:
            body["listIds"] = list_ids
        if owner_ids is not None:
            body["ownerIds"] = owner_ids
        if entity_ids is not None:
            body["entityIds"] = entity_ids

        return _call_criterion_api("/criteria:batchDelete", http_method="post", request_body=body)

    @mcp.tool()
    def evaluate_criteria(
        entity_ids: list[dict[str, Any]],
        criteria: str,
        types: list[str] | None = None,
        frequency: str | None = None,
        last_execution_time: str | None = None,
        current_execution_time: str | None = None,
    ) -> str:
        """Evaluate ad hoc criteria against a set of entities.

        Given a criteria expression string and entity IDs, evaluates the
        criteria and returns a mapping of entity IDs to results (true/false).

        Example: Evaluate "((price > 55 OR oas = 75) AND market_cap < 1mm)
        OR msci_social_score > 5.0" on some cusips.

        Args:
            entity_ids: List of entity ID dicts to evaluate against.
                        Each dict can have: issuer (str), assetId (str),
                        investmentStrategyId (str).
            criteria: The criteria expression string to evaluate.
            types: List of criterion types for the evaluation.
            frequency: Notification frequency
                       (e.g. NOTIFICATION_FREQUENCY_UNSPECIFIED).
            last_execution_time: Last execution timestamp in RFC 3339 format.
            current_execution_time: Current execution timestamp in RFC 3339 format.
        """
        body: dict[str, Any] = {
            "entityIds": entity_ids,
            "criteria": criteria,
        }
        if types is not None:
            body["types"] = types
        if frequency is not None:
            body["frequency"] = frequency
        if last_execution_time is not None:
            body["lastExecutionTime"] = last_execution_time
        if current_execution_time is not None:
            body["currentExecutionTime"] = current_execution_time

        return _call_criterion_api("/criteria:evaluate", http_method="post", request_body=body)

    @mcp.tool()
    def filter_criteria_by_user(
        owner_id: str,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Retrieve all criteria owned by a specific user.

        Args:
            owner_id: The user ID to filter criteria by.
            page_size: Maximum number of criteria to return per page.
            page_token: Token for retrieving the next page of results.
        """
        body: dict[str, Any] = {"ownerId": owner_id}
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_criterion_api("/criteria:filterByUser", http_method="post", request_body=body)

    @mcp.tool()
    def run_criteria(
        ids: list[str] | None = None,
        types: list[str] | None = None,
        list_ids: list[str] | None = None,
        owners: list[str] | None = None,
        frequency: str | None = None,
        last_execution_time: str | None = None,
        current_execution_time: str | None = None,
    ) -> str:
        """Run stored criteria in bulk.

        Evaluates stored criteria based on any combination of criterion IDs,
        types, owners, etc. Returns a mapping of criterion IDs to evaluation
        results (true/false).

        Args:
            ids: List of criterion IDs to run.
            types: List of criterion types to run.
            list_ids: List of list IDs whose criteria should be run.
            owners: List of owner user IDs whose criteria should be run.
            frequency: Notification frequency
                       (e.g. NOTIFICATION_FREQUENCY_UNSPECIFIED).
            last_execution_time: Last execution timestamp in RFC 3339 format.
            current_execution_time: Current execution timestamp in RFC 3339 format.
        """
        body: dict[str, Any] = {}
        if ids is not None:
            body["ids"] = ids
        if types is not None:
            body["types"] = types
        if list_ids is not None:
            body["listIds"] = list_ids
        if owners is not None:
            body["owners"] = owners
        if frequency is not None:
            body["frequency"] = frequency
        if last_execution_time is not None:
            body["lastExecutionTime"] = last_execution_time
        if current_execution_time is not None:
            body["currentExecutionTime"] = current_execution_time

        return _call_criterion_api("/criteria:run", http_method="post", request_body=body)

    @mcp.tool()
    def search_criteria(
        filter_criteria: list[str] | None = None,
        order_by: str | None = None,
        page_size: int | None = None,
        page_number: int | None = None,
    ) -> str:
        """Search criteria by filter conditions.

        Filter syntax supports AND/OR logic operators to combine multiple
        criteria conditions.

        Args:
            filter_criteria: List of filter strings. Multiple criteria can be
                             joined by AND and OR logic operators.
            order_by: Sort order string with ascending or descending order
                      based on a specific field (default ascending).
            page_size: Maximum number of criteria to return per page.
            page_number: Page number for pagination.
        """
        body: dict[str, Any] = {}
        if filter_criteria is not None:
            body["filterCriteria"] = filter_criteria
        if order_by is not None:
            body["orderBy"] = order_by
        if page_size is not None:
            body["pageSize"] = page_size
        if page_number is not None:
            body["pageNumber"] = page_number

        return _call_criterion_api("/criteria:search", http_method="post", request_body=body)
