from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx
from loguru import logger

from mcp_server.auth import get_auth_headers
from mcp_server.config import server_config

# Static API registry mirroring the aladdinsdk codegen_allow_list.yaml
API_REGISTRY: dict[str, dict[str, str]] = {
    "StudioNotificationAPI": {
        "version": "v1",
        "base_path": "/api/platform/studio/studio-notification/v1/",
    },
    "StudioSubscriptionAPI": {
        "version": "v1",
        "base_path": "/api/platform/studio/studio-notification/v1/",
    },
    "TokenAPI": {
        "version": "v1",
        "base_path": "/api/platform/infrastructure/token/v1/",
    },
    "TrainJourneyAPI": {
        "version": "v1",
        "base_path": "/api/reference-architecture/demo/train-journey/v1/",
    },
}

# Optional: path to directory containing swagger files for endpoint discovery
_SWAGGER_DIR: Path | None = None


def set_swagger_dir(path: Path) -> None:
    """Set the directory where swagger.json files are located for API discovery."""
    global _SWAGGER_DIR
    _SWAGGER_DIR = path


def list_api_names() -> list[str]:
    """Return all registered API names."""
    return list(API_REGISTRY.keys())


def get_api_base_url(api_name: str) -> str:
    """Build the full base URL for an API."""
    if api_name not in API_REGISTRY:
        raise ValueError(f"Unknown API: {api_name}. Available: {list_api_names()}")
    base_path = API_REGISTRY[api_name]["base_path"]
    return urljoin(server_config.default_web_server, base_path)


def get_api_endpoints(api_name: str) -> list[dict[str, str]]:
    """Parse swagger.json for the given API to list endpoints."""
    swagger = _load_swagger(api_name)
    if swagger is None:
        return []

    endpoints: list[dict[str, str]] = []
    for path, methods in swagger.get("paths", {}).items():
        for method, details in methods.items():
            if method.lower() in ("get", "post", "put", "delete", "patch"):
                endpoints.append({
                    "path": path,
                    "method": method.upper(),
                    "summary": details.get("summary", ""),
                    "operation_id": details.get("operationId", ""),
                })
    return endpoints


def get_endpoint_schema(api_name: str, endpoint_path: str, http_method: str) -> dict[str, Any] | None:
    """Get the request/response schema for a specific endpoint from swagger."""
    swagger = _load_swagger(api_name)
    if swagger is None:
        return None

    path_item = swagger.get("paths", {}).get(endpoint_path, {})
    operation = path_item.get(http_method.lower())
    if operation is None:
        return None

    result: dict[str, Any] = {
        "operation_id": operation.get("operationId", ""),
        "summary": operation.get("summary", ""),
        "description": operation.get("description", ""),
        "parameters": operation.get("parameters", []),
    }

    responses = operation.get("responses", {})
    if "200" in responses:
        result["response_schema"] = responses["200"].get("schema", {})

    return result


def call_api(
    api_name: str,
    endpoint_path: str,
    http_method: str = "GET",
    request_body: dict[str, Any] | None = None,
    query_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Make a REST API call to an Aladdin Graph API endpoint."""
    base_url = get_api_base_url(api_name)
    url = f"{base_url.rstrip('/')}{endpoint_path}"
    headers = get_auth_headers()

    logger.debug(f"API call: {http_method} {url}")

    try:
        with httpx.Client(verify=True, timeout=60.0) as client:
            response = client.request(
                method=http_method.upper(),
                url=url,
                headers=headers,
                json=request_body,
                params=query_params,
            )
            response.raise_for_status()

            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            return {"raw_response": response.text}

    except httpx.HTTPStatusError as e:
        logger.error(f"API call failed: {e.response.status_code} {e.response.text}")
        return {"error": f"HTTP {e.response.status_code}", "detail": e.response.text}
    except httpx.HTTPError as e:
        logger.error(f"API call error: {e}")
        return {"error": str(e)}


def _load_swagger(api_name: str) -> dict[str, Any] | None:
    """Load swagger.json for the given API from the swagger directory."""
    if _SWAGGER_DIR is None:
        logger.debug("No swagger directory configured")
        return None

    for swagger_path in _SWAGGER_DIR.rglob("swagger.json"):
        try:
            with swagger_path.open(encoding="utf-8") as f:
                swagger = json.load(f)
            api_id = swagger.get("info", {}).get("x-aladdin-spec-id", "")
            if api_name.replace("API", "") in api_id:
                return swagger
        except (json.JSONDecodeError, OSError) as e:
            logger.debug(f"Failed to read {swagger_path}: {e}")

    logger.debug(f"No swagger file found for {api_name}")
    return None
