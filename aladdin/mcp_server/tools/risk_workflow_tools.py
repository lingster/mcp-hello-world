"""MCP tools for the Aladdin Risk Workflow API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_RISK_WORKFLOW_BASE_PATH = "/api/analytics/oversight/governance/v1/"

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


def _call_risk_workflow_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Risk Workflow API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_RISK_WORKFLOW_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Risk Workflow API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_risk_workflow_tools(mcp: FastMCP) -> None:
    """Register Aladdin Risk Workflow API tools with the MCP server."""

    @mcp.tool()
    def list_risk_workflows(
        workflow_states: list[str] | None = None,
        workflow_ids: list[str] | None = None,
        assignee: str | None = None,
        begin_range_time: str | None = None,
        end_range_time: str | None = None,
        filter: str | None = None,
    ) -> str:
        """Retrieve a list of Workflow items matching the search parameters provided.

        If no workflow states are specified, only items with non-terminal states are
        returned. If terminal states are provided without a begin range time, results
        are restricted to a 45-day lookback period.

        Args:
            workflow_states: List of workflow states to filter by.
            workflow_ids: List of workflow IDs to search for.
            assignee: The user whom a workflow item (task) is assigned to.
            begin_range_time: Start date-time for the search range (RFC 3339 format).
            end_range_time: End date-time for the search range (RFC 3339 format).
            filter: Filter expression for workflow results (AIP-160 syntax).
        """
        params: dict[str, Any] = {}
        if workflow_states is not None:
            params["workflowStates"] = workflow_states
        if workflow_ids is not None:
            params["workflowIds"] = workflow_ids
        if assignee is not None:
            params["assignee"] = assignee
        if begin_range_time is not None:
            params["beginRangeTime"] = begin_range_time
        if end_range_time is not None:
            params["endRangeTime"] = end_range_time
        if filter is not None:
            params["filter"] = filter

        return _call_risk_workflow_api(
            "/workflows",
            http_method="get",
            params=params if params else None,
        )

    @mcp.tool()
    def get_risk_workflow_longrunning_operation(operation_id: str) -> str:
        """Get the latest state of a long-running operation for a workflow bulk request.

        Args:
            operation_id: The ID of the long-running operation.
        """
        return _call_risk_workflow_api(
            f"/workflows/longrunningoperations/{operation_id}",
            http_method="get",
        )

    @mcp.tool()
    def batch_list_risk_workflow_revisions(
        workflow_ids: list[str] | None = None,
        exception_ids: list[str] | None = None,
    ) -> str:
        """Bulk retrieve workflow activity history for multiple workflow IDs or exception IDs.

        Retrieves the history of all activities performed against workflow items or
        all workflows associated with a given set of exceptions over the last 12 months.
        Provide either workflow_ids or exception_ids, not both.

        Args:
            workflow_ids: List of workflow IDs to retrieve history for.
            exception_ids: List of exception IDs to retrieve history for.
        """
        body: dict[str, Any] = {}
        if workflow_ids is not None:
            body["workflowRequest"] = {"ids": workflow_ids}
        if exception_ids is not None:
            body["exceptionRequest"] = {"ids": exception_ids}

        return _call_risk_workflow_api(
            "/workflows/revisions:batchList",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def batch_create_risk_workflows(
        requests: list[dict[str, Any]],
    ) -> str:
        """Bulk create workflow items. For internal use only.

        Each request in the list should contain a riskWorkflow object with the
        required fields: ruleId, scopeId, and scopeType.

        Args:
            requests: List of workflow creation requests. Each dict should have:
                      riskWorkflow (dict) with keys:
                        - ruleId (str, required): The rule ID associated with the workflow.
                        - scopeId (str, required): The scope identifier (e.g. portfolio code).
                        - scopeType (str, required): One of GLOBAL, PORTFOLIO_GROUP, PORTFOLIO, OTHER.
                        - workflowDescription (str, optional): Description for context.
                        - workflowPriority (str, optional): One of RISK_WORKFLOW_PRIORITY_UNSPECIFIED,
                          RISK_WORKFLOW_PRIORITY_HIGH, RISK_WORKFLOW_PRIORITY_MEDIUM, RISK_WORKFLOW_PRIORITY_LOW.
        """
        body: dict[str, Any] = {"requests": requests}
        return _call_risk_workflow_api(
            "/workflows:batchCreate",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def batch_update_risk_workflows(
        requests: list[dict[str, Any]],
    ) -> str:
        """Update selected workflow attributes for a list of workflow items excluding state transitions.

        Example use cases include updating the assignee or adding a comment.

        Args:
            requests: List of update requests. Each dict should have:
                      riskWorkflowActivity (dict) with keys:
                        - id (str, required): The unique activity identifier.
                        - workflowId (str, required): The unique workflow identifier.
                        - workflowAssignee (str, optional): User assigned to the task.
                        - workflowComment (str, optional): A comment placed by a user.
                        - workflowAction (str, optional): The action taken on this item.
                        - workflowResolutionCategoryKey (str, optional): Resolution category key.
                        - workflowResolutionKey (str, optional): Resolution key.
                        - dueDate (str, optional): Due date in RFC 3339 format.
                        - workflowPriority (str, optional): Priority level.
                      updateMask (str, optional): Comma-separated list of fields to update.
        """
        body: dict[str, Any] = {"requests": requests}
        return _call_risk_workflow_api(
            "/workflows:batchUpdate",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def execute_risk_workflow(
        workflow_activity_items: list[dict[str, Any]],
    ) -> str:
        """Transition a list of Workflow items from their current state to a subsequent valid state.

        Args:
            workflow_activity_items: List of workflow activity dicts. Each dict should have:
                                    - id (str, required): The unique activity identifier.
                                    - workflowId (str, required): The unique workflow identifier.
                                    - workflowAssignee (str, optional): User assigned to the task.
                                    - workflowComment (str, optional): A comment placed by a user.
                                    - workflowAction (str, optional): The action to execute.
                                    - workflowResolutionCategoryKey (str, optional): Resolution category key.
                                    - workflowResolutionKey (str, optional): Resolution key.
                                    - dueDate (str, optional): Due date in RFC 3339 format.
                                    - workflowPriority (str, optional): Priority level.
        """
        body: dict[str, Any] = {"workflowActivityItems": workflow_activity_items}
        return _call_risk_workflow_api(
            "/workflows:executeRiskWorkflow",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def list_risk_workflow_revisions(
        workflow_id: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Retrieve the history of all activities performed against a single workflow item.

        Args:
            workflow_id: The ID of the workflow item to retrieve history for.
            page_size: Maximum number of results to return per page.
            page_token: Pagination token for retrieving the next page of results.
        """
        params: dict[str, Any] = {}
        if workflow_id is not None:
            params["id"] = workflow_id
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token is not None:
            params["pageToken"] = page_token

        return _call_risk_workflow_api(
            "/workflows:listRevisions",
            http_method="get",
            params=params if params else None,
        )

    @mcp.tool()
    def retrieve_risk_workflows_by_id(
        workflow_ids: list[str],
    ) -> str:
        """Bulk retrieve Workflow items by their IDs.

        Optimised to retrieve Workflow items in bulk using the natural unique identifier.

        Args:
            workflow_ids: List of workflow IDs to retrieve.
        """
        body: dict[str, Any] = {"workflowIds": workflow_ids}
        return _call_risk_workflow_api(
            "/workflows:retrieveRiskWorkflowsById",
            http_method="post",
            request_body=body,
        )
