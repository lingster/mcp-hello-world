"""MCP tools for the Aladdin Train Journey API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_TRAIN_JOURNEY_BASE_PATH = "/api/reference-architecture/demo/train-journey/v1/"

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
    """Helper to call a Train Journey API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_TRAIN_JOURNEY_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Train Journey API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def _build_train_journey_body(
    short_code: str | None = None,
    train_id: str | None = None,
    departing_train_station_id: str | None = None,
    destination_train_station_id: str | None = None,
    pass_through_station_ids: list[str] | None = None,
    journey_date: str | None = None,
    journey_time: str | None = None,
    journey_duration: str | None = None,
    journey_id: str | None = None,
) -> dict[str, Any]:
    """Build a TrainJourney dict, filtering out None values."""
    body: dict[str, Any] = {}
    if journey_id is not None:
        body["id"] = journey_id
    if short_code is not None:
        body["shortCode"] = short_code
    if train_id is not None:
        body["trainId"] = train_id
    if departing_train_station_id is not None:
        body["departingTrainStationId"] = departing_train_station_id
    if destination_train_station_id is not None:
        body["destinationTrainStationId"] = destination_train_station_id
    if pass_through_station_ids is not None:
        body["passThroughStationIds"] = pass_through_station_ids
    if journey_date is not None:
        body["journeyDate"] = journey_date
    if journey_time is not None:
        body["journeyTime"] = journey_time
    if journey_duration is not None:
        body["journeyDuration"] = journey_duration
    return body


