"""MCP tools for the Aladdin Broker Contact API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_CONTACT_BASE_PATH = "/api/investment-operations/reference-data/contact/v1/"

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


def _call_contact_api(
    endpoint_path: str,
    http_method: str = "post",
    request_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Helper to call a Contact API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_CONTACT_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Contact API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def _build_contact_dict(
    first_name: str | None = None,
    last_name: str | None = None,
    external_account_id: str | None = None,
    contact_id: str | None = None,
    title: str | None = None,
    email_address: str | None = None,
    ftp_address: str | None = None,
    printer: str | None = None,
    voice_phone: str | None = None,
    fax_phone: str | None = None,
    street_address_1: str | None = None,
    street_address_2: str | None = None,
    city: str | None = None,
    contact_state: str | None = None,
    country_code: str | None = None,
    zip_code: str | None = None,
    web_type: str | None = None,
    remote_directory: str | None = None,
    login: str | None = None,
    port: int | None = None,
) -> dict[str, Any]:
    """Build a contact dict, filtering out None values."""
    mapping: list[tuple[str, str, Any]] = [
        ("id", "id", contact_id),
        ("firstName", "firstName", first_name),
        ("lastName", "lastName", last_name),
        ("externalAccountId", "externalAccountId", external_account_id),
        ("title", "title", title),
        ("emailAddress", "emailAddress", email_address),
        ("ftpAddress", "ftpAddress", ftp_address),
        ("printer", "printer", printer),
        ("voicePhone", "voicePhone", voice_phone),
        ("faxPhone", "faxPhone", fax_phone),
        ("streetAddress1", "streetAddress1", street_address_1),
        ("streetAddress2", "streetAddress2", street_address_2),
        ("city", "city", city),
        ("contactState", "contactState", contact_state),
        ("countryCode", "countryCode", country_code),
        ("zip", "zip", zip_code),
        ("webType", "webType", web_type),
        ("remoteDirectory", "remoteDirectory", remote_directory),
        ("login", "login", login),
        ("port", "port", port),
    ]
    return {api_key: value for _, api_key, value in mapping if value is not None}


def register_contact_tools(mcp: FastMCP) -> None:
    """Register Aladdin Contact API tools with the MCP server."""

    @mcp.tool()
    def get_contact(contact_id: str) -> str:
        """Retrieve a contact by its unique contact code.

        Args:
            contact_id: The unique contact code (id) of the contact to retrieve.
        """
        return _call_contact_api(
            f"/contacts/{contact_id}",
            http_method="get",
        )

    @mcp.tool()
    def create_contact(
        first_name: str,
        last_name: str,
        external_account_id: str,
        title: str | None = None,
        email_address: str | None = None,
        ftp_address: str | None = None,
        printer: str | None = None,
        voice_phone: str | None = None,
        fax_phone: str | None = None,
        street_address_1: str | None = None,
        street_address_2: str | None = None,
        city: str | None = None,
        contact_state: str | None = None,
        country_code: str | None = None,
        zip_code: str | None = None,
        web_type: str | None = None,
        remote_directory: str | None = None,
        login: str | None = None,
        port: int | None = None,
    ) -> str:
        """Create a new contact.

        Required fields: firstName, lastName, externalAccountId.
        Users need permissions under permType='asContMOD'.

        Args:
            first_name: First name of the contact.
            last_name: Last name of the contact.
            external_account_id: The external account ID (organization ID).
            title: Title of the contact.
            email_address: Email address.
            ftp_address: FTP address.
            printer: Printer.
            voice_phone: Phone number.
            fax_phone: Fax number.
            street_address_1: Street address line 1.
            street_address_2: Street address line 2.
            city: City.
            contact_state: State.
            country_code: Country code.
            zip_code: Zip code.
            web_type: Web type.
            remote_directory: FTP remote directory.
            login: FTP login token name.
            port: FTP host port number.
        """
        contact = _build_contact_dict(
            first_name=first_name,
            last_name=last_name,
            external_account_id=external_account_id,
            title=title,
            email_address=email_address,
            ftp_address=ftp_address,
            printer=printer,
            voice_phone=voice_phone,
            fax_phone=fax_phone,
            street_address_1=street_address_1,
            street_address_2=street_address_2,
            city=city,
            contact_state=contact_state,
            country_code=country_code,
            zip_code=zip_code,
            web_type=web_type,
            remote_directory=remote_directory,
            login=login,
            port=port,
        )
        body: dict[str, Any] = {"contact": contact}
        return _call_contact_api("/contacts:createContact", http_method="post", request_body=body)

    @mcp.tool()
    def update_contact(
        contact_id: str,
        first_name: str,
        last_name: str,
        external_account_id: str,
        title: str | None = None,
        email_address: str | None = None,
        ftp_address: str | None = None,
        printer: str | None = None,
        voice_phone: str | None = None,
        fax_phone: str | None = None,
        street_address_1: str | None = None,
        street_address_2: str | None = None,
        city: str | None = None,
        contact_state: str | None = None,
        country_code: str | None = None,
        zip_code: str | None = None,
        web_type: str | None = None,
        remote_directory: str | None = None,
        login: str | None = None,
        port: int | None = None,
    ) -> str:
        """Update an existing contact.

        Required fields: id, firstName, lastName, externalAccountId.
        Users need permissions under permType='asContMOD'.

        Args:
            contact_id: The unique contact code of the contact to update.
            first_name: First name of the contact.
            last_name: Last name of the contact.
            external_account_id: The external account ID (organization ID).
            title: Title of the contact.
            email_address: Email address.
            ftp_address: FTP address.
            printer: Printer.
            voice_phone: Phone number.
            fax_phone: Fax number.
            street_address_1: Street address line 1.
            street_address_2: Street address line 2.
            city: City.
            contact_state: State.
            country_code: Country code.
            zip_code: Zip code.
            web_type: Web type.
            remote_directory: FTP remote directory.
            login: FTP login token name.
            port: FTP host port number.
        """
        contact = _build_contact_dict(
            contact_id=contact_id,
            first_name=first_name,
            last_name=last_name,
            external_account_id=external_account_id,
            title=title,
            email_address=email_address,
            ftp_address=ftp_address,
            printer=printer,
            voice_phone=voice_phone,
            fax_phone=fax_phone,
            street_address_1=street_address_1,
            street_address_2=street_address_2,
            city=city,
            contact_state=contact_state,
            country_code=country_code,
            zip_code=zip_code,
            web_type=web_type,
            remote_directory=remote_directory,
            login=login,
            port=port,
        )
        body: dict[str, Any] = {"contact": contact}
        return _call_contact_api("/contacts:updateContact", http_method="post", request_body=body)

    @mcp.tool()
    def batch_create_contacts(
        contacts: list[dict[str, Any]],
    ) -> str:
        """Create multiple contacts in a single batch request (max 100).

        Required fields per contact: firstName, lastName, externalAccountId.
        Users need permissions under permType='asContMOD'.
        This is atomic: if any validation fails, none of the contacts are created.

        Args:
            contacts: List of contact dicts. Each dict can have:
                      firstName (str, required), lastName (str, required),
                      externalAccountId (str, required), title (str),
                      emailAddress (str), ftpAddress (str), printer (str),
                      voicePhone (str), faxPhone (str), streetAddress1 (str),
                      streetAddress2 (str), city (str), contactState (str),
                      countryCode (str), zip (str), webType (str),
                      remoteDirectory (str), login (str), port (int).
        """
        requests: list[dict[str, Any]] = [{"contact": c} for c in contacts]
        body: dict[str, Any] = {"requests": requests}
        return _call_contact_api("/contacts:batchCreate", http_method="post", request_body=body)

    @mcp.tool()
    def filter_contacts(
        external_account_id: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        contacts_codes: list[str] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> str:
        """Filter contacts by name + external account ID, external account ID alone, or contact codes.

        Args:
            external_account_id: External account ID to filter by.
            first_name: First name to filter by (use with last_name and external_account_id).
            last_name: Last name to filter by (use with first_name and external_account_id).
            contacts_codes: List of contact codes to look up directly.
            page_size: Maximum number of contacts to return (default server-side).
            page_token: Page token from a previous call for pagination.
        """
        query: dict[str, Any] = {}
        if external_account_id is not None:
            query["externalAccountId"] = external_account_id
        if first_name is not None:
            query["firstName"] = first_name
        if last_name is not None:
            query["lastName"] = last_name
        if contacts_codes is not None:
            query["contactsCodes"] = contacts_codes

        body: dict[str, Any] = {"contactsQuery": query}
        if page_size is not None:
            body["pageSize"] = page_size
        if page_token is not None:
            body["pageToken"] = page_token

        return _call_contact_api("/contacts:filter", http_method="post", request_body=body)
