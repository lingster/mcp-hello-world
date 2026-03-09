"""MCP tools for the Aladdin Studio Subscription API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_STUDIO_SUBSCRIPTION_BASE_PATH = "/api/platform/studio/studio-notification/v1/"

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
    """Helper to call a Studio Subscription API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_STUDIO_SUBSCRIPTION_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Studio Subscription API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_studio_subscription_tools(mcp: FastMCP) -> None:
    """Register Aladdin Studio Subscription API tools with the MCP server."""

    @mcp.tool()
    def create_studio_subscription(
        user: str,
        notification_event_type: str,
        event_name: str = "",
        entity_type: str = "",
        entity_name: str = "",
        notification_action: str = "STUDIO_NOTIFICATION_ACTION_UNSPECIFIED",
        email: str = "",
    ) -> str:
        """Create a new Studio notification subscription.

        Args:
            user: The user ID for the subscription owner.
            notification_event_type: Type of notification event. One of:
                STUDIO_NOTIFICATION_EVENT_TYPE_UNSPECIFIED,
                STUDIO_NOTIFICATION_EVENT_TYPE_ACM,
                STUDIO_NOTIFICATION_EVENT_TYPE_COMPUTE,
                STUDIO_NOTIFICATION_EVENT_TYPE_API,
                STUDIO_NOTIFICATION_EVENT_TYPE_SPACE,
                STUDIO_NOTIFICATION_EVENT_TYPE_PROJECT.
            event_name: Name of the specific event to subscribe to.
            entity_type: Type of Studio entity. One of:
                STUDIO_ENTITY_TYPE_UNSPECIFIED,
                STUDIO_ENTITY_TYPE_USER,
                STUDIO_ENTITY_TYPE_PROJECT,
                STUDIO_ENTITY_TYPE_SPACE.
            entity_name: Name of the Studio entity to scope the subscription to.
            notification_action: Delivery action for the notification. One of:
                STUDIO_NOTIFICATION_ACTION_UNSPECIFIED,
                STUDIO_NOTIFICATION_ACTION_SMTP,
                STUDIO_NOTIFICATION_ACTION_PUSH.
            email: Email address for SMTP notifications.
        """
        body: dict[str, Any] = {
            "user": user,
            "studioNotificationEvent": {
                "studioNotificationEventType": notification_event_type,
            },
            "studioNotificationAction": notification_action,
        }
        if event_name:
            body["studioNotificationEvent"]["eventName"] = event_name
        if entity_type or entity_name:
            scope: dict[str, Any] = {}
            if entity_type:
                scope["studioEntityType"] = entity_type
            if entity_name:
                scope["studioEntityName"] = entity_name
            body["studioNotificationScope"] = scope
        if email:
            body["email"] = email

        return _call_api("/studioSubscriptions", http_method="post", request_body=body)

    @mcp.tool()
    def get_studio_subscription(subscription_id: str) -> str:
        """Retrieve a Studio subscription by its ID.

        Args:
            subscription_id: The unique ID of the subscription to retrieve.
        """
        return _call_api(
            f"/studioSubscriptions/{subscription_id}",
            http_method="get",
        )

    @mcp.tool()
    def delete_studio_subscription(subscription_id: str) -> str:
        """Delete a Studio subscription.

        Args:
            subscription_id: The unique ID of the subscription to delete.
        """
        return _call_api(
            f"/studioSubscriptions/{subscription_id}",
            http_method="delete",
        )

    @mcp.tool()
    def update_studio_subscription(
        subscription_id: str,
        user: str | None = None,
        notification_event_type: str | None = None,
        event_name: str | None = None,
        entity_type: str | None = None,
        entity_name: str | None = None,
        notification_action: str | None = None,
        email: str | None = None,
        update_mask: str | None = None,
    ) -> str:
        """Update an existing Studio subscription.

        Only the fields provided will be updated. Use update_mask to specify
        exactly which fields to update.

        Args:
            subscription_id: The unique ID of the subscription to update.
            user: The user ID for the subscription owner.
            notification_event_type: Type of notification event. One of:
                STUDIO_NOTIFICATION_EVENT_TYPE_UNSPECIFIED,
                STUDIO_NOTIFICATION_EVENT_TYPE_ACM,
                STUDIO_NOTIFICATION_EVENT_TYPE_COMPUTE,
                STUDIO_NOTIFICATION_EVENT_TYPE_API,
                STUDIO_NOTIFICATION_EVENT_TYPE_SPACE,
                STUDIO_NOTIFICATION_EVENT_TYPE_PROJECT.
            event_name: Name of the specific event.
            entity_type: Type of Studio entity. One of:
                STUDIO_ENTITY_TYPE_UNSPECIFIED,
                STUDIO_ENTITY_TYPE_USER,
                STUDIO_ENTITY_TYPE_PROJECT,
                STUDIO_ENTITY_TYPE_SPACE.
            entity_name: Name of the Studio entity.
            notification_action: Delivery action. One of:
                STUDIO_NOTIFICATION_ACTION_UNSPECIFIED,
                STUDIO_NOTIFICATION_ACTION_SMTP,
                STUDIO_NOTIFICATION_ACTION_PUSH.
            email: Email address for SMTP notifications.
            update_mask: Comma-separated list of fields to update
                (e.g. "user,email,studioNotificationAction").
        """
        body: dict[str, Any] = {"id": subscription_id}
        if user is not None:
            body["user"] = user
        if notification_event_type is not None or event_name is not None:
            event: dict[str, Any] = {}
            if notification_event_type is not None:
                event["studioNotificationEventType"] = notification_event_type
            if event_name is not None:
                event["eventName"] = event_name
            body["studioNotificationEvent"] = event
        if entity_type is not None or entity_name is not None:
            scope: dict[str, Any] = {}
            if entity_type is not None:
                scope["studioEntityType"] = entity_type
            if entity_name is not None:
                scope["studioEntityName"] = entity_name
            body["studioNotificationScope"] = scope
        if notification_action is not None:
            body["studioNotificationAction"] = notification_action
        if email is not None:
            body["email"] = email

        params: dict[str, Any] | None = None
        if update_mask is not None:
            params = {"updateMask": update_mask}

        return _call_api(
            f"/studioSubscriptions/{subscription_id}",
            http_method="patch",
            request_body=body,
            params=params,
        )

    @mcp.tool()
    def batch_create_studio_subscriptions(
        subscriptions: list[dict[str, Any]],
    ) -> str:
        """Create a batch of Studio notification subscriptions.

        Args:
            subscriptions: List of subscription dicts. Each dict should contain
                a "studioSubscription" key with subscription details including:
                user (str), studioNotificationEvent (dict with
                studioNotificationEventType, eventName),
                studioNotificationScope (dict with studioEntityType, studioEntityName),
                studioNotificationAction (str), email (str).
        """
        body: dict[str, Any] = {
            "requests": [{"studioSubscription": sub} for sub in subscriptions],
        }
        return _call_api("/studioSubscriptions:batchCreate", http_method="post", request_body=body)

    @mcp.tool()
    def filter_studio_subscriptions(
        entity_type: str | None = None,
        entity_name: str | None = None,
        notification_event_type: str | None = None,
        notification_event_name: str | None = None,
        user_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page_token: str | None = None,
        page_size: int | None = None,
    ) -> str:
        """Filter Studio subscriptions by event details, entity, user, or date range.

        Args:
            entity_type: Filter by Studio entity type. One of:
                STUDIO_ENTITY_TYPE_UNSPECIFIED,
                STUDIO_ENTITY_TYPE_USER,
                STUDIO_ENTITY_TYPE_PROJECT,
                STUDIO_ENTITY_TYPE_SPACE.
            entity_name: Filter by Studio entity name.
            notification_event_type: Filter by notification event type. One of:
                STUDIO_NOTIFICATION_EVENT_TYPE_UNSPECIFIED,
                STUDIO_NOTIFICATION_EVENT_TYPE_ACM,
                STUDIO_NOTIFICATION_EVENT_TYPE_COMPUTE,
                STUDIO_NOTIFICATION_EVENT_TYPE_API,
                STUDIO_NOTIFICATION_EVENT_TYPE_SPACE,
                STUDIO_NOTIFICATION_EVENT_TYPE_PROJECT.
            notification_event_name: Filter by notification event name.
            user_id: Filter by user ID.
            start_date: Start date for date range filter (ISO format).
            end_date: End date for date range filter (ISO format).
            page_token: Token for pagination (from previous response).
            page_size: Maximum number of results per page.
        """
        query: dict[str, Any] = {}
        if entity_type is not None:
            query["studioEntityType"] = entity_type
        if entity_name is not None:
            query["studioEntityName"] = entity_name
        if notification_event_type is not None:
            query["studioNotificationEventType"] = notification_event_type
        if notification_event_name is not None:
            query["studioNotificationEventName"] = notification_event_name
        if user_id is not None:
            query["userId"] = user_id
        if start_date is not None or end_date is not None:
            date_filter: dict[str, Any] = {}
            if start_date is not None:
                date_filter["startDate"] = start_date
            if end_date is not None:
                date_filter["endDate"] = end_date
            query["dateRangeFilter"] = date_filter

        body: dict[str, Any] = {}
        if query:
            body["query"] = query
        if page_token is not None:
            body["pageToken"] = page_token
        if page_size is not None:
            body["pageSize"] = page_size

        return _call_api("/studioSubscriptions:filter", http_method="post", request_body=body)
