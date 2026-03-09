"""MCP tools for the Aladdin Risk Rule API (Risk Governance - Rules)."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_RISK_RULE_BASE_PATH = "/api/analytics/oversight/governance/v1/"

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
    """Helper to call a Risk Rule API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_RISK_RULE_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Risk Rule API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_risk_rule_tools(mcp: FastMCP) -> None:
    """Register Aladdin Risk Rule API tools with the MCP server."""

    # ── Long-running operations ──────────────────────────────────────────

    @mcp.tool()
    def get_risk_rule_longrunning_operation(operation_id: str) -> str:
        """Get the status of a long-running Risk Rule API operation.

        Clients can use this method to poll the operation result at intervals
        as recommended by the API service.

        Args:
            operation_id: The unique identifier of the long-running operation.
        """
        return _call_api(
            f"/longrunningoperations/{operation_id}",
            http_method="get",
        )

    # ── Rules ────────────────────────────────────────────────────────────

    @mcp.tool()
    def list_risk_rules(
        filter: str | None = None,
        effective_date: str | None = None,
    ) -> str:
        """Retrieve a list of Risk Rules matching the search parameters provided.

        Args:
            filter: Filter expression to narrow results.
            effective_date: Effective date for the rules (YYYY-MM-DD).
        """
        params: dict[str, Any] = {}
        if filter is not None:
            params["filter"] = filter
        if effective_date is not None:
            params["effectiveDate"] = effective_date

        return _call_api("/rules", http_method="get", params=params or None)

    @mcp.tool()
    def create_risk_rule(rule: dict[str, Any]) -> str:
        """Create a new Risk Rule in DRAFT status.

        Args:
            rule: The rule definition dict. Keys may include:
                  name (str), tierKey (str), categoryKey (str),
                  subCategoryKey (str), conditions (list[dict]),
                  splitExceptions (bool), priority (int),
                  evaluator (dict), effectiveDate (str YYYY-MM-DD),
                  permissionScopes (list[str]), ruleSetting (dict).
        """
        return _call_api("/rules", http_method="post", request_body=rule)

    @mcp.tool()
    def update_risk_rule(
        rule: dict[str, Any],
        update_mask: str | None = None,
    ) -> str:
        """Update an existing Risk Rule.

        Creates a new DRAFT version if the supplied Rule is in an APPROVED state.

        Args:
            rule: The rule definition dict containing the fields to update.
                  Must include id (str). Other keys: name, tierKey,
                  categoryKey, subCategoryKey, conditions, splitExceptions,
                  priority, evaluator, effectiveDate, permissionScopes,
                  ruleSetting.
            update_mask: Comma-separated list of fields to update
                         (e.g. "name,conditions").
        """
        params: dict[str, Any] | None = None
        if update_mask is not None:
            params = {"updateMask": update_mask}

        return _call_api("/rules", http_method="put", request_body=rule, params=params)

    @mcp.tool()
    def approve_risk_rule(rule: dict[str, Any]) -> str:
        """Approve an existing version of a Risk Rule that is in DRAFT state.

        Args:
            rule: The rule definition dict. Must include id (str) and
                  version (str) identifying the DRAFT version to approve.
        """
        return _call_api("/rules:approve", http_method="post", request_body=rule)

    @mcp.tool()
    def retrieve_risk_rules_by_id(
        rule_ids: list[str],
        effective_date: str | None = None,
        rule_states: list[str] | None = None,
    ) -> str:
        """Bulk retrieve Risk Rules by their IDs.

        This operation is optimised for retrieving a large number of Rules
        using the Rule's natural key.

        Args:
            rule_ids: List of rule IDs to retrieve.
            effective_date: Retrieve the version effective on the given date
                            (YYYY-MM-DD). Defaults to current date.
            rule_states: Filter by rule states (e.g. DRAFT, APPROVED).
        """
        body: dict[str, Any] = {"ruleIds": rule_ids}
        if effective_date is not None:
            body["effectiveDate"] = effective_date
        if rule_states is not None:
            body["ruleStates"] = rule_states

        return _call_api("/rules:retrieveRiskRulesById", http_method="post", request_body=body)

    @mcp.tool()
    def list_subscribed_risk_rules_by_portfolio(
        portfolio_id: str,
        filter: str | None = None,
        effective_date: str | None = None,
    ) -> str:
        """Retrieve Risk Rules subscribed to by a specific portfolio.

        Args:
            portfolio_id: The portfolio ID to look up subscribed rules for.
            filter: Filter expression to narrow results.
            effective_date: Effective date for the rules (YYYY-MM-DD).
        """
        params: dict[str, Any] = {"portfolioId": portfolio_id}
        if filter is not None:
            params["filter"] = filter
        if effective_date is not None:
            params["effectiveDate"] = effective_date

        return _call_api(
            "/rules:listSubscribedRiskRulesByPortfolio",
            http_method="get",
            params=params,
        )

    # ── Rule versions ────────────────────────────────────────────────────

    @mcp.tool()
    def list_risk_rule_versions(
        rule_id: str,
        version: str | None = None,
    ) -> str:
        """List all or one specific version for a given Risk Rule.

        Args:
            rule_id: The ID of the rule to list versions for.
            version: A specific version number to retrieve (optional).
        """
        params: dict[str, Any] = {"ruleId": rule_id}
        if version is not None:
            params["version"] = version

        return _call_api("/ruleVersions", http_method="get", params=params)

    @mcp.tool()
    def list_risk_rule_versions_info(rule_id: str) -> str:
        """List all version info for a given Risk Rule.

        Args:
            rule_id: The ID of the rule to list version info for.
        """
        return _call_api(
            "/ruleVersionsInfo",
            http_method="get",
            params={"ruleId": rule_id},
        )

    # ── Rule subscriptions ───────────────────────────────────────────────

    @mcp.tool()
    def list_risk_rule_subscriptions(
        rule_id: str,
        effective_date: str | None = None,
    ) -> str:
        """List all portfolio subscriptions for a given Rule and effective date.

        Args:
            rule_id: The ID of the rule to list subscriptions for.
            effective_date: Effective date for the subscriptions (YYYY-MM-DD).
        """
        params: dict[str, Any] = {"ruleId": rule_id}
        if effective_date is not None:
            params["effectiveDate"] = effective_date

        return _call_api("/ruleSubscriptions", http_method="get", params=params)

    @mcp.tool()
    def batch_create_risk_rule_subscriptions(
        requests: list[dict[str, Any]],
    ) -> str:
        """Subscribe one or more portfolios to existing Risk Rules.

        Args:
            requests: List of subscription request dicts. Each dict should
                      contain a riskRuleSubscription dict with keys:
                      portfolioId (str), ruleId (str), startDate (str YYYY-MM-DD),
                      endDate (str YYYY-MM-DD, optional), ruleOverrideId (str, optional).
        """
        body: dict[str, Any] = {"requests": requests}
        return _call_api("/ruleSubscriptions:batchCreate", http_method="post", request_body=body)

    @mcp.tool()
    def batch_update_risk_rule_subscriptions(
        requests: list[dict[str, Any]],
    ) -> str:
        """Modify the start and/or end date of one or more existing portfolio subscriptions.

        Args:
            requests: List of update request dicts. Each dict should contain
                      a riskRuleSubscription dict with keys: id (str),
                      portfolioId (str), ruleId (str), startDate (str),
                      endDate (str). May also include forceUpdate (bool).
        """
        body: dict[str, Any] = {"requests": requests}
        return _call_api("/ruleSubscriptions:batchUpdate", http_method="post", request_body=body)

    @mcp.tool()
    def batch_cancel_risk_rule_subscriptions(
        requests: list[dict[str, Any]],
    ) -> str:
        """Cancel one or more existing Risk Rule Subscriptions.

        Invalidates rather than ends the Subscriptions by changing their state
        to CANCELLED.

        Args:
            requests: List of cancellation request dicts. Each dict should
                      contain a riskRuleSubscription dict with keys:
                      id (str), portfolioId (str), ruleId (str).
        """
        body: dict[str, Any] = {"requests": requests}
        return _call_api("/ruleSubscriptions:batchCancel", http_method="post", request_body=body)

    @mcp.tool()
    def retrieve_risk_rule_subscriptions(
        rule_ids: list[str],
        effective_date: str | None = None,
        rule_subscription_states: list[str] | None = None,
    ) -> str:
        """Retrieve subscriptions in bulk for a set of Rules.

        Args:
            rule_ids: List of rule IDs to retrieve subscriptions for.
            effective_date: Effective date for subscriptions (YYYY-MM-DD).
                            Defaults to current date.
            rule_subscription_states: Filter by subscription states.
        """
        query: dict[str, Any] = {"ruleIds": rule_ids}
        if effective_date is not None:
            query["effectiveDate"] = effective_date
        if rule_subscription_states is not None:
            query["ruleSubscriptionStates"] = rule_subscription_states

        body: dict[str, Any] = {"query": query}
        return _call_api("/ruleSubscriptions:retrieve", http_method="post", request_body=body)

    @mcp.tool()
    def retrieve_risk_rule_subscriptions_by_rules(
        rule_ids: list[str],
        effective_date: str | None = None,
    ) -> str:
        """Bulk retrieve subscriptions for a set of Rules by rule IDs.

        Args:
            rule_ids: List of rule IDs to retrieve subscriptions for.
            effective_date: Effective date for subscriptions (YYYY-MM-DD).
                            Defaults to current date.
        """
        body: dict[str, Any] = {"ruleIds": rule_ids}
        if effective_date is not None:
            body["effectiveDate"] = effective_date

        return _call_api(
            "/ruleSubscriptions:retrieveByRules",
            http_method="post",
            request_body=body,
        )

    # ── Rule overrides ───────────────────────────────────────────────────

    @mcp.tool()
    def list_risk_rule_overrides(
        rule_id: str | None = None,
        effective_date: str | None = None,
        rule_override_ids: list[str] | None = None,
    ) -> str:
        """Retrieve all Overrides for a given Risk Rule.

        Args:
            rule_id: The ID of the rule to list overrides for.
            effective_date: Effective date for the overrides (YYYY-MM-DD).
            rule_override_ids: Specific override IDs to retrieve.
        """
        params: dict[str, Any] = {}
        if rule_id is not None:
            params["ruleId"] = rule_id
        if effective_date is not None:
            params["effectiveDate"] = effective_date
        if rule_override_ids is not None:
            params["ruleOverrideIds"] = rule_override_ids

        return _call_api("/ruleOverrides", http_method="get", params=params or None)

    @mcp.tool()
    def batch_create_risk_rule_overrides(
        requests: list[dict[str, Any]],
    ) -> str:
        """Create one or more Overrides for a given Risk Rule.

        Args:
            requests: List of create request dicts. Each dict should contain
                      a riskRuleOverride dict with keys: ruleId (str),
                      name (str), conditionOverrides (list[dict]),
                      effectiveDate (str YYYY-MM-DD).
        """
        body: dict[str, Any] = {"requests": requests}
        return _call_api("/ruleOverrides:batchCreate", http_method="post", request_body=body)

    @mcp.tool()
    def batch_update_risk_rule_overrides(
        requests: list[dict[str, Any]],
    ) -> str:
        """Update one or more existing Risk Rule Overrides.

        Creates a new DRAFT version if the Overrides supplied are in
        APPROVED state.

        Args:
            requests: List of update request dicts. Each dict should contain
                      a riskRuleOverride dict with keys: id (str),
                      ruleId (str), name (str), conditionOverrides (list[dict]),
                      effectiveDate (str YYYY-MM-DD).
        """
        body: dict[str, Any] = {"requests": requests}
        return _call_api("/ruleOverrides:batchUpdate", http_method="post", request_body=body)

    @mcp.tool()
    def batch_approve_risk_rule_overrides(
        requests: list[dict[str, Any]],
    ) -> str:
        """Approve one or more existing Risk Rule Overrides that are in DRAFT state.

        Args:
            requests: List of approval request dicts. Each dict should contain
                      a riskRuleOverride dict with keys: id (str),
                      ruleId (str), version (str).
        """
        body: dict[str, Any] = {"requests": requests}
        return _call_api("/ruleOverrides:batchApprove", http_method="post", request_body=body)

    # ── Rule override versions ───────────────────────────────────────────

    @mcp.tool()
    def list_risk_rule_override_versions(
        rule_override_id: str,
        version: str | None = None,
    ) -> str:
        """List all or one specific version for a given Rule Override.

        Args:
            rule_override_id: The ID of the rule override to list versions for.
            version: A specific version number to retrieve (optional).
        """
        params: dict[str, Any] = {"ruleOverrideId": rule_override_id}
        if version is not None:
            params["version"] = version

        return _call_api("/ruleOverrideVersions", http_method="get", params=params)
