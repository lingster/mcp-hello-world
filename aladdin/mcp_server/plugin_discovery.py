"""Discover installed asdk_plugin_* packages and load their swagger specs.

Mirrors the plugin discovery mechanism from aladdinsdk.api.registry without
requiring aladdinsdk as a dependency.
"""

from __future__ import annotations

import importlib
import json
import pkgutil
from pathlib import Path
from typing import Any

from loguru import logger

_DOMAIN_SDK_PACKAGE_NAME_PREFIX = "asdk_plugin"
_DOMAIN_SDK_API_REGISTRY_MODULE = "api_registry"


def _find_swagger_file(api_detail: dict[str, Any]) -> Path | None:
    """Resolve the swagger file path for a plugin API entry."""
    # Plugin may provide an explicit swagger_file_path
    swagger_path = api_detail.get("swagger_file_path")
    if swagger_path:
        path = Path(swagger_path) if not isinstance(swagger_path, Path) else swagger_path
        if path.exists():
            return path

    # Fallback: derive from api_module_path (swagger.json lives next to the codegen module)
    module_path = api_detail.get("api_module_path", "")
    if not module_path:
        return None

    try:
        mod = importlib.import_module(module_path)
        if mod.__file__:
            candidate = Path(mod.__file__).parent / "swagger.json"
            if candidate.exists():
                return candidate
    except Exception:
        pass

    return None


def discover_plugin_apis() -> list[dict[str, Any]]:
    """Scan for installed asdk_plugin_* packages and collect their API metadata.

    Returns:
        List of dicts with keys: api_name, api_version, host_url_path,
        swagger_file_path (resolved Path or None), api_module_path.
    """
    apis: list[dict[str, Any]] = []

    plugin_modules = [
        mod_info.name
        for mod_info in pkgutil.iter_modules()
        if mod_info.name.startswith(_DOMAIN_SDK_PACKAGE_NAME_PREFIX)
    ]

    if plugin_modules:
        logger.info(f"Discovered {len(plugin_modules)} plugin(s): {plugin_modules}")

    for module_name in plugin_modules:
        try:
            registry_mod = importlib.import_module(
                f"{module_name}.{_DOMAIN_SDK_API_REGISTRY_MODULE}"
            )
            plugin_apis: list[dict[str, Any]] = registry_mod.fetch_api_details_for_asdk()

            for api_detail in plugin_apis:
                swagger_path = _find_swagger_file(api_detail)
                apis.append({
                    "api_name": api_detail.get("api_name", ""),
                    "api_version": api_detail.get("api_version", ""),
                    "host_url_path": api_detail.get("host_url_path", ""),
                    "api_module_path": api_detail.get("api_module_path", ""),
                    "swagger_file_path": swagger_path,
                    "plugin": module_name,
                })

            logger.info(
                f"Plugin {module_name}: loaded {len(plugin_apis)} API(s)"
            )
        except Exception as e:
            logger.warning(
                f"Unable to load plugin {module_name}: {e}. "
                "APIs from this plugin will not be available."
            )

    return apis


def load_plugin_swagger_specs() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """Load swagger specs from all discovered plugins.

    Returns:
        A tuple of (all_specs, merged_by_base_path) matching the format used
        by AladdinRestClient._load_swagger_specs.
    """
    all_specs: list[dict[str, Any]] = []
    merged: dict[str, dict[str, Any]] = {}

    for api_info in discover_plugin_apis():
        swagger_path = api_info.get("swagger_file_path")
        if swagger_path is None or not swagger_path.exists():
            # No swagger file — create a minimal spec from metadata so the API
            # still appears in list_available_apis and can be called by base_path.
            host_url = api_info.get("host_url_path", "").strip("/")
            if host_url:
                base_path = f"/{host_url}/"
                minimal_spec: dict[str, Any] = {
                    "basePath": base_path,
                    "info": {
                        "title": api_info.get("api_name", "Unknown"),
                        "version": api_info.get("api_version", ""),
                        "x-aladdin-api-id": api_info.get("api_name", ""),
                        "description": (
                            f"API from plugin {api_info.get('plugin', 'unknown')}. "
                            "No swagger spec available — use call_aladdin_api with known endpoints."
                        ),
                    },
                    "paths": {},
                }
                all_specs.append(minimal_spec)
                merged.setdefault(base_path.rstrip("/"), minimal_spec)
            continue

        try:
            spec = json.loads(swagger_path.read_text(encoding="utf-8"))
            all_specs.append(spec)
            base_path = spec.get("basePath", "").rstrip("/")
            if base_path:
                if base_path in merged:
                    merged[base_path].setdefault("paths", {}).update(
                        spec.get("paths", {})
                    )
                else:
                    merged[base_path] = spec
        except Exception as e:
            logger.warning(
                f"Failed to parse swagger from plugin "
                f"{api_info.get('plugin', '?')}: {e}"
            )

    return all_specs, merged
