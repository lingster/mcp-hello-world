"""Direct REST client for Aladdin Graph APIs, replacing aladdinsdk dependency."""

from __future__ import annotations

import datetime
import json
import re
import time
import uuid
from functools import cached_property
from pathlib import Path
from typing import Any

import httpx
from loguru import logger

from mcp_server.config import LroConfig, OAuthConfig, PaginationConfig
from mcp_server.plugin_discovery import load_plugin_swagger_specs

_HEADER_KEY_REQUEST_ID = "VND.com.blackrock.Request-ID"
_HEADER_KEY_ORIGIN_TIMESTAMP = "VND.com.blackrock.Origin-Timestamp"

# Bundled swagger specs from aladdinsdk codegen (path relative to this file)
_SWAGGER_DIR = Path(__file__).parent / "swagger"

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_$.]*$")


def validate_sql_identifier(value: str, label: str) -> str:
    """Validate that a string is a safe SQL identifier."""
    if not _IDENTIFIER_RE.match(value):
        raise ValueError(f"Invalid {label}: {value!r}")
    return value


class OAuthTokenManager:
    """Manages OAuth token lifecycle for Aladdin API calls."""

    def __init__(self, config: OAuthConfig, default_web_server: str) -> None:
        self._config = config
        self._default_web_server = default_web_server
        self._access_token: str | None = None
        self._token_expiry: datetime.datetime | None = None
        # If a static token was provided via config, store it immediately
        if config.access_token:
            self._access_token = config.access_token

    def get_access_token(self, scopes: list[str] | None = None) -> str:
        """Return a valid access token, refreshing if needed."""
        now = datetime.datetime.now(datetime.timezone.utc)
        if self._access_token and self._token_expiry and now < self._token_expiry:
            return self._access_token

        # Static token with no expiry — always valid
        if self._access_token and self._token_expiry is None and self._config.access_token:
            return self._access_token

        token, ttl = self._request_token(scopes)
        self._access_token = token
        if isinstance(ttl, int):
            self._token_expiry = now + datetime.timedelta(seconds=ttl)
        return self._access_token

    def _request_token(self, scopes: list[str] | None = None) -> tuple[str, int | None]:
        url = self._get_token_url()
        data: dict[str, Any] = {
            "grant_type": self._config.auth_flow_type,
            "client_id": self._config.client_id,
            "client_secret": self._config.client_secret,
        }
        if scopes:
            data["scopes"] = scopes

        if self._config.auth_flow_type == "refresh_token" and self._config.refresh_token:
            data["refresh_token"] = self._config.refresh_token

        headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
        }
        proxies = {}
        if self._config.auth_server_proxy:
            proxies["https://"] = self._config.auth_server_proxy

        resp = self._http_client.post(url, headers=headers, params=data)

        if resp.status_code != 200:
            raise RuntimeError(f"OAuth token request failed ({resp.status_code}): {resp.text}")

        body = resp.json()
        return body["access_token"], body.get("expires_in")

    def _get_token_url(self) -> str:
        if self._config.auth_server_url:
            return f"{self._config.auth_server_url}/v1/token"
        return f"{self._default_web_server}/api/oauth2/default/v1/token"

    @cached_property
    def _http_client(self) -> httpx.Client:
        proxies = {}
        if self._config.auth_server_proxy:
            proxies["https://"] = self._config.auth_server_proxy
        return httpx.Client(proxies=proxies, verify=True, timeout=30.0)


def _build_request_headers() -> dict[str, str]:
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    return {
        _HEADER_KEY_REQUEST_ID: str(uuid.uuid4()),
        _HEADER_KEY_ORIGIN_TIMESTAMP: now.isoformat(),
    }


