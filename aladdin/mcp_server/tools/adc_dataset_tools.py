"""MCP tools for the Aladdin ADC Dataset API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_BASE_PATH = "/api/platform/studio/adc/adc-dataset/v1/"

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
    """Helper to call an ADC Dataset API endpoint and return JSON string."""
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
        logger.error(f"ADC Dataset API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_adc_dataset_tools(mcp: FastMCP) -> None:
    """Register Aladdin ADC Dataset API tools with the MCP server."""

    @mcp.tool()
    def get_adc_dataset(
        database: str,
        schema: str,
        dataset_name: str,
        client_abbreviation: str,
        version: str,
    ) -> str:
        """Get an ADC Dataset matching the given criteria.

        Conforms to the 'idxPrimary' index: database, schema, datasetName,
        clientAbbreviation, and version together uniquely identify a dataset.

        Args:
            database: Underlying database name (upper case, e.g. CUSTOMDB).
            schema: Underlying schema name (upper case, e.g. PUBLIC).
            dataset_name: Name of the dataset/view.
            client_abbreviation: Aladdin client environment abbreviation (upper case).
            version: Semantic version string (e.g. 1.0.0).
        """
        params: dict[str, Any] = {
            "datasetId.database": database,
            "datasetId.schema": schema,
            "datasetId.datasetName": dataset_name,
            "datasetId.clientAbbreviation": client_abbreviation,
            "datasetId.version": version,
        }
        return _call_api("/adcDatasets", http_method="get", params=params)

    @mcp.tool()
    def create_adc_dataset(
        dataset_name: str,
        client_abbreviation: str,
        version: str,
        database: str,
        schema: str,
        description: str = "",
        dataset_type: str = "DATASET_TYPE_UNSPECIFIED",
        bitemporal: bool = False,
        category: str = "",
        display_name: str = "",
        merge_enabled: bool = False,
        primary_keys: list[str] | None = None,
        version_key: str = "",
        tags: list[str] | None = None,
        success_emails: list[str] | None = None,
        failure_emails: list[str] | None = None,
        target_ddl_commands: list[str] | None = None,
        underlying_datasets: list[str] | None = None,
        input_location: str = "",
        column_metadata: dict[str, Any] | None = None,
        table_metadata: dict[str, Any] | None = None,
        etl_config: dict[str, Any] | None = None,
        dataset_facet: dict[str, Any] | None = None,
        ingestion_facet: dict[str, Any] | None = None,
    ) -> str:
        """Create a new ADC Dataset in the Aladdin Data Cloud.

        Args:
            dataset_name: Name of the dataset.
            client_abbreviation: Aladdin client environment abbreviation (upper case).
            version: Semantic version string (e.g. 1.0.0).
            database: Underlying database name (upper case).
            schema: Underlying schema name (upper case).
            description: Description of the dataset.
            dataset_type: Type of dataset (DATASET_TYPE_UNSPECIFIED, DATASET_TYPE_TABLE,
                          DATASET_TYPE_VIEW, DATASET_TYPE_HIST_VIEW).
            bitemporal: Whether the dataset is bitemporal.
            category: Business categorization of dataset.
            display_name: Human-readable display name.
            merge_enabled: Whether merge is enabled.
            primary_keys: List of primary key column names.
            version_key: Version key for the dataset.
            tags: List of tags.
            success_emails: Email addresses for success notifications.
            failure_emails: Email addresses for failure notifications.
            target_ddl_commands: List of DDL commands for target.
            underlying_datasets: List of underlying dataset references.
            input_location: Input data location.
            column_metadata: Column metadata configuration.
            table_metadata: Table metadata configuration.
            etl_config: ETL configuration.
            dataset_facet: Dataset facet configuration.
            ingestion_facet: Ingestion facet configuration.
        """
        body: dict[str, Any] = {
            "datasetName": dataset_name,
            "clientAbbreviation": client_abbreviation,
            "version": version,
            "database": database,
            "schema": schema,
            "datasetType": dataset_type,
            "bitemporal": bitemporal,
            "mergeEnabled": merge_enabled,
        }
        if description:
            body["description"] = description
        if category:
            body["category"] = category
        if display_name:
            body["displayName"] = display_name
        if version_key:
            body["versionKey"] = version_key
        if input_location:
            body["inputLocation"] = input_location
        if primary_keys:
            body["primaryKeys"] = primary_keys
        if tags:
            body["tags"] = tags
        if success_emails:
            body["successEmails"] = success_emails
        if failure_emails:
            body["failureEmails"] = failure_emails
        if target_ddl_commands:
            body["targetDdlCommands"] = target_ddl_commands
        if underlying_datasets:
            body["underlyingDatasets"] = underlying_datasets
        if column_metadata is not None:
            body["columnMetadata"] = column_metadata
        if table_metadata is not None:
            body["tableMetadata"] = table_metadata
        if etl_config is not None:
            body["etlConfig"] = etl_config
        if dataset_facet is not None:
            body["datasetFacet"] = dataset_facet
        if ingestion_facet is not None:
            body["ingestionFacet"] = ingestion_facet

        return _call_api("/adcDatasets", http_method="post", request_body=body)

    @mcp.tool()
    def delete_adc_dataset(
        database: str,
        schema: str,
        dataset_name: str,
        client_abbreviation: str,
        version: str,
        drop_db_object: bool = False,
    ) -> str:
        """Delete an ADC Dataset.

        Args:
            database: Underlying database name (upper case).
            schema: Underlying schema name (upper case).
            dataset_name: Name of the dataset/view.
            client_abbreviation: Aladdin client environment abbreviation (upper case).
            version: Semantic version string (e.g. 1.0.0).
            drop_db_object: If true, all database objects associated with the dataset
                            will be dropped.
        """
        params: dict[str, Any] = {
            "datasetId.database": database,
            "datasetId.schema": schema,
            "datasetId.datasetName": dataset_name,
            "datasetId.clientAbbreviation": client_abbreviation,
            "datasetId.version": version,
        }
        if drop_db_object:
            params["dropDbObject"] = drop_db_object

        return _call_api("/adcDatasets", http_method="delete", params=params)

    @mcp.tool()
    def update_adc_dataset(
        database: str,
        schema: str,
        dataset_name: str,
        client_abbreviation: str,
        version: str,
        update_mask: str | None = None,
        description: str | None = None,
        dataset_type: str | None = None,
        bitemporal: bool | None = None,
        category: str | None = None,
        display_name: str | None = None,
        merge_enabled: bool | None = None,
        primary_keys: list[str] | None = None,
        version_key: str | None = None,
        tags: list[str] | None = None,
        success_emails: list[str] | None = None,
        failure_emails: list[str] | None = None,
        target_ddl_commands: list[str] | None = None,
        underlying_datasets: list[str] | None = None,
        input_location: str | None = None,
        column_metadata: dict[str, Any] | None = None,
        table_metadata: dict[str, Any] | None = None,
        etl_config: dict[str, Any] | None = None,
        dataset_facet: dict[str, Any] | None = None,
        ingestion_facet: dict[str, Any] | None = None,
    ) -> str:
        """Update an existing ADC Dataset. Only provided fields are updated.

        Args:
            database: Underlying database name (upper case) - identifies the dataset.
            schema: Underlying schema name (upper case) - identifies the dataset.
            dataset_name: Name of the dataset - identifies the dataset.
            client_abbreviation: Aladdin client environment abbreviation (upper case) -
                                 identifies the dataset.
            version: Semantic version string - identifies the dataset.
            update_mask: Comma-separated list of fields to update (e.g. "description,tags").
            description: New description.
            dataset_type: Type of dataset (DATASET_TYPE_UNSPECIFIED, DATASET_TYPE_TABLE,
                          DATASET_TYPE_VIEW, DATASET_TYPE_HIST_VIEW).
            bitemporal: Whether the dataset is bitemporal.
            category: Business categorization of dataset.
            display_name: Human-readable display name.
            merge_enabled: Whether merge is enabled.
            primary_keys: List of primary key column names.
            version_key: Version key for the dataset.
            tags: List of tags.
            success_emails: Email addresses for success notifications.
            failure_emails: Email addresses for failure notifications.
            target_ddl_commands: List of DDL commands for target.
            underlying_datasets: List of underlying dataset references.
            input_location: Input data location.
            column_metadata: Column metadata configuration.
            table_metadata: Table metadata configuration.
            etl_config: ETL configuration.
            dataset_facet: Dataset facet configuration.
            ingestion_facet: Ingestion facet configuration.
        """
        params: dict[str, Any] = {
            "datasetId.database": database,
            "datasetId.schema": schema,
            "datasetId.datasetName": dataset_name,
            "datasetId.clientAbbreviation": client_abbreviation,
            "datasetId.version": version,
        }
        if update_mask is not None:
            params["updateMask"] = update_mask

        body: dict[str, Any] = {}
        if description is not None:
            body["description"] = description
        if dataset_type is not None:
            body["datasetType"] = dataset_type
        if bitemporal is not None:
            body["bitemporal"] = bitemporal
        if category is not None:
            body["category"] = category
        if display_name is not None:
            body["displayName"] = display_name
        if merge_enabled is not None:
            body["mergeEnabled"] = merge_enabled
        if primary_keys is not None:
            body["primaryKeys"] = primary_keys
        if version_key is not None:
            body["versionKey"] = version_key
        if tags is not None:
            body["tags"] = tags
        if success_emails is not None:
            body["successEmails"] = success_emails
        if failure_emails is not None:
            body["failureEmails"] = failure_emails
        if target_ddl_commands is not None:
            body["targetDdlCommands"] = target_ddl_commands
        if underlying_datasets is not None:
            body["underlyingDatasets"] = underlying_datasets
        if input_location is not None:
            body["inputLocation"] = input_location
        if column_metadata is not None:
            body["columnMetadata"] = column_metadata
        if table_metadata is not None:
            body["tableMetadata"] = table_metadata
        if etl_config is not None:
            body["etlConfig"] = etl_config
        if dataset_facet is not None:
            body["datasetFacet"] = dataset_facet
        if ingestion_facet is not None:
            body["ingestionFacet"] = ingestion_facet

        return _call_api(
            "/adcDatasets",
            http_method="patch",
            request_body=body,
            params=params,
        )

    @mcp.tool()
    def filter_adc_datasets(
        dataset_name: str | None = None,
        client_abbreviation: str | None = None,
        database: str | None = None,
        schema: str | None = None,
        version: str | None = None,
        states: list[str] | None = None,
        page_token: str | None = None,
        page_size: int | None = None,
    ) -> str:
        """Filter ADC Datasets by various criteria.

        Args:
            dataset_name: Filter on dataset name.
            client_abbreviation: Filter on Aladdin client environment abbreviation.
            database: Filter on database name.
            schema: Filter on schema name.
            version: Filter on version.
            states: Filter on dataset states (list of state strings).
            page_token: Page token from a previous FilterAdcDatasets call.
            page_size: Maximum number of datasets to return (max 500, default 500).
        """
        adc_dataset_query: dict[str, Any] = {}
        if dataset_name is not None:
            adc_dataset_query["datasetName"] = dataset_name
        if client_abbreviation is not None:
            adc_dataset_query["clientAbbreviation"] = client_abbreviation
        if database is not None:
            adc_dataset_query["database"] = database
        if schema is not None:
            adc_dataset_query["schema"] = schema
        if version is not None:
            adc_dataset_query["version"] = version
        if states is not None:
            adc_dataset_query["states"] = states

        body: dict[str, Any] = {}
        if adc_dataset_query:
            body["adcDatasetQuery"] = adc_dataset_query
        if page_token is not None:
            body["pageToken"] = page_token
        if page_size is not None:
            body["pageSize"] = page_size

        return _call_api("/adcDatasets:filter", http_method="post", request_body=body)

    @mcp.tool()
    def reconcile_adc_datasets(
        source_client_abbreviation: str,
        target_client_abbreviation: str,
        schema: str | None = None,
        email_addresses: list[str] | None = None,
    ) -> str:
        """Reconcile ADC Datasets between two client environments.

        Args:
            source_client_abbreviation: Client abbreviation to reconcile from.
            target_client_abbreviation: Client abbreviation to reconcile against.
            schema: Database schema to run reconciliation against.
            email_addresses: Email addresses to receive the reconciliation report.
        """
        body: dict[str, Any] = {
            "sourceClientAbbreviation": source_client_abbreviation,
            "targetClientAbbreviation": target_client_abbreviation,
        }
        if schema is not None:
            body["schema"] = schema
        if email_addresses is not None:
            body["emailAddresses"] = email_addresses

        return _call_api("/adcDatasets:reconcile", http_method="post", request_body=body)

    @mcp.tool()
    def refresh_adc_datasets(
        database: str,
        schema: str,
        dataset_names: list[str] | None = None,
    ) -> str:
        """Refresh the schema (columnMetadata) of ADC Datasets.

        Args:
            database: Database name for the schema identifier.
            schema: Schema name for the schema identifier.
            dataset_names: List of dataset names to refresh within the given
                           database and schema.
        """
        body: dict[str, Any] = {
            "schemaId": {
                "database": database,
                "schema": schema,
            },
        }
        if dataset_names is not None:
            body["datasetNames"] = dataset_names

        return _call_api("/adcDatasets:refresh", http_method="post", request_body=body)

    @mcp.tool()
    def register_adc_datasets(
        database: str,
        schema: str,
        data_owners: list[str],
        category: str,
        dataset_names: list[str] | None = None,
        auto_sync: bool = False,
    ) -> str:
        """Register ADC Datasets in Aladdin Studio.

        Args:
            database: Database name for the schema identifier.
            schema: Schema name for the schema identifier.
            data_owners: Email addresses identifying data owners (required for
                         successful registration).
            category: Business categorization of dataset for use in Aladdin Studio.
            dataset_names: List of dataset names belonging to the given database
                           and schema.
            auto_sync: Whether background metadata refresh is set to automatic.
        """
        body: dict[str, Any] = {
            "schemaId": {
                "database": database,
                "schema": schema,
            },
            "dataOwners": data_owners,
            "category": category,
            "autoSync": auto_sync,
        }
        if dataset_names is not None:
            body["datasetNames"] = dataset_names

        return _call_api("/adcDatasets:register", http_method="post", request_body=body)

    @mcp.tool()
    def release_adc_dataset(
        database: str,
        schema: str,
        dataset_name: str,
        client_abbreviation: str,
        version: str,
    ) -> str:
        """Release an ADC Dataset.

        Args:
            database: Underlying database name (upper case).
            schema: Underlying schema name (upper case).
            dataset_name: Name of the dataset.
            client_abbreviation: Aladdin client environment abbreviation (upper case).
            version: Semantic version string.
        """
        body: dict[str, Any] = {
            "datasetId": {
                "database": database,
                "schema": schema,
                "datasetName": dataset_name,
                "clientAbbreviation": client_abbreviation,
                "version": version,
            },
        }
        return _call_api(
            "/adcDatasets:releaseAdcDataset",
            http_method="post",
            request_body=body,
        )

    @mcp.tool()
    def batch_update_dataset_facets(
        requests: list[dict[str, Any]],
        database: str | None = None,
        schema: str | None = None,
    ) -> str:
        """Update Dataset Facets in batch.

        Args:
            requests: List of update requests. Each dict should contain:
                      - datasetFacet (dict): The dataset facet to update.
                      - updateMask (str, optional): Comma-separated list of fields
                        to update.
            database: Database name to narrow down datasets (optional).
            schema: Schema name to narrow down datasets (optional).
        """
        body: dict[str, Any] = {
            "requests": requests,
        }
        if database is not None and schema is not None:
            body["schemaId"] = {
                "database": database,
                "schema": schema,
            }

        return _call_api(
            "/datasetFacets:batchUpdate",
            http_method="patch",
            request_body=body,
        )

    @mcp.tool()
    def get_longrunning_operation(operation_id: str) -> str:
        """Get the state of a long-running operation.

        Args:
            operation_id: ID of the long-running operation.
        """
        return _call_api(
            f"/longRunningOperations/{operation_id}",
            http_method="get",
        )
