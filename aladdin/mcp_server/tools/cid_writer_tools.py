"""MCP tools for the Aladdin Custom Investment Dataset (CID) Writer API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_CID_WRITER_BASE_PATH = "/api/portfolio-management/setup/cids/v1/"

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
    """Helper to call a CID Writer API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_CID_WRITER_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"CID Writer API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_cid_writer_tools(mcp: FastMCP) -> None:
    """Register Aladdin CID Writer API tools with the MCP server."""

    @mcp.tool()
    def create_cid_dataset_definition(
        dataset_name: str,
        dataset_type: str,
        element_path: str,
        description: str = "",
        schema_name: str | None = None,
        repo_name: str | None = None,
        perm_group: str | None = None,
        meta_info: str | None = None,
        team: str | None = None,
        purpose: str | None = None,
        dataset_full_name: str | None = None,
        retention_policy_period: str | None = None,
    ) -> str:
        """Create a new CID Dataset Definition. A Dataset can be Category, Class, Group or Leaf Level Dataset.

        Args:
            dataset_name: Name of the Dataset. Character limit: 25.
            dataset_type: Type of entities that can be added (e.g. DATASET_TYPE_SCHEMA).
            element_path: Dataset hierarchy definition as a path string.
            description: Description of the dataset.
            schema_name: Name of the schema in case of DATASET_TYPE_SCHEMA. Character limit: 25.
            repo_name: Repo name describing the type of data written in this dataset.
            perm_group: Permission group identification for the dataset.
            meta_info: Additional information in key=value format.
            team: Team that owns the dataset. Character limit: 15.
            purpose: Dataset level - Category/Class/Group/Dataset.
            dataset_full_name: Full name of the dataset. Character limit: 75.
            retention_policy_period: Retention policy period for the dataset.
        """
        body: dict[str, Any] = {
            "datasetName": dataset_name,
            "datasetType": dataset_type,
            "elementPath": element_path,
        }
        if description:
            body["description"] = description
        if schema_name is not None:
            body["schemaName"] = schema_name
        if repo_name is not None:
            body["repoName"] = repo_name
        if perm_group is not None:
            body["permGroup"] = perm_group
        if meta_info is not None:
            body["metaInfo"] = meta_info
        if team is not None:
            body["team"] = team
        if purpose is not None:
            body["purpose"] = purpose
        if dataset_full_name is not None:
            body["datasetFullName"] = dataset_full_name
        if retention_policy_period is not None:
            body["retentionPolicyPeriod"] = retention_policy_period

        return _call_api("/datasets/definitions", http_method="post", request_body=body)

    @mcp.tool()
    def update_cid_dataset_definition(
        dataset_name: str,
        dataset_type: str | None = None,
        element_path: str | None = None,
        description: str | None = None,
        schema_name: str | None = None,
        repo_name: str | None = None,
        perm_group: str | None = None,
        meta_info: str | None = None,
        team: str | None = None,
        purpose: str | None = None,
        dataset_full_name: str | None = None,
        retention_policy_period: str | None = None,
    ) -> str:
        """Update an existing CID Dataset Definition and create a new version of it.

        Args:
            dataset_name: Name of the Dataset to update.
            dataset_type: Type of entities that can be added.
            element_path: Dataset hierarchy definition as a path string.
            description: Description of the dataset.
            schema_name: Name of the schema in case of DATASET_TYPE_SCHEMA.
            repo_name: Repo name describing the type of data.
            perm_group: Permission group identification.
            meta_info: Additional information in key=value format.
            team: Team that owns the dataset.
            purpose: Dataset level - Category/Class/Group/Dataset.
            dataset_full_name: Full name of the dataset.
            retention_policy_period: Retention policy period for the dataset.
        """
        body: dict[str, Any] = {"datasetName": dataset_name}
        if dataset_type is not None:
            body["datasetType"] = dataset_type
        if element_path is not None:
            body["elementPath"] = element_path
        if description is not None:
            body["description"] = description
        if schema_name is not None:
            body["schemaName"] = schema_name
        if repo_name is not None:
            body["repoName"] = repo_name
        if perm_group is not None:
            body["permGroup"] = perm_group
        if meta_info is not None:
            body["metaInfo"] = meta_info
        if team is not None:
            body["team"] = team
        if purpose is not None:
            body["purpose"] = purpose
        if dataset_full_name is not None:
            body["datasetFullName"] = dataset_full_name
        if retention_policy_period is not None:
            body["retentionPolicyPeriod"] = retention_policy_period

        return _call_api("/datasets/definitions", http_method="patch", request_body=body)

    @mcp.tool()
    def activate_cid_dataset_definition(
        dataset_name: str,
        revision_id: str,
    ) -> str:
        """Activate a CID Dataset Definition in DRAFT state, moving it to APPROVED state.

        Once activated, entities can be written to the dataset.

        Args:
            dataset_name: Name of the Dataset to activate.
            revision_id: Version of the DRAFT Dataset to be activated.
        """
        body: dict[str, Any] = {
            "datasetName": dataset_name,
            "revisionId": revision_id,
        }
        return _call_api(
            "/datasets/definitions:activateCidDatasetDefinition",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def expire_cid_dataset_definition(
        dataset_name: str,
        revision_id: str,
    ) -> str:
        """Expire an APPROVED CID Dataset Definition, moving it to RETIRED state.

        Once expired, entities can no longer be written to the dataset.

        Args:
            dataset_name: Name of the Dataset to expire.
            revision_id: Version of the APPROVED Dataset to be expired.
        """
        body: dict[str, Any] = {
            "datasetName": dataset_name,
            "revisionId": revision_id,
        }
        return _call_api(
            "/datasets/definitions:expireCidDatasetDefinition",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def create_cid_dataset_schema(
        dataset_name: str,
        attributes: list[dict[str, Any]],
    ) -> str:
        """Create a data schema for a CID Dataset.

        Args:
            dataset_name: Name of the category or classification dataset in the hierarchy.
            attributes: List of schema attributes. Each dict can have:
                        schemaAttributeName (str, limit 15), attributeType (str),
                        indexed (bool), metaData (str), description (str),
                        attributeDisplayName (str, limit 75), indexOrder (str),
                        attributePrecision (str), attributeAgg (str),
                        listMappings (dict).
        """
        body: dict[str, Any] = {
            "datasetName": dataset_name,
            "data": {"attributes": attributes},
        }
        return _call_api("/datasets/schema", http_method="post", request_body=body)

    @mcp.tool()
    def update_cid_dataset_schema(
        schema_id: str,
        dataset_name: str | None = None,
        attributes: list[dict[str, Any]] | None = None,
        update_mask: str | None = None,
    ) -> str:
        """Update an existing CID Dataset Schema.

        Args:
            schema_id: The ID of the schema to update.
            dataset_name: Name of the category or classification dataset.
            attributes: List of updated schema attributes. Each dict can have:
                        schemaAttributeName (str), attributeType (str),
                        indexed (bool), metaData (str), description (str),
                        attributeDisplayName (str), indexOrder (str),
                        attributePrecision (str), attributeAgg (str),
                        listMappings (dict).
            update_mask: Comma-separated list of fields to update.
        """
        body: dict[str, Any] = {"id": schema_id}
        if dataset_name is not None:
            body["datasetName"] = dataset_name
        if attributes is not None:
            body["data"] = {"attributes": attributes}

        params: dict[str, Any] | None = None
        if update_mask is not None:
            params = {"updateMask": update_mask}

        return _call_api(
            f"/datasets/schema/{schema_id}",
            http_method="patch",
            request_body=body,
            params=params,
        )

    @mcp.tool()
    def batch_create_cid_entities(
        parent: str,
        requests: list[dict[str, Any]],
    ) -> str:
        """Create entities in an approved CID Dataset.

        Entities can only be created under leaf level approved Datasets.

        Args:
            parent: Name of the parent Dataset under which entities are created.
            requests: List of entity creation requests. Each dict should have a
                      cidEntity dict with fields: entityName (str, limit 75),
                      datasetName (str), entityType (str, e.g. isin/cusip/broker),
                      timeRange (dict with startTime/expireTime),
                      data (str), author (str, limit 8),
                      portfolioName (str, for portfolio datasets only).
        """
        body: dict[str, Any] = {"requests": requests}
        return _call_api(
            f"/datasets/{parent}/entities:batchCreate",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def batch_update_cid_entities(
        parent: str,
        requests: list[dict[str, Any]],
    ) -> str:
        """Update existing entities in a CID Dataset.

        Entities can be activated by updating their state to APPROVED.

        Args:
            parent: Name of the Dataset for which entities are to be updated.
            requests: List of entity update requests. Each dict should have a
                      cidEntity dict with fields: id (str), entityName (str),
                      datasetName (str), entityType (str),
                      timeRange (dict with startTime/expireTime),
                      state (str), data (str), author (str, limit 8),
                      portfolioName (str).
        """
        body: dict[str, Any] = {
            "parent": parent,
            "requests": requests,
        }
        return _call_api(
            "/datasets/entities:batchUpdate",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def batch_delete_cid_entities(
        parent: str,
        requests: list[dict[str, Any]],
    ) -> str:
        """Expire APPROVED entities in a CID Dataset, moving them to RETIRED state.

        Args:
            parent: Name of the parent Dataset containing the entities.
            requests: List of entity expiration requests. Each dict should have:
                      datasetName (str), entityName (str),
                      startTime (str, start time of the APPROVED entity version),
                      revisionId (str, version of the APPROVED entity),
                      portfolioName (str, optional).
        """
        body: dict[str, Any] = {"requests": requests}
        return _call_api(
            f"/datasets/{parent}/entities:batchDelete",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def upload_cid_entities_file(
        dataset: str,
        filename: str,
        content: str,
        email: str | None = None,
    ) -> str:
        """Upload an entities file for a CID Dataset.

        For loading entities of a given dataset from a file.

        Args:
            dataset: Name of the dataset to upload entities to.
            filename: Name of the file being uploaded.
            content: Base64 encoded file content.
            email: Email address for notification upon completion.
        """
        body: dict[str, Any] = {
            "dataset": dataset,
            "filename": filename,
            "content": content,
        }
        if email is not None:
            body["email"] = email

        return _call_api(
            "/datasets:uploadEntitiesFile",
            http_method="post",
            request_body=body,
        )
