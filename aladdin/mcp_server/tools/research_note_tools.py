"""MCP tools for the Aladdin Research Note API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_RESEARCH_NOTE_BASE_PATH = "/api/investment-research/content/research-note/v2/"

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
    """Helper to call a Research Note API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_RESEARCH_NOTE_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Research Note API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def _build_entity_dicts(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize entity dicts, filtering out None values.

    Each entity dict may contain: issuer, assetId, investmentStrategyId.
    """
    cleaned: list[dict[str, Any]] = []
    for ent in entities:
        entry: dict[str, Any] = {}
        if ent.get("issuer"):
            entry["issuer"] = ent["issuer"]
        if ent.get("assetId"):
            entry["assetId"] = ent["assetId"]
        if ent.get("investmentStrategyId"):
            entry["investmentStrategyId"] = ent["investmentStrategyId"]
        cleaned.append(entry)
    return cleaned


def register_research_note_tools(mcp: FastMCP) -> None:
    """Register Aladdin Research Note API tools with the MCP server."""

    @mcp.tool()
    def create_research_note(
        author: str,
        subject: str,
        note: str,
        creator: str | None = None,
        note_category: str | None = None,
        keywords: list[str] | None = None,
        publish_time: str | None = None,
        note_state: str | None = None,
        selected_permission_groups: list[str] | None = None,
        entities: list[dict[str, Any]] | None = None,
        broker_id: str | None = None,
        expiringPermissionGroups: list[dict[str, Any]] | None = None,
        note_html: str | None = None,
        template_id: str | None = None,
        template_version: int | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> str:
        """Create a new research note.

        Args:
            author: The author of the research note.
            subject: The subject (title) of the research note.
            note: The note textual content.
            creator: The creator of the research note.
            note_category: The note category.
            keywords: List of keywords for the research note.
            publish_time: The publish time in ISO 8601 date-time format.
            note_state: The research note state. One of:
                        NOTE_STATE_UNSPECIFIED, NOTE_STATE_REGULAR,
                        NOTE_STATE_DRAFT, NOTE_STATE_DELETED, NOTE_STATE_INVALID.
            selected_permission_groups: List of selected permission groups.
            entities: List of entity dicts associated with the note. Each dict can have:
                      issuer (str), assetId (str), investmentStrategyId (str).
            broker_id: Broker identifier.
            expiringPermissionGroups: List of expiring permission group dicts. Each dict can have:
                                     permissionGroup (str), timeUnit (str), timeSpan (int).
            note_html: The note content in HTML format.
            template_id: Research template ID.
            template_version: Research template version.
            custom_fields: Custom fields as a dict where key is field ID and value is a
                           custom field value dict (booleanValue, integerValue, doubleValue,
                           stringValue, longValue, stringArrayValue, fieldDate).
        """
        body: dict[str, Any] = {
            "author": author,
            "subject": subject,
            "note": note,
        }
        if creator is not None:
            body["creator"] = creator
        if note_category is not None:
            body["noteCategory"] = note_category
        if keywords is not None:
            body["keywords"] = keywords
        if publish_time is not None:
            body["publishTime"] = publish_time
        if note_state is not None:
            body["noteState"] = note_state
        if selected_permission_groups is not None:
            body["selectedPermissionGroups"] = selected_permission_groups
        if entities is not None:
            body["entities"] = _build_entity_dicts(entities)
        if broker_id is not None:
            body["brokerId"] = broker_id
        if expiringPermissionGroups is not None:
            body["expiringPermissionGroups"] = expiringPermissionGroups
        if note_html is not None:
            body["noteHtml"] = note_html
        if template_id is not None:
            body["templateId"] = template_id
        if template_version is not None:
            body["templateVersion"] = template_version
        if custom_fields is not None:
            body["customFields"] = custom_fields

        return _call_api("/researchNote", http_method="post", request_body=body)

    @mcp.tool()
    def get_research_note(research_note_id: str) -> str:
        """Retrieve a research note by its ID.

        Args:
            research_note_id: The unique ID of the research note to retrieve.
        """
        return _call_api(
            f"/researchNote/{research_note_id}",
            http_method="get",
        )

    @mcp.tool()
    def delete_research_note(research_note_id: str) -> str:
        """Delete a research note by its ID.

        Args:
            research_note_id: The unique ID of the research note to delete.
        """
        return _call_api(
            f"/researchNote/{research_note_id}",
            http_method="delete",
        )

    @mcp.tool()
    def update_research_note(
        research_note_id: str,
        author: str | None = None,
        subject: str | None = None,
        note: str | None = None,
        creator: str | None = None,
        note_category: str | None = None,
        keywords: list[str] | None = None,
        publish_time: str | None = None,
        note_state: str | None = None,
        selected_permission_groups: list[str] | None = None,
        entities: list[dict[str, Any]] | None = None,
        broker_id: str | None = None,
        expiring_permission_groups: list[dict[str, Any]] | None = None,
        note_html: str | None = None,
        template_id: str | None = None,
        template_version: int | None = None,
        custom_fields: dict[str, Any] | None = None,
        update_mask: str | None = None,
    ) -> str:
        """Update an existing research note.

        Only the fields provided will be updated. Use update_mask to specify
        exactly which fields to update.

        Args:
            research_note_id: The unique ID of the research note to update.
            author: New author of the research note.
            subject: New subject (title) of the research note.
            note: New textual content of the note.
            creator: New creator of the research note.
            note_category: New note category.
            keywords: New list of keywords.
            publish_time: New publish time in ISO 8601 date-time format.
            note_state: New research note state. One of:
                        NOTE_STATE_UNSPECIFIED, NOTE_STATE_REGULAR,
                        NOTE_STATE_DRAFT, NOTE_STATE_DELETED, NOTE_STATE_INVALID.
            selected_permission_groups: New list of selected permission groups.
            entities: New list of entity dicts. Each dict can have:
                      issuer (str), assetId (str), investmentStrategyId (str).
            broker_id: New broker identifier.
            expiring_permission_groups: New list of expiring permission group dicts. Each dict
                                       can have: permissionGroup (str), timeUnit (str), timeSpan (int).
            note_html: New note content in HTML format.
            template_id: New research template ID.
            template_version: New research template version.
            custom_fields: New custom fields dict.
            update_mask: Comma-separated list of fields to update
                         (e.g. "subject,note,author").
        """
        body: dict[str, Any] = {"id": research_note_id}
        if author is not None:
            body["author"] = author
        if subject is not None:
            body["subject"] = subject
        if note is not None:
            body["note"] = note
        if creator is not None:
            body["creator"] = creator
        if note_category is not None:
            body["noteCategory"] = note_category
        if keywords is not None:
            body["keywords"] = keywords
        if publish_time is not None:
            body["publishTime"] = publish_time
        if note_state is not None:
            body["noteState"] = note_state
        if selected_permission_groups is not None:
            body["selectedPermissionGroups"] = selected_permission_groups
        if entities is not None:
            body["entities"] = _build_entity_dicts(entities)
        if broker_id is not None:
            body["brokerId"] = broker_id
        if expiring_permission_groups is not None:
            body["expiringPermissionGroups"] = expiring_permission_groups
        if note_html is not None:
            body["noteHtml"] = note_html
        if template_id is not None:
            body["templateId"] = template_id
        if template_version is not None:
            body["templateVersion"] = template_version
        if custom_fields is not None:
            body["customFields"] = custom_fields

        params: dict[str, Any] | None = None
        if update_mask is not None:
            params = {"updateMask": update_mask}

        return _call_api(
            f"/researchNote/{research_note_id}",
            http_method="patch",
            request_body=body,
            params=params,
        )

    @mcp.tool()
    def get_research_note_template(
        template_id: str,
        version: int | None = None,
    ) -> str:
        """Get a research note template by its ID.

        Args:
            template_id: The template ID to fetch.
            version: Optional template version to fetch a specific version.
        """
        params: dict[str, Any] | None = None
        if version is not None:
            params = {"version": version}

        return _call_api(
            f"/researchNoteTemplate/{template_id}",
            http_method="get",
            params=params,
        )

    @mcp.tool()
    def get_research_note_templates() -> str:
        """Get all available research note templates."""
        return _call_api(
            "/researchNoteTemplates",
            http_method="get",
        )

    @mcp.tool()
    def filter_research_note_templates(
        template_filter_criteria: list[str] | None = None,
        order_by: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter research note templates by criteria.

        Filter syntax examples:
          - 'template.author:"user"' to filter by author
          - 'Technology' to match anything containing "Technology"

        Args:
            template_filter_criteria: List of filter criteria strings
                                     (e.g. ['template.author:"user"']).
            order_by: Sort order string (e.g. 'note.publish_time desc, note.author').
            page_size: Max number of templates to return (default 10).
            page_token: Page token from a previous call for pagination.
        """
        body: dict[str, Any] = {}
        query: dict[str, Any] = {}

        if template_filter_criteria is not None:
            query["templateFilterCriteria"] = template_filter_criteria
        if order_by is not None:
            query["orderBy"] = order_by
        if query:
            body["query"] = query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api("/researchNoteTemplates:filter", http_method="post", request_body=body)

    @mcp.tool()
    def filter_research_notes(
        filter_criteria: list[str] | None = None,
        order_by: str | None = None,
        facet_fields: list[str] | None = None,
        field_lists: list[str] | None = None,
        templates: list[dict[str, Any]] | None = None,
        date_range: dict[str, str] | None = None,
        entities: list[str] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter research notes by criteria such as author, entities, keywords, etc.

        Filter syntax examples:
          - 'note.author:"user"' to filter by author
          - 'note.entities.asset_id:"123456789"' to filter by asset ID
          - 'note.entities.issuer:"*ABC*"' to wildcard match issuer
          - Combine with AND/OR: 'note.author:"user" AND note.entities.asset_id:"123"'
          - 'Technology' to match anything containing "Technology"

        Args:
            filter_criteria: List of filter criteria strings.
            order_by: Sort order string (e.g. 'note.publish_time desc, note.author').
            facet_fields: List of fields to use for facet search.
            field_lists: When provided, only retrieve the specified fields.
            templates: List of template info dicts to filter by specific templates.
            date_range: Date range dict to fetch notes from (e.g. {"startDate": "...", "endDate": "..."}).
            entities: List of entity strings for which to fetch notes.
            page_size: Max number of notes to return (default 10).
            page_token: Page token from a previous call for pagination.
        """
        body: dict[str, Any] = {}
        query: dict[str, Any] = {}

        if filter_criteria is not None:
            query["filterCriteria"] = filter_criteria
        if order_by is not None:
            query["orderBy"] = order_by
        if facet_fields is not None:
            query["facetFields"] = facet_fields
        if field_lists is not None:
            query["fieldLists"] = field_lists
        if templates is not None:
            query["templates"] = templates
        if date_range is not None:
            query["dateRange"] = date_range
        if entities is not None:
            query["entities"] = entities
        if query:
            body["query"] = query
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_api("/researchNotes:filter", http_method="post", request_body=body)
