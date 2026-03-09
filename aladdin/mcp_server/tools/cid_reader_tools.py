"""MCP tools for the Aladdin Custom Investment Dataset (CID) Reader API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_BASE_PATH = "/api/portfolio-management/setup/cids/v1/"

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
    http_method: str = "get",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a CID Reader API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"CID Reader API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_cid_reader_tools(mcp: FastMCP) -> None:
    """Register Aladdin CID Reader API tools with the MCP server."""

    @mcp.tool()
    def remove_datasets(
        dataset_names: list[str],
    ) -> str:
        """Remove datasets from the CID Read server cache so that entities can be reloaded from ADL on the next request.

        Args:
            dataset_names: List of dataset names to be evicted from cache.
        """
        body: dict[str, Any] = {
            "datasetNames": dataset_names,
        }
        return _call_api("/datasets/datasets:remove", http_method="post", request_body=body)

    @mcp.tool()
    def list_cid_dataset_definitions(
        state: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
        include_all_status: bool | None = None,
    ) -> str:
        """Retrieve all latest versions of CID Dataset Definitions.

        Args:
            state: Filter by state of the dataset. One of STATE_UNSPECIFIED, STATE_DRAFT, STATE_APPROVED, STATE_RETIRED, STATE_SUSPENDED.
            page_size: The number of Dataset Definitions to be returned per page.
            page_token: Token used to retrieve the next set of Dataset Definitions (from previous response's next_page_token).
            include_all_status: Set to True to include datasets with all statuses; otherwise only Approved status datasets are returned.
        """
        params: dict[str, Any] = {}
        if state is not None:
            params["state"] = state
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token is not None:
            params["pageToken"] = page_token
        if include_all_status is not None:
            params["includeAllStatus"] = include_all_status

        return _call_api("/datasets/definitions", http_method="get", params=params or None)

    @mcp.tool()
    def get_cid_dataset_definition(
        dataset_name: str,
    ) -> str:
        """Retrieve the latest approved version of a CID Dataset Definition by its name.

        Args:
            dataset_name: Name of the Category, Class, Group or leaf level Dataset.
        """
        return _call_api(f"/datasets/definitions/{dataset_name}", http_method="get")

    @mcp.tool()
    def filter_cid_entities(
        dataset_names: list[str],
        entity_names: list[str] | None = None,
        port_names: list[str] | None = None,
        state: str | None = None,
        index_attribute_criterion: dict[str, Any] | None = None,
        time_range: dict[str, Any] | None = None,
        as_of_date: str | None = None,
        data_column_filters: list[str] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter active versions of CID dataset entities by filter criteria.

        If state is unspecified, returns APPROVED entities matching the criteria.
        Only one of entity_names, port_names, state, or index_attribute_criterion should be specified at a time.

        Args:
            dataset_names: List of dataset names to filter on (required).
            entity_names: List of entity names to filter by.
            port_names: List of portfolio names to filter by.
            state: State of the entity. One of STATE_UNSPECIFIED, STATE_DRAFT, STATE_APPROVED, STATE_RETIRED, STATE_SUSPENDED.
            index_attribute_criterion: Indexed attribute criteria dict for searching records (e.g. {"filterType": "...", "filterValue": "..."}).
            time_range: Start and expire time range dict with keys "startTime" and "expireTime" (UTC datetime strings).
            as_of_date: As-of date (YYYY-MM-DD). All records valid as of this date will be returned. Only T or T-1 supported.
            data_column_filters: List of column names corresponding to data fields expected in the response.
            page_size: The number of entities to be returned per page.
            page_token: Token used to retrieve the next set of records (from previous response's next_page_token).
        """
        body: dict[str, Any] = {
            "datasetNames": dataset_names,
        }
        if entity_names is not None:
            body["entityName"] = {"entityNames": entity_names}
        if port_names is not None:
            body["portName"] = {"portNames": port_names}
        if state is not None:
            body["state"] = state
        if index_attribute_criterion is not None:
            body["indexAttributeCriterion"] = index_attribute_criterion
        if time_range is not None:
            body["timeRange"] = time_range
        if as_of_date is not None:
            body["asOfDate"] = as_of_date
        if data_column_filters is not None:
            body["dataColumnFilters"] = data_column_filters
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api("/datasets/entities:filter", http_method="post", request_body=body)

    @mcp.tool()
    def get_cid_dataset_hierarchy(
        dataset_name: str,
        include_all_status: bool | None = None,
    ) -> str:
        """Retrieve the full hierarchy associated with a CID Dataset by its name.

        Args:
            dataset_name: Name of the Dataset.
            include_all_status: Set to True to include datasets with all statuses; otherwise only Approved status datasets are returned.
        """
        params: dict[str, Any] = {}
        if include_all_status is not None:
            params["includeAllStatus"] = include_all_status

        return _call_api(
            f"/datasets/hierarchy/{dataset_name}",
            http_method="get",
            params=params or None,
        )

    @mcp.tool()
    def list_cid_entities(
        dataset_name: str,
        page_size: int | None = None,
        page_token: str | None = None,
        as_of_date: str | None = None,
        time_range_start_time: str | None = None,
        time_range_expire_time: str | None = None,
    ) -> str:
        """Retrieve all latest approved versions of entities for a given CID Dataset.

        Optionally accepts an as-of date or date range to return only the subset valid within that period.

        Args:
            dataset_name: Name of the Dataset. This cannot be a Category, Class or Group level Dataset.
            page_size: The number of entities to be returned per page.
            page_token: Token used to retrieve the next set of entities (from previous response's next_page_token).
            as_of_date: As-of date (UTC). All records valid as of this date will be returned. Defaults to today if not specified.
            time_range_start_time: Start time of the entity range (UTC datetime string). Defaults to current date time when not provided.
            time_range_expire_time: Expire time of the entity range (UTC datetime string). Defaults to 12/31/2222 when not provided.
        """
        params: dict[str, Any] = {}
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token is not None:
            params["pageToken"] = page_token
        if as_of_date is not None:
            params["asOfDate"] = as_of_date
        if time_range_start_time is not None:
            params["timeRange.startTime"] = time_range_start_time
        if time_range_expire_time is not None:
            params["timeRange.expireTime"] = time_range_expire_time

        return _call_api(
            f"/datasets/{dataset_name}/entities",
            http_method="get",
            params=params or None,
        )

    @mcp.tool()
    def get_cid_dataset_schema(
        schema_name: str,
    ) -> str:
        """Retrieve the latest approved version of a CID Dataset Schema by its name.

        Args:
            schema_name: Name of the schema.
        """
        return _call_api(f"/schema/{schema_name}", http_method="get")
