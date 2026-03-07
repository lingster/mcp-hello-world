"""Direct REST client for Aladdin Graph APIs, replacing aladdinsdk dependency."""

from __future__ import annotations

import datetime
import json
import re
import uuid
from functools import cached_property
from pathlib import Path
from typing import Any

import httpx
from loguru import logger

from mcp_server.config import OAuthConfig

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
    """Load all bundled swagger specs once.

    Returns:
        A tuple of (all_specs, merged_by_base_path).
        merged_by_base_path combines paths from specs sharing the same basePath.
    """
    all_specs: list[dict[str, Any]] = []
    merged: dict[str, dict[str, Any]] = {}
    if not _SWAGGER_DIR.exists():
        return all_specs, merged
    for swagger_file in _SWAGGER_DIR.glob("**/*.json"):
        try:
            spec = json.loads(swagger_file.read_text(encoding="utf-8"))
            all_specs.append(spec)
            base_path = spec.get("basePath", "").rstrip("/")
            if base_path:
                if base_path in merged:
                    # Merge paths from multiple specs sharing the same basePath
                    merged[base_path].setdefault("paths", {}).update(spec.get("paths", {}))
                else:
                    merged[base_path] = spec
        except Exception as e:
            logger.warning(f"Failed to parse swagger file {swagger_file}: {e}")
    return all_specs, merged


class AladdinRestClient:
    """Lightweight REST client for Aladdin Graph APIs."""

    def __init__(self, default_web_server: str, oauth_config: OAuthConfig) -> None:
        self._default_web_server = default_web_server.rstrip("/")
        self._oauth_config = oauth_config
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
