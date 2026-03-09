"""MCP tools for the Aladdin Studio Notification API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_STUDIO_NOTIFICATION_BASE_PATH = "/api/platform/studio/studio-notification/v1/"

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
    """Helper to call a Studio Notification API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_STUDIO_NOTIFICATION_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Studio Notification API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def _build_notification_dict(
    sender: str | None = None,
    notification_subject: str | None = None,
    notification_message: str | None = None,
    event_type: str | None = None,
    event_name: str | None = None,
    scope_entity_type: str | None = None,
    scope_entity_name: str | None = None,
    notification_metadata: dict[str, Any] | None = None,
    recipient_scopes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a StudioNotification dict, filtering out None values."""
    notification: dict[str, Any] = {}

    if sender is not None:
        notification["sender"] = sender
    if notification_subject is not None:
        notification["notificationSubject"] = notification_subject
    if notification_message is not None:
        notification["notificationMessage"] = notification_message
    if notification_metadata is not None:
        notification["notificationMetadata"] = notification_metadata

    if event_type is not None or event_name is not None:
        event: dict[str, Any] = {}
        if event_type is not None:
            event["studioNotificationEventType"] = event_type
        if event_name is not None:
            event["eventName"] = event_name
        notification["studioNotificationEvent"] = event

    if scope_entity_type is not None or scope_entity_name is not None:
        scope: dict[str, Any] = {}
        if scope_entity_type is not None:
            scope["studioEntityType"] = scope_entity_type
        if scope_entity_name is not None:
            scope["studioEntityName"] = scope_entity_name
        notification["studioNotificationScope"] = scope

    if recipient_scopes is not None:
        cleaned: list[dict[str, Any]] = []
        for rs in recipient_scopes:
            entry: dict[str, Any] = {}
            if rs.get("studioRecipientId"):
                entry["studioRecipientId"] = rs["studioRecipientId"]
            if rs.get("studioRecipientType"):
                entry["studioRecipientType"] = rs["studioRecipientType"]
            if rs.get("studioRecipientAccessType"):
                entry["studioRecipientAccessType"] = rs["studioRecipientAccessType"]
            cleaned.append(entry)
        notification["studioRecipientScopes"] = cleaned

    return notification


def register_studio_notification_tools(mcp: FastMCP) -> None:
    """Register Aladdin Studio Notification API tools with the MCP server."""

    @mcp.tool()
    def create_studio_notification(
        sender: str,
        notification_subject: str,
        notification_message: str,
        event_type: str = "STUDIO_NOTIFICATION_EVENT_TYPE_UNSPECIFIED",
        event_name: str | None = None,
        scope_entity_type: str = "STUDIO_ENTITY_TYPE_UNSPECIFIED",
        scope_entity_name: str | None = None,
        notification_metadata: dict[str, Any] | None = None,
        recipient_scopes: list[dict[str, Any]] | None = None,
    ) -> str:
        """Create a Studio notification to be sent to subscribers.

        Args:
            sender: The sender of the notification.
            notification_subject: The subject line of the notification.
            notification_message: The body message of the notification.
            event_type: The notification event type. One of:
                        STUDIO_NOTIFICATION_EVENT_TYPE_UNSPECIFIED,
                        STUDIO_NOTIFICATION_EVENT_TYPE_ACM,
                        STUDIO_NOTIFICATION_EVENT_TYPE_COMPUTE,
                        STUDIO_NOTIFICATION_EVENT_TYPE_API,
                        STUDIO_NOTIFICATION_EVENT_TYPE_SPACE,
                        STUDIO_NOTIFICATION_EVENT_TYPE_PROJECT.
            event_name: A descriptive name for the event.
            scope_entity_type: The entity type scope. One of:
                               STUDIO_ENTITY_TYPE_UNSPECIFIED,
                               STUDIO_ENTITY_TYPE_USER,
                               STUDIO_ENTITY_TYPE_PROJECT,
                               STUDIO_ENTITY_TYPE_SPACE.
            scope_entity_name: The name of the scoped entity.
            notification_metadata: Arbitrary key-value metadata for the notification.
            recipient_scopes: List of recipient scope dicts. Each dict can have:
                              studioRecipientId (str), studioRecipientType (str:
                              STUDIO_RECIPIENT_TYPE_UNSPECIFIED|STUDIO_RECIPIENT_TYPE_USER|
                              STUDIO_RECIPIENT_TYPE_EMAIL|STUDIO_RECIPIENT_TYPE_PROJECT|
                              STUDIO_RECIPIENT_TYPE_SPACE|STUDIO_RECIPIENT_TYPE_PERM),
                              studioRecipientAccessType (str).
        """
        notification = _build_notification_dict(
            sender=sender,
            notification_subject=notification_subject,
            notification_message=notification_message,
            event_type=event_type,
            event_name=event_name,
            scope_entity_type=scope_entity_type,
            scope_entity_name=scope_entity_name,
            notification_metadata=notification_metadata,
            recipient_scopes=recipient_scopes,
        )
        body: dict[str, Any] = {"studioNotification": notification}
        return _call_api("/studioNotifications", http_method="post", request_body=body)

    @mcp.tool()
    def get_studio_notification(notification_id: str) -> str:
        """Retrieve a Studio notification by its ID.

        Args:
            notification_id: The unique ID of the studio notification to retrieve.
        """
        return _call_api(
            f"/studioNotifications/{notification_id}",
            http_method="get",
        )

    @mcp.tool()
    def batch_create_studio_notifications(
        notifications: list[dict[str, Any]],
    ) -> str:
        """Create a batch of Studio notifications (max 100 at a time).

        Args:
            notifications: List of notification dicts. Each dict can have:
                           sender (str), notificationSubject (str),
                           notificationMessage (str),
                           studioNotificationEvent (dict with studioNotificationEventType, eventName),
                           studioNotificationScope (dict with studioEntityType, studioEntityName),
                           notificationMetadata (dict), studioRecipientScopes (list of dicts).
        """
        requests: list[dict[str, Any]] = []
        for notif in notifications:
            requests.append({"studioNotification": notif})
        body: dict[str, Any] = {"requests": requests}
        return _call_api("/studioNotifications:batchCreate", http_method="post", request_body=body)

    @mcp.tool()
    def filter_studio_notifications(
        studio_entity_type: str | None = None,
        studio_entity_name: str | None = None,
        studio_notification_event_type: str | None = None,
        studio_notification_event_name: str | None = None,
        user_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page_token: str | None = None,
        page_size: int | None = None,
    ) -> str:
        """Filter Studio notifications by event details, entity, user, or date range.

        Args:
            studio_entity_type: Filter by entity type. One of:
                                STUDIO_ENTITY_TYPE_UNSPECIFIED,
                                STUDIO_ENTITY_TYPE_USER,
                                STUDIO_ENTITY_TYPE_PROJECT,
                                STUDIO_ENTITY_TYPE_SPACE.
            studio_entity_name: Filter by entity name.
            studio_notification_event_type: Filter by event type. One of:
                                            STUDIO_NOTIFICATION_EVENT_TYPE_UNSPECIFIED,
                                            STUDIO_NOTIFICATION_EVENT_TYPE_ACM,
                                            STUDIO_NOTIFICATION_EVENT_TYPE_COMPUTE,
                                            STUDIO_NOTIFICATION_EVENT_TYPE_API,
                                            STUDIO_NOTIFICATION_EVENT_TYPE_SPACE,
                                            STUDIO_NOTIFICATION_EVENT_TYPE_PROJECT.
            studio_notification_event_name: Filter by event name.
            user_id: Filter by user ID.
            start_date: Start date for date range filter (e.g. "2025-01-01").
            end_date: End date for date range filter (e.g. "2025-12-31").
            page_token: Token to retrieve the next page of results.
            page_size: Maximum number of notifications per page.
        """
        query: dict[str, Any] = {}
        if studio_entity_type is not None:
            query["studioEntityType"] = studio_entity_type
        if studio_entity_name is not None:
            query["studioEntityName"] = studio_entity_name
        if studio_notification_event_type is not None:
            query["studioNotificationEventType"] = studio_notification_event_type
        if studio_notification_event_name is not None:
            query["studioNotificationEventName"] = studio_notification_event_name
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

        return _call_api("/studioNotifications:filter", http_method="post", request_body=body)
