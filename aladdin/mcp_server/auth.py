import datetime
import uuid

import httpx
from loguru import logger

from mcp_server.config import server_config

_HEADER_KEY_REQUEST_ID = "VND.com.blackrock.Request-ID"
_HEADER_KEY_ORIGIN_TIMESTAMP = "VND.com.blackrock.Origin-Timestamp"

_cached_access_token: str | None = None
_cached_token_expiry: datetime.datetime | None = None


def build_request_headers() -> dict[str, str]:
    """Build base Aladdin request headers with unique request ID and timestamp."""
    return {
        _HEADER_KEY_REQUEST_ID: str(uuid.uuid1()),
        _HEADER_KEY_ORIGIN_TIMESTAMP: (
            datetime.datetime.now(tz=datetime.timezone.utc)
            .replace(microsecond=0)
            .isoformat()
        ),
    }


def get_auth_headers() -> dict[str, str]:
    """Get combined request + auth headers for an Aladdin API call."""
    headers = build_request_headers()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"

    if server_config.api_key:
        headers["APIKeyHeader"] = server_config.api_key

    if server_config.auth_type == "OAuth":
        token = _get_oauth_access_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
    elif server_config.auth_type == "Basic Auth":
        if server_config.username and server_config.password:
            import base64
            credentials = base64.b64encode(
                f"{server_config.username}:{server_config.password}".encode()
            ).decode()
            headers["Authorization"] = f"Basic {credentials}"

    return headers


def _get_oauth_access_token() -> str | None:
    """Get a valid OAuth access token, fetching a new one if needed."""
    global _cached_access_token, _cached_token_expiry

    if server_config.oauth_access_token:
        return server_config.oauth_access_token

    if _cached_access_token and _cached_token_expiry:
        if datetime.datetime.now(tz=datetime.timezone.utc) < _cached_token_expiry:
            return _cached_access_token

    token, ttl = _fetch_token_from_oauth_server()
    if token:
        _cached_access_token = token
        if isinstance(ttl, int):
            _cached_token_expiry = (
                datetime.datetime.now(tz=datetime.timezone.utc)
                + datetime.timedelta(seconds=ttl)
            )
        return token

    token, expires_at = _fetch_token_from_okta_sidecar()
    if token:
        _cached_access_token = token
        if expires_at:
            _cached_token_expiry = datetime.datetime.fromisoformat(str(expires_at))
        return token

    logger.warning("Unable to obtain OAuth access token from any source")
    return None


def _fetch_token_from_oauth_server() -> tuple[str | None, int | None]:
    """Fetch access token from the OAuth token endpoint."""
    client_id = server_config.oauth_client_id
    client_secret = server_config.oauth_client_secret
    refresh_token = server_config.oauth_refresh_token
    auth_flow_type = server_config.auth_flow_type

    if not client_id or not client_secret:
        logger.debug("OAuth client_id/client_secret not configured, skipping OAuth server")
        return None, None

    if auth_flow_type == "refresh_token" and not refresh_token:
        logger.debug("Refresh token not configured for refresh_token flow")
        return None, None

    token_url = _build_token_url()

    data: dict[str, str] = {
        "grant_type": auth_flow_type or "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    if refresh_token and auth_flow_type == "refresh_token":
        data["refresh_token"] = refresh_token

    proxies = {}
    if server_config.oauth_auth_server_proxy:
        proxies["https://"] = server_config.oauth_auth_server_proxy

    try:
        with httpx.Client(verify=True, proxy=proxies.get("https://")) as client:
            response = client.post(
                token_url,
                headers={
                    "accept": "application/json",
                    "content-type": "application/x-www-form-urlencoded",
                },
                params=data,
            )
        if response.status_code == 200:
            resp_json = response.json()
            return resp_json.get("access_token"), resp_json.get("expires_in")
        else:
            logger.debug(f"OAuth token request failed: {response.status_code} {response.text}")
    except httpx.HTTPError as e:
        logger.debug(f"OAuth token request error: {e}")

    return None, None


def _build_token_url() -> str:
    """Build the OAuth token endpoint URL."""
    if server_config.oauth_auth_server_url:
        return f"{server_config.oauth_auth_server_url}/v1/token"
    return f"{server_config.default_web_server}/api/oauth2/default/v1/token"


def _fetch_token_from_okta_sidecar(scopes: list[str] | None = None) -> tuple[str | None, str | None]:
    """Attempt to fetch access token from okta-sidecar (compute mode)."""
    import os
    sidecar_url = os.getenv("OKTA_SIDECAR_SERVER_URL", "http://localhost:8081")

    try:
        with httpx.Client() as client:
            ping = client.get(f"{sidecar_url}/v1/ping", timeout=2.0)
            if ping.status_code != 200:
                return None, None
    except httpx.HTTPError:
        logger.debug("Okta sidecar not available")
        return None, None

    params: dict[str, str] = {}
    if scopes:
        params["scopes"] = ",".join(scopes)

    try:
        with httpx.Client() as client:
            resp = client.get(f"{sidecar_url}/v1/access-token", params=params, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("accessToken"), data.get("expiresAt")
    except httpx.HTTPError as e:
        logger.debug(f"Okta sidecar token fetch error: {e}")

    return None, None