def _load_swagger_specs() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Load all bundled swagger specs and discovered plugin specs.

    Returns:
        A tuple of (all_specs, merged_by_base_path).
        merged_by_base_path combines paths from specs sharing the same basePath.
    """
    all_specs: list[dict[str, Any]] = []
    merged: dict[str, dict[str, Any]] = {}

    # 1. Load bundled swagger specs
    if _SWAGGER_DIR.exists():
        for swagger_file in _SWAGGER_DIR.glob("**/*.json"):
            try:
                spec = json.loads(swagger_file.read_text(encoding="utf-8"))
                all_specs.append(spec)
                base_path = spec.get("basePath", "").rstrip("/")
                if base_path:
                    if base_path in merged:
                        merged[base_path].setdefault("paths", {}).update(spec.get("paths", {}))
                    else:
                        merged[base_path] = spec
            except Exception as e:
                logger.warning(f"Failed to parse swagger file {swagger_file}: {e}")

    # 2. Load swagger specs from installed asdk_plugin_* packages
    plugin_specs, plugin_merged = load_plugin_swagger_specs()
    all_specs.extend(plugin_specs)
    for base_path, spec in plugin_merged.items():
        if base_path in merged:
            merged[base_path].setdefault("paths", {}).update(spec.get("paths", {}))
        else:
            merged[base_path] = spec

    bundled_count = len(all_specs) - len(plugin_specs)
    if plugin_specs:
        logger.info(
            f"Loaded {bundled_count} bundled + {len(plugin_specs)} plugin swagger spec(s)"
        )

    return all_specs, merged


class AladdinRestClient:
    """Lightweight REST client for Aladdin Graph APIs."""

    def __init__(
        self,
        default_web_server: str,
        oauth_config: OAuthConfig,
        lro_config: LroConfig | None = None,
        pagination_config: PaginationConfig | None = None,
    ) -> None:
        self._default_web_server = default_web_server.rstrip("/")
        self._oauth_config = oauth_config
        self._lro_config = lro_config or LroConfig()
        self._pagination_config = pagination_config or PaginationConfig()
        self._token_manager = OAuthTokenManager(oauth_config, self._default_web_server)
        self._http_client = httpx.Client(verify=True, timeout=60.0)
        self._all_swagger_specs, self._swagger_by_base_path = _load_swagger_specs()

    def _auth_headers(self, scopes: list[str] | None = None) -> dict[str, str]:
        headers = _build_request_headers()
        if self._oauth_config.auth_type == "OAuth":
            token = self._token_manager.get_access_token(scopes)
            headers["Authorization"] = f"Bearer {token}"
        if self._oauth_config.api_key:
            headers["APIKeyHeader"] = self._oauth_config.api_key
        return headers

    def call_api(
        self,
        base_path: str,
        endpoint_path: str,
        http_method: str = "get",
        request_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a REST call to an Aladdin Graph API endpoint."""
        # Build URL by concatenation — urljoin has unintuitive path-replacement behavior
        base = self._default_web_server + base_path.rstrip("/") + "/"
        url = base + endpoint_path.lstrip("/")

        headers = self._auth_headers()
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"

        method = http_method.upper()
        logger.debug(f"Calling {method} {url}")

        resp = self._http_client.request(
            method=method,
            url=url,
            headers=headers,
            json=request_body if method in ("POST", "PUT", "PATCH") else None,
            params=params,
        )

        if resp.status_code >= 400:
            raise RuntimeError(f"API call failed ({resp.status_code}): {resp.text}")

        return resp.json()

    # ── Swagger-based discovery ──────────────────────────────────────────

    def list_apis_from_swagger(self) -> list[dict[str, str]]:
        """List APIs available from bundled swagger specs."""
        apis: list[dict[str, str]] = []
        for spec in self._all_swagger_specs:
            info = spec.get("info", {})
            apis.append({
                "api_name": info.get("x-aladdin-api-id", info.get("title", "")),
                "title": info.get("title", ""),
                "version": info.get("version", ""),
                "base_path": spec.get("basePath", ""),
                "description": info.get("description", ""),
            })
        return apis

    def list_endpoints_from_swagger(self, base_path: str) -> list[dict[str, str]]:
        """List endpoints for an API identified by its base_path."""
        spec = self._swagger_by_base_path.get(base_path.rstrip("/"))
        if not spec:
            return []
        endpoints: list[dict[str, str]] = []
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method in ("get", "post", "put", "delete", "patch"):
                    endpoints.append({
                        "path": path,
                        "method": method,
                        "summary": details.get("summary", ""),
                        "operation_id": details.get("operationId", ""),
                    })
        return endpoints

    def get_endpoint_details_from_swagger(
        self, base_path: str, endpoint_path: str, http_method: str
    ) -> dict[str, Any] | None:
        """Get parameter details for a specific endpoint from the swagger spec."""
        spec = self._swagger_by_base_path.get(base_path.rstrip("/"))
        if not spec:
            return None
        path_obj = spec.get("paths", {}).get(endpoint_path, {})
        method_obj = path_obj.get(http_method.lower())
        if not method_obj:
            return None
        return {
            "operation_id": method_obj.get("operationId", ""),
            "summary": method_obj.get("summary", ""),
            "description": method_obj.get("description", ""),
            "parameters": method_obj.get("parameters", []),
        }

    # ── Pagination ───────────────────────────────────────────────────────

    def call_api_with_pagination(
        self,
        base_path: str,
        endpoint_path: str,
        http_method: str = "get",
        request_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        page_size: int | None = None,
        max_pages: int | None = None,
        timeout: int | None = None,
        interval: int | None = None,
    ) -> list[dict[str, Any]]:
        """Call an API endpoint with automatic pagination.

        Follows nextPageToken in responses to collect multiple pages.
        """
        page_size = page_size or self._pagination_config.max_page_size
        max_pages = max_pages or self._pagination_config.max_pages
        timeout = timeout or self._pagination_config.timeout
        interval = interval or self._pagination_config.interval

        # Inject page_size into request body or params
        if request_body is not None:
            request_body = {**request_body, "page_size": page_size}
        else:
            params = {**(params or {}), "page_size": page_size}

        all_pages: list[dict[str, Any]] = []
        start_time = time.time()
        page_token: str | None = None

        for page_num in range(max_pages):
            if time.time() - start_time >= timeout:
                logger.info(f"Pagination timed out after {page_num} page(s)")
                break

            # Set page token for subsequent pages
            if page_token:
                if request_body is not None:
                    request_body["page_token"] = page_token
                else:
                    params = {**(params or {}), "page_token": page_token}

            result = self.call_api(
                base_path=base_path,
                endpoint_path=endpoint_path,
                http_method=http_method,
                request_body=request_body,
                params=params,
            )
            all_pages.append(result)

            # Check for next page
            page_token = result.get("nextPageToken") or result.get("next_page_token")
            if not page_token:
                break

            if interval and page_num < max_pages - 1:
                time.sleep(interval)

        return all_pages

    # ── Long-Running Operations (LRO) ────────────────────────────────────

    def poll_lro(
        self,
        base_path: str,
        lro_id: str,
        status_endpoint: str = "/longRunningOperations/{id}",
        check_interval: int | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """Poll a long-running operation until completion or timeout.

        Args:
            base_path: API base path.
            lro_id: The long-running operation ID.
            status_endpoint: Endpoint template for checking status (must contain {id}).
            check_interval: Seconds between polls (default from config).
            timeout: Max seconds to wait (default from config).

        Returns:
            The final LRO status response.

        Raises:
            RuntimeError: If the operation times out.
        """
        check_interval = check_interval or self._lro_config.status_check_interval
        timeout = timeout or self._lro_config.status_check_timeout

        endpoint = status_endpoint.replace("{id}", lro_id)
        start_time = time.time()
        attempt = 0

        while True:
            result = self.call_api(
                base_path=base_path,
                endpoint_path=endpoint,
                http_method="get",
            )
            attempt += 1
            logger.debug(f"LRO poll attempt #{attempt}, done={result.get('done')}")

            if result.get("done"):
                return result

            elapsed = time.time() - start_time
            if elapsed + check_interval > timeout:
                raise RuntimeError(
                    f"Long-running operation {lro_id} timed out after {elapsed:.0f}s "
                    f"({attempt} attempts)"
                )

            time.sleep(check_interval)

    def start_and_poll_lro(
        self,
        base_path: str,
        start_endpoint: str,
        status_endpoint: str = "/longRunningOperations/{id}",
        http_method: str = "post",
        request_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        check_interval: int | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """Start a long-running operation and poll until completion.

        Args:
            base_path: API base path.
            start_endpoint: Endpoint to start the LRO.
            status_endpoint: Endpoint template for checking status.
            http_method: HTTP method for starting the LRO.
            request_body: Request body for starting the LRO.
            params: Query parameters for starting the LRO.
            check_interval: Seconds between polls.
            timeout: Max seconds to wait.

        Returns:
            The final LRO response.
        """
        start_response = self.call_api(
            base_path=base_path,
            endpoint_path=start_endpoint,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )

        if start_response.get("done"):
            return start_response

        lro_id = start_response.get("id")
        if not lro_id:
            raise RuntimeError(
                "LRO start response missing 'id' field — cannot poll for status"
            )

        return self.poll_lro(
            base_path=base_path,
            lro_id=lro_id,
            status_endpoint=status_endpoint,
            check_interval=check_interval,
            timeout=timeout,
        )