def register_train_journey_tools(mcp: FastMCP) -> None:
    """Register Aladdin Train Journey API tools with the MCP server."""

    @mcp.tool()
    def get_longrunning_operation(operation_id: str) -> str:
        """Get the state of a long-running operation.

        Clients can use this method to poll the operation result at intervals
        as recommended by the API service.

        Args:
            operation_id: The unique identifier of the long-running operation.
        """
        return _call_api(
            f"/longRunningOperations/{operation_id}",
            http_method="get",
        )

    @mcp.tool()
    def cancel_longrunning_operation(operation_id: str) -> str:
        """Start asynchronous cancellation on a long-running operation.

        The server makes a best effort to cancel the operation, but success
        is not guaranteed. On successful cancellation the operation is not
        deleted; instead it receives a CANCELLED status.

        Args:
            operation_id: The id of the operation to cancel.
        """
        return _call_api(
            f"/longRunningOperations/{operation_id}:cancel",
            http_method="post",
        )

    @mcp.tool()
    def list_train_journeys(
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Retrieve a list of train journeys. Supports pagination.

        Args:
            page_size: Maximum number of train journeys to return (max 10).
            page_token: Page token from a previous ListTrainJourneys call
                        to retrieve the next page.
        """
        params: dict[str, Any] = {}
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token is not None:
            params["pageToken"] = page_token

        return _call_api(
            "/trainJourneys",
            http_method="get",
            params=params or None,
        )

    @mcp.tool()
    def create_train_journey(
        short_code: str | None = None,
        train_id: str | None = None,
        departing_train_station_id: str | None = None,
        destination_train_station_id: str | None = None,
        pass_through_station_ids: list[str] | None = None,
        journey_date: str | None = None,
        journey_time: str | None = None,
        journey_duration: str | None = None,
    ) -> str:
        """Create a new train journey.

        Args:
            short_code: The journey code used for identification.
            train_id: The train id.
            departing_train_station_id: The departing station id.
            destination_train_station_id: The destination station id.
            pass_through_station_ids: List of station ids the train passes through.
            journey_date: The date this journey is scheduled (YYYY-MM-DD).
            journey_time: The exact timestamp this journey is scheduled for.
            journey_duration: The duration of this journey.
        """
        body = _build_train_journey_body(
            short_code=short_code,
            train_id=train_id,
            departing_train_station_id=departing_train_station_id,
            destination_train_station_id=destination_train_station_id,
            pass_through_station_ids=pass_through_station_ids,
            journey_date=journey_date,
            journey_time=journey_time,
            journey_duration=journey_duration,
        )
        return _call_api("/trainJourneys", http_method="post", request_body=body)

    @mcp.tool()
    def get_train_journey(
        journey_id: str,
        expand_mask_expands: list[str] | None = None,
    ) -> str:
        """Retrieve a specific train journey by its ID.

        Args:
            journey_id: The train journey id.
            expand_mask_expands: Set of expands as key-value pair strings
                                 of format 'resource:slice_to_expand_with'.
        """
        params: dict[str, Any] = {}
        if expand_mask_expands is not None:
            params["expandMask.expands"] = expand_mask_expands

        return _call_api(
            f"/trainJourneys/{journey_id}",
            http_method="get",
            params=params or None,
        )

    @mcp.tool()
    def delete_train_journey(journey_id: str) -> str:
        """Delete a specific train journey.

        Args:
            journey_id: The id of the train journey to delete.
        """
        return _call_api(
            f"/trainJourneys/{journey_id}",
            http_method="delete",
        )

    @mcp.tool()
    def run_train_journey_simulation(journey_id: str) -> str:
        """Simulate an existing train journey in real time.

        Returns a long-running operation that will contain a
        SimulateTrainJourneyResponse when done.

        Args:
            journey_id: The id of the train journey to simulate.
        """
        return _call_api(
            f"/trainJourneys/{journey_id}:run",
            http_method="get",
        )

    @mcp.tool()
    def update_train_journey(
        journey_id: str,
        short_code: str | None = None,
        train_id: str | None = None,
        departing_train_station_id: str | None = None,
        destination_train_station_id: str | None = None,
        pass_through_station_ids: list[str] | None = None,
        journey_date: str | None = None,
        journey_time: str | None = None,
        journey_duration: str | None = None,
        update_mask: str | None = None,
    ) -> str:
        """Update an existing train journey.

        Only the fields provided will be updated. Use update_mask to specify
        exactly which fields to update. Returns NOT_FOUND if the journey
        does not exist.

        Args:
            journey_id: The id of the train journey to update.
            short_code: The journey code used for identification.
            train_id: The train id.
            departing_train_station_id: The departing station id.
            destination_train_station_id: The destination station id.
            pass_through_station_ids: List of station ids the train passes through.
            journey_date: The date this journey is scheduled (YYYY-MM-DD).
            journey_time: The exact timestamp this journey is scheduled for.
            journey_duration: The duration of this journey.
            update_mask: Comma-separated list of fields to update
                         (e.g. "shortCode,trainId").
        """
        body = _build_train_journey_body(
            journey_id=journey_id,
            short_code=short_code,
            train_id=train_id,
            departing_train_station_id=departing_train_station_id,
            destination_train_station_id=destination_train_station_id,
            pass_through_station_ids=pass_through_station_ids,
            journey_date=journey_date,
            journey_time=journey_time,
            journey_duration=journey_duration,
        )

        params: dict[str, Any] | None = None
        if update_mask is not None:
            params = {"updateMask": update_mask}

        return _call_api(
            f"/trainJourneys/{journey_id}",
            http_method="patch",
            request_body=body,
            params=params,
        )

    @mcp.tool()
    def batch_create_train_journeys(
        requests: list[dict[str, Any]],
    ) -> str:
        """Batch create new train journeys.

        A maximum of 1000 train journeys can be created in a batch.

        Args:
            requests: List of train journey dicts to create. Each dict can have:
                      shortCode (str), trainId (str), departingTrainStationId (str),
                      destinationTrainStationId (str), passThroughStationIds (list[str]),
                      journeyDate (str YYYY-MM-DD), journeyTime (str), journeyDuration (str).
        """
        body: dict[str, Any] = {
            "requests": [{"trainJourney": req} for req in requests],
        }
        return _call_api("/trainJourneys:batchCreate", http_method="post", request_body=body)

    @mcp.tool()
    def batch_delete_train_journeys(ids: list[str]) -> str:
        """Batch delete train journeys by their IDs.

        A maximum of 1000 train journeys can be deleted in a batch.

        Args:
            ids: List of train journey IDs to delete.
        """
        body: dict[str, Any] = {"ids": ids}
        return _call_api("/trainJourneys:batchDelete", http_method="post", request_body=body)

    @mcp.tool()
    def batch_update_train_journeys(
        requests: list[dict[str, Any]],
    ) -> str:
        """Batch update existing train journeys.

        A maximum of 1000 train journeys can be modified in a batch.
        Returns NOT_FOUND if any journey does not exist.

        Args:
            requests: List of update request dicts. Each dict should have:
                      trainJourney (dict with fields to update) and optionally
                      updateMask (str, comma-separated field names).
        """
        body: dict[str, Any] = {"requests": requests}
        return _call_api("/trainJourneys:batchUpdate", http_method="post", request_body=body)

    @mcp.tool()
    def filter_train_journeys(
        departing_station_id: str | None = None,
        destination_station_id: str | None = None,
        train_types: list[str] | None = None,
        excluded_station_ids: list[str] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter train journeys using provided criteria.

        Args:
            departing_station_id: The id of the departing train station.
            destination_station_id: The id of the destination train station.
            train_types: Train types to filter by. If empty, defaults to all.
            excluded_station_ids: Station ids to exclude from journeys
                                  passing through (max 5).
            page_size: Maximum number of results per page (max 100, default 100).
            page_token: Page token for retrieving subsequent pages.
        """
        query: dict[str, Any] = {}
        if departing_station_id is not None:
            query["departingStationId"] = departing_station_id
        if destination_station_id is not None:
            query["destinationStationId"] = destination_station_id
        if train_types is not None:
            query["trainTypes"] = train_types
        if excluded_station_ids is not None:
            query["excludedStationIds"] = excluded_station_ids

        body: dict[str, Any] = {}
        if query:
            body["query"] = query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api("/trainJourneys:filter", http_method="post", request_body=body)
