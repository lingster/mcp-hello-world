"""MCP tools for the Aladdin User API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_USER_BASE_PATH = "/api/platform/identity/user/v1/"

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


def _call_user_api(
    endpoint_path: str,
    http_method: str = "get",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a User API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_USER_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"User API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def _build_profile_dict(
    email: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    middle_name: str | None = None,
    title: str | None = None,
    office_location: str | None = None,
    office_phone: str | None = None,
    alternative_phone: str | None = None,
    fax_phone: str | None = None,
    initials: str | None = None,
    department: str | None = None,
    client_abbreviation: str | None = None,
) -> dict[str, Any] | None:
    """Build a profile dict from individual fields, omitting None values."""
    mapping: dict[str, Any] = {
        "email": email,
        "firstName": first_name,
        "lastName": last_name,
        "middleName": middle_name,
        "title": title,
        "officeLocation": office_location,
        "officePhone": office_phone,
        "alternativePhone": alternative_phone,
        "faxPhone": fax_phone,
        "initials": initials,
        "department": department,
        "clientAbbreviation": client_abbreviation,
    }
    profile = {k: v for k, v in mapping.items() if v is not None}
    return profile if profile else None


def register_user_tools(mcp: FastMCP) -> None:
    """Register Aladdin User API tools with the MCP server."""

    @mcp.tool()
    def list_users(
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """List Aladdin users with optional pagination.

        Args:
            page_size: Maximum number of users to return per page.
            page_token: Token for retrieving the next page of results.
        """
        params: dict[str, Any] = {}
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token is not None:
            params["pageToken"] = page_token

        return _call_user_api("/users", http_method="get", params=params or None)

    @mcp.tool()
    def get_user(user_id: str) -> str:
        """Retrieve a single Aladdin user by their ID (login ID).

        Args:
            user_id: The unique login ID of the user to retrieve.
        """
        return _call_user_api(f"/users/{user_id}", http_method="get")

    @mcp.tool()
    def create_user(
        user_id: str,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        middle_name: str | None = None,
        title: str | None = None,
        office_location: str | None = None,
        office_phone: str | None = None,
        alternative_phone: str | None = None,
        fax_phone: str | None = None,
        initials: str | None = None,
        department: str | None = None,
        client_abbreviation: str | None = None,
        user_type: str | None = None,
        start_date: str | None = None,
        termination_date: str | None = None,
        locked: bool | None = None,
        active: bool | None = None,
        alternative_user_ids: dict[str, str] | None = None,
    ) -> str:
        """Create a new Aladdin user.

        Args:
            user_id: The login ID for the new user.
            email: User email address.
            first_name: First name.
            last_name: Last name.
            middle_name: Middle name.
            title: Job title.
            office_location: Office location.
            office_phone: Main phone number.
            alternative_phone: Alternative phone number.
            fax_phone: FAX number.
            initials: User's initials.
            department: Department (internally mapped to roles).
            client_abbreviation: Primary client abbreviation.
            user_type: User classification. One of USER_TYPE_UNSPECIFIED,
                       USER_TYPE_CLIENT_EMPLOYEE, USER_TYPE_PROVIDER,
                       USER_TYPE_SYSTEM, USER_TYPE_BLK_EMPLOYEE.
            start_date: Date user was activated (YYYY-MM-DD).
            termination_date: Date user was deactivated (YYYY-MM-DD).
            locked: Whether the user account is locked.
            active: Whether the user account is active.
            alternative_user_ids: Map of alternative user identifiers
                                  (e.g. {"clientUserId": "some-id"}).
        """
        body: dict[str, Any] = {"id": user_id}

        profile = _build_profile_dict(
            email=email,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            title=title,
            office_location=office_location,
            office_phone=office_phone,
            alternative_phone=alternative_phone,
            fax_phone=fax_phone,
            initials=initials,
            department=department,
            client_abbreviation=client_abbreviation,
        )
        if profile is not None:
            body["profile"] = profile
        if user_type is not None:
            body["userType"] = user_type
        if start_date is not None:
            body["startDate"] = start_date
        if termination_date is not None:
            body["terminationDate"] = termination_date
        if locked is not None:
            body["locked"] = locked
        if active is not None:
            body["active"] = active
        if alternative_user_ids is not None:
            body["alternativeUserIds"] = alternative_user_ids

        return _call_user_api("/users", http_method="post", request_body=body)

    @mcp.tool()
    def update_user(
        user_id: str,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        middle_name: str | None = None,
        title: str | None = None,
        office_location: str | None = None,
        office_phone: str | None = None,
        alternative_phone: str | None = None,
        fax_phone: str | None = None,
        initials: str | None = None,
        department: str | None = None,
        client_abbreviation: str | None = None,
        user_type: str | None = None,
        start_date: str | None = None,
        termination_date: str | None = None,
        locked: bool | None = None,
        active: bool | None = None,
        alternative_user_ids: dict[str, str] | None = None,
        update_mask: str | None = None,
    ) -> str:
        """Update an existing Aladdin user's properties.

        Only the fields provided will be updated. Use update_mask to specify
        exactly which fields to update.

        Args:
            user_id: The login ID of the user to update.
            email: User email address.
            first_name: First name.
            last_name: Last name.
            middle_name: Middle name.
            title: Job title.
            office_location: Office location.
            office_phone: Main phone number.
            alternative_phone: Alternative phone number.
            fax_phone: FAX number.
            initials: User's initials.
            department: Department (internally mapped to roles).
            client_abbreviation: Primary client abbreviation.
            user_type: User classification. One of USER_TYPE_UNSPECIFIED,
                       USER_TYPE_CLIENT_EMPLOYEE, USER_TYPE_PROVIDER,
                       USER_TYPE_SYSTEM, USER_TYPE_BLK_EMPLOYEE.
            start_date: Date user was activated (YYYY-MM-DD).
            termination_date: Date user was deactivated (YYYY-MM-DD).
            locked: Whether the user account is locked.
            active: Whether the user account is active.
            alternative_user_ids: Map of alternative user identifiers
                                  (e.g. {"clientUserId": "some-id"}).
            update_mask: Comma-separated list of fields to update
                         (e.g. "profile.email,active").
        """
        body: dict[str, Any] = {"id": user_id}

        profile = _build_profile_dict(
            email=email,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            title=title,
            office_location=office_location,
            office_phone=office_phone,
            alternative_phone=alternative_phone,
            fax_phone=fax_phone,
            initials=initials,
            department=department,
            client_abbreviation=client_abbreviation,
        )
        if profile is not None:
            body["profile"] = profile
        if user_type is not None:
            body["userType"] = user_type
        if start_date is not None:
            body["startDate"] = start_date
        if termination_date is not None:
            body["terminationDate"] = termination_date
        if locked is not None:
            body["locked"] = locked
        if active is not None:
            body["active"] = active
        if alternative_user_ids is not None:
            body["alternativeUserIds"] = alternative_user_ids

        params: dict[str, Any] | None = None
        if update_mask is not None:
            params = {"updateMask": update_mask}

        return _call_user_api(
            f"/users/{user_id}",
            http_method="patch",
            request_body=body,
            params=params,
        )

    @mcp.tool()
    def search_user(
        email: str | None = None,
        alternate_id_key: str | None = None,
        alternate_id_value: str | None = None,
    ) -> str:
        """Search for an Aladdin user by email or alternate ID. Returns exact matches.

        At least one search criterion should be provided: either email, or both
        alternate_id_key and alternate_id_value.

        Args:
            email: Email address to search for.
            alternate_id_key: The key of the alternate identifier
                              (e.g. "clientUserId").
            alternate_id_value: The value of the alternate identifier.
        """
        params: dict[str, Any] = {}
        if email is not None:
            params["email"] = email
        if alternate_id_key is not None:
            params["alternateId.alternateIdKey"] = alternate_id_key
        if alternate_id_value is not None:
            params["alternateId.alternateIdValue"] = alternate_id_value

        return _call_user_api("/users:search", http_method="get", params=params or None)
