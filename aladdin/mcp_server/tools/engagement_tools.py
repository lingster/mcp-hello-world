"""MCP tools for the Aladdin Engagement API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_ENGAGEMENT_BASE_PATH = "/api/investment-research/content/engagement/v1/"

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


def _call_engagement_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call an Engagement API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_ENGAGEMENT_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Engagement API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def _build_entity_id(entity: dict[str, Any]) -> dict[str, Any]:
    """Normalize an entity ID dict, filtering out None values."""
    cleaned: dict[str, Any] = {}
    for key in ("issuer", "assetId", "investmentStrategyId"):
        if entity.get(key):
            cleaned[key] = entity[key]
    return cleaned


def _build_topics_data(topics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize topics data dicts, filtering out None values."""
    cleaned: list[dict[str, Any]] = []
    for topic in topics:
        entry: dict[str, Any] = {}
        for key in (
            "engagementTopic",
            "engagementMomentum",
            "engagementKpi",
            "timeFrame",
            "customTopicFields",
        ):
            if topic.get(key) is not None:
                entry[key] = topic[key]
        cleaned.append(entry)
    return cleaned


def register_engagement_tools(mcp: FastMCP) -> None:
    """Register Aladdin Engagement API tools with the MCP server."""

    @mcp.tool()
    def create_engagement(
        subject: str,
        author: str,
        entity: dict[str, Any] | None = None,
        creator: str | None = None,
        selected_permission_groups: list[str] | None = None,
        expiring_permission_groups: list[dict[str, Any]] | None = None,
        tags: list[str] | None = None,
        internal_attendees: list[str] | None = None,
        external_attendees: list[str] | None = None,
        category: str | None = None,
        engagement_format: str | None = None,
        engagement_initiator: str | None = None,
        engagement_types: list[str] | None = None,
        engagement_momentum: str | None = None,
        engagement_date: str | None = None,
        engagement_topics: list[dict[str, Any]] | None = None,
        internal_note: str | None = None,
        client_note: str | None = None,
        template_name: str | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> str:
        """Create a new engagement.

        Args:
            subject: The subject (title) of the engagement.
            author: The author of the engagement.
            entity: Entity ID dict with optional keys: issuer, assetId, investmentStrategyId.
            creator: The creator of the engagement.
            selected_permission_groups: List of permission group names.
            expiring_permission_groups: List of expiring permission groups, each with
                                        permissionGroup (str), timeUnit (str), timeSpan (int).
            tags: List of tags for the engagement.
            internal_attendees: List of internal attendee identifiers.
            external_attendees: List of external attendee identifiers.
            category: The engagement category.
            engagement_format: The format of the engagement.
            engagement_initiator: Who initiated the engagement.
            engagement_types: List of engagement type strings.
            engagement_momentum: The momentum of the engagement.
            engagement_date: Engagement date in YYYY-MM-DD format.
            engagement_topics: List of topic dicts with keys: engagementTopic, engagementMomentum,
                               engagementKpi, timeFrame, customTopicFields.
            internal_note: Internal note text.
            client_note: Client-facing note text.
            template_name: Name of the engagement template.
            custom_fields: Dictionary of custom field key-value pairs.
        """
        body: dict[str, Any] = {
            "subject": subject,
            "author": author,
        }
        if entity is not None:
            body["entity"] = _build_entity_id(entity)
        if creator is not None:
            body["creator"] = creator
        if selected_permission_groups is not None:
            body["selectedPermissionGroups"] = selected_permission_groups
        if expiring_permission_groups is not None:
            body["expiringPermissionGroups"] = expiring_permission_groups
        if tags is not None:
            body["tags"] = tags
        if internal_attendees is not None:
            body["internalAttendees"] = internal_attendees
        if external_attendees is not None:
            body["externalAttendees"] = external_attendees
        if category is not None:
            body["category"] = category
        if engagement_format is not None:
            body["engagementFormat"] = engagement_format
        if engagement_initiator is not None:
            body["engagementInitiator"] = engagement_initiator
        if engagement_types is not None:
            body["engagementTypes"] = engagement_types
        if engagement_momentum is not None:
            body["engagementMomentum"] = engagement_momentum
        if engagement_date is not None:
            body["engagementDate"] = engagement_date
        if engagement_topics is not None:
            body["engagementTopics"] = _build_topics_data(engagement_topics)
        if internal_note is not None:
            body["internalNote"] = internal_note
        if client_note is not None:
            body["clientNote"] = client_note
        if template_name is not None:
            body["templateName"] = template_name
        if custom_fields is not None:
            body["customFields"] = custom_fields

        return _call_engagement_api("/engagement", http_method="post", request_body=body)

    @mcp.tool()
    def update_engagement(
        engagement_id: str,
        subject: str | None = None,
        author: str | None = None,
        entity: dict[str, Any] | None = None,
        creator: str | None = None,
        selected_permission_groups: list[str] | None = None,
        expiring_permission_groups: list[dict[str, Any]] | None = None,
        tags: list[str] | None = None,
        internal_attendees: list[str] | None = None,
        external_attendees: list[str] | None = None,
        category: str | None = None,
        engagement_format: str | None = None,
        engagement_initiator: str | None = None,
        engagement_types: list[str] | None = None,
        engagement_momentum: str | None = None,
        engagement_date: str | None = None,
        engagement_topics: list[dict[str, Any]] | None = None,
        internal_note: str | None = None,
        client_note: str | None = None,
        template_name: str | None = None,
        custom_fields: dict[str, Any] | None = None,
        update_mask: str | None = None,
    ) -> str:
        """Update an existing engagement.

        Only the fields provided will be updated. Use update_mask to specify
        exactly which fields to update.

        Args:
            engagement_id: The unique ID of the engagement to update.
            subject: New subject (title) for the engagement.
            author: New author for the engagement.
            entity: Entity ID dict with optional keys: issuer, assetId, investmentStrategyId.
            creator: New creator for the engagement.
            selected_permission_groups: List of permission group names.
            expiring_permission_groups: List of expiring permission groups, each with
                                        permissionGroup (str), timeUnit (str), timeSpan (int).
            tags: List of tags for the engagement.
            internal_attendees: List of internal attendee identifiers.
            external_attendees: List of external attendee identifiers.
            category: The engagement category.
            engagement_format: The format of the engagement.
            engagement_initiator: Who initiated the engagement.
            engagement_types: List of engagement type strings.
            engagement_momentum: The momentum of the engagement.
            engagement_date: Engagement date in YYYY-MM-DD format.
            engagement_topics: List of topic dicts with keys: engagementTopic, engagementMomentum,
                               engagementKpi, timeFrame, customTopicFields.
            internal_note: Internal note text.
            client_note: Client-facing note text.
            template_name: Name of the engagement template.
            custom_fields: Dictionary of custom field key-value pairs.
            update_mask: Comma-separated list of fields to update (e.g. "subject,author").
        """
        body: dict[str, Any] = {"id": engagement_id}
        if subject is not None:
            body["subject"] = subject
        if author is not None:
            body["author"] = author
        if entity is not None:
            body["entity"] = _build_entity_id(entity)
        if creator is not None:
            body["creator"] = creator
        if selected_permission_groups is not None:
            body["selectedPermissionGroups"] = selected_permission_groups
        if expiring_permission_groups is not None:
            body["expiringPermissionGroups"] = expiring_permission_groups
        if tags is not None:
            body["tags"] = tags
        if internal_attendees is not None:
            body["internalAttendees"] = internal_attendees
        if external_attendees is not None:
            body["externalAttendees"] = external_attendees
        if category is not None:
            body["category"] = category
        if engagement_format is not None:
            body["engagementFormat"] = engagement_format
        if engagement_initiator is not None:
            body["engagementInitiator"] = engagement_initiator
        if engagement_types is not None:
            body["engagementTypes"] = engagement_types
        if engagement_momentum is not None:
            body["engagementMomentum"] = engagement_momentum
        if engagement_date is not None:
            body["engagementDate"] = engagement_date
        if engagement_topics is not None:
            body["engagementTopics"] = _build_topics_data(engagement_topics)
        if internal_note is not None:
            body["internalNote"] = internal_note
        if client_note is not None:
            body["clientNote"] = client_note
        if template_name is not None:
            body["templateName"] = template_name
        if custom_fields is not None:
            body["customFields"] = custom_fields

        params: dict[str, Any] | None = None
        if update_mask is not None:
            params = {"updateMask": update_mask}

        return _call_engagement_api(
            f"/engagement/{engagement_id}",
            http_method="patch",
            request_body=body,
            params=params,
        )

    @mcp.tool()
    def delete_engagement(engagement_id: str) -> str:
        """Delete an engagement by its ID.

        Args:
            engagement_id: The unique ID of the engagement to delete.
        """
        return _call_engagement_api(
            f"/engagement/{engagement_id}",
            http_method="delete",
        )

    @mcp.tool()
    def search_engagements(
        as_of_date: str | None = None,
        entity_ids: list[dict[str, Any]] | None = None,
        filter_criteria: list[str] | None = None,
        order_by: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Search engagements by criteria.

        Args:
            as_of_date: As-of date for the search in YYYY-MM-DD format.
            entity_ids: List of entity ID dicts to filter by. Each dict can have:
                        issuer (str), assetId (str), investmentStrategyId (str).
            filter_criteria: List of filter strings.
            order_by: Sort order string.
            page_size: Maximum number of engagements to return.
            page_token: Page token from a previous search call for pagination.
        """
        body: dict[str, Any] = {}
        if as_of_date is not None:
            body["asOfDate"] = as_of_date
        if entity_ids is not None:
            body["entityIds"] = [_build_entity_id(e) for e in entity_ids]
        if filter_criteria is not None:
            body["filterCriteria"] = filter_criteria
        if order_by is not None:
            body["orderBy"] = order_by
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_engagement_api("/engagements:search", http_method="post", request_body=body)

    @mcp.tool()
    def search_draft_engagements(
        entity_ids: list[dict[str, Any]] | None = None,
        filter_criteria: list[str] | None = None,
        order_by: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Search draft engagements by criteria.

        Args:
            entity_ids: List of entity ID dicts to filter by. Each dict can have:
                        issuer (str), assetId (str), investmentStrategyId (str).
            filter_criteria: List of filter strings.
            order_by: Sort order string.
            page_size: Maximum number of draft engagements to return.
            page_token: Page token from a previous search call for pagination.
        """
        body: dict[str, Any] = {}
        if entity_ids is not None:
            body["entityIds"] = [_build_entity_id(e) for e in entity_ids]
        if filter_criteria is not None:
            body["filterCriteria"] = filter_criteria
        if order_by is not None:
            body["orderBy"] = order_by
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_engagement_api(
            "/draftEngagements:search", http_method="post", request_body=body
        )

    @mcp.tool()
    def search_historical_engagements(
        engagement_date_range: dict[str, str] | None = None,
        entity_ids: list[dict[str, Any]] | None = None,
        filter_criteria: list[str] | None = None,
        order_by: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Search historical engagements by criteria including date range.

        Args:
            engagement_date_range: Date range dict with startDate and endDate in YYYY-MM-DD format.
                                   Example: {"startDate": "2024-01-01", "endDate": "2024-12-31"}.
            entity_ids: List of entity ID dicts to filter by. Each dict can have:
                        issuer (str), assetId (str), investmentStrategyId (str).
            filter_criteria: List of filter strings.
            order_by: Sort order string.
            page_size: Maximum number of historical engagements to return.
            page_token: Page token from a previous search call for pagination.
        """
        body: dict[str, Any] = {}
        if engagement_date_range is not None:
            body["engagementDateRange"] = engagement_date_range
        if entity_ids is not None:
            body["entityIds"] = [_build_entity_id(e) for e in entity_ids]
        if filter_criteria is not None:
            body["filterCriteria"] = filter_criteria
        if order_by is not None:
            body["orderBy"] = order_by
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_engagement_api(
            "/historicalEngagements:search", http_method="post", request_body=body
        )
