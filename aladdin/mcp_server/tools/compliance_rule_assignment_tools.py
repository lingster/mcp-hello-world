"""MCP tools for the Aladdin Compliance Rule Assignment API."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import AladdinRestClient
from mcp_server.config import server_config

_COMPLIANCE_RULE_ASSIGNMENT_BASE_PATH = "/api/compliance/state/compliance-rule-assignment/v1/"

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
    """Helper to call a Compliance Rule Assignment API endpoint and return JSON string."""
    try:
        result = _get_client().call_api(
            base_path=_COMPLIANCE_RULE_ASSIGNMENT_BASE_PATH,
            endpoint_path=endpoint_path,
            http_method=http_method,
            request_body=request_body,
            params=params,
        )
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        logger.error(f"Compliance Rule Assignment API call failed: {http_method.upper()} {endpoint_path}: {e}")
        return json.dumps({"error": str(e)})


def register_compliance_rule_assignment_tools(mcp: FastMCP) -> None:
    """Register Aladdin Compliance Rule Assignment API tools with the MCP server."""

    @mcp.tool()
    def create_compliance_rule_assignment(
        portfolio_names: list[str],
        approval_category: str | None = None,
        rule_assignment_source: str | None = None,
        category: str | None = None,
        effective_date: str | None = None,
        effective: bool | None = None,
        review_state: str | None = None,
        implementation_note: str | None = None,
        excerpt: str | None = None,
        reference: str | None = None,
        labels: list[str] | None = None,
        regulator: str | None = None,
        deadline: str | None = None,
        jurisdiction_country_code: str | None = None,
        documentation_link: str | None = None,
        override_action: str | None = None,
        resolution_action: str | None = None,
        termination_date: str | None = None,
        constraint_applicability_type: str | None = None,
        assignment_name: str | None = None,
        resolution_requires_four_eyes_approval: bool | None = None,
        prohibition_rule_configurations: dict[str, Any] | None = None,
        concentration_rule_configurations: dict[str, Any] | None = None,
        value_at_risk_rule_configurations: dict[str, Any] | None = None,
        scripted_rule_configurations: dict[str, Any] | None = None,
        trade_rule_configurations: dict[str, Any] | None = None,
        counterparty_rule_configurations: dict[str, Any] | None = None,
        disclosure_rule_configurations: dict[str, Any] | None = None,
        info_rule_configurations: dict[str, Any] | None = None,
    ) -> str:
        """Create a new compliance rule assignment.

        Assigns compliance rules to one or more portfolios with optional
        rule configurations and metadata.

        Args:
            portfolio_names: Portfolio name(s) to which the rule is assigned.
            approval_category: Approval category for the assignment.
            rule_assignment_source: Source of the rule assignment (e.g. client guideline or regulatory).
            category: Category of the rule assignment.
            effective_date: Date when this rule assignment is activated (ISO 8601).
            effective: Whether the rule assignment is currently effective.
            review_state: Review state of the assignment.
            implementation_note: Implementation note for the assignment.
            excerpt: Documentation excerpt for the rule assignment.
            reference: Documentation reference links.
            labels: Labels associated with the assignment.
            regulator: Regulating body of the rule assignment.
            deadline: Deadline for the rule assignment.
            jurisdiction_country_code: Jurisdiction country code.
            documentation_link: Documentation links for the rule assignment.
            override_action: Override action documentation.
            resolution_action: Resolution action documentation.
            termination_date: Date when this rule assignment would be terminated (ISO 8601).
            constraint_applicability_type: Constraint applicability type.
            assignment_name: Name of the assignment.
            resolution_requires_four_eyes_approval: Whether violation resolution requires four-eyes approval.
            prohibition_rule_configurations: Rule names and customizable components of each Prohibition Rule.
            concentration_rule_configurations: Rule names and customizable components of each Concentration Rule.
            value_at_risk_rule_configurations: Rule names and customizable components of each VaR Rule.
            scripted_rule_configurations: Rule names and customizable components of each Scripted Rule.
            trade_rule_configurations: Rule names and customizable components of each Trade Rule.
            counterparty_rule_configurations: Rule names and customizable components of each Counterparty Rule.
            disclosure_rule_configurations: Rule names and customizable components of each Disclosure Rule.
            info_rule_configurations: Rule names and customizable components of each Information Rule.
        """
        body: dict[str, Any] = {
            "portfolioNames": portfolio_names,
        }
        if approval_category is not None:
            body["approvalCategory"] = approval_category
        if rule_assignment_source is not None:
            body["ruleAssignmentSource"] = rule_assignment_source
        if category is not None:
            body["category"] = category
        if effective_date is not None:
            body["effectiveDate"] = effective_date
        if effective is not None:
            body["effective"] = effective
        if review_state is not None:
            body["reviewState"] = review_state
        if implementation_note is not None:
            body["implementationNote"] = implementation_note
        if excerpt is not None:
            body["excerpt"] = excerpt
        if reference is not None:
            body["reference"] = reference
        if labels is not None:
            body["labels"] = labels
        if regulator is not None:
            body["regulator"] = regulator
        if deadline is not None:
            body["deadline"] = deadline
        if jurisdiction_country_code is not None:
            body["jurisdictionCountryCode"] = jurisdiction_country_code
        if documentation_link is not None:
            body["documentationLink"] = documentation_link
        if override_action is not None:
            body["overrideAction"] = override_action
        if resolution_action is not None:
            body["resolutionAction"] = resolution_action
        if termination_date is not None:
            body["terminationDate"] = termination_date
        if constraint_applicability_type is not None:
            body["constraintApplicabilityType"] = constraint_applicability_type
        if assignment_name is not None:
            body["assignmentName"] = assignment_name
        if resolution_requires_four_eyes_approval is not None:
            body["resolutionRequiresFourEyesApproval"] = resolution_requires_four_eyes_approval
        if prohibition_rule_configurations is not None:
            body["prohibitionRuleConfigurations"] = prohibition_rule_configurations
        if concentration_rule_configurations is not None:
            body["concentrationRuleConfigurations"] = concentration_rule_configurations
        if value_at_risk_rule_configurations is not None:
            body["valueAtRiskRuleConfigurations"] = value_at_risk_rule_configurations
        if scripted_rule_configurations is not None:
            body["scriptedRuleConfigurations"] = scripted_rule_configurations
        if trade_rule_configurations is not None:
            body["tradeRuleConfigurations"] = trade_rule_configurations
        if counterparty_rule_configurations is not None:
            body["counterpartyRuleConfigurations"] = counterparty_rule_configurations
        if disclosure_rule_configurations is not None:
            body["disclosureRuleConfigurations"] = disclosure_rule_configurations
        if info_rule_configurations is not None:
            body["infoRuleConfigurations"] = info_rule_configurations

        return _call_api("/complianceRuleAssignments", http_method="post", request_body=body)

    @mcp.tool()
    def get_compliance_rule_assignment(assignment_id: str) -> str:
        """Retrieve a compliance rule assignment by its ID.

        Args:
            assignment_id: The unique ID of the compliance rule assignment to retrieve.
        """
        return _call_api(
            f"/complianceRuleAssignments/{assignment_id}",
            http_method="get",
        )

    @mcp.tool()
    def update_compliance_rule_assignment(
        assignment_id: str,
        portfolio_names: list[str] | None = None,
        approval_category: str | None = None,
        rule_assignment_source: str | None = None,
        category: str | None = None,
        effective_date: str | None = None,
        effective: bool | None = None,
        review_state: str | None = None,
        implementation_note: str | None = None,
        excerpt: str | None = None,
        reference: str | None = None,
        labels: list[str] | None = None,
        regulator: str | None = None,
        deadline: str | None = None,
        jurisdiction_country_code: str | None = None,
        documentation_link: str | None = None,
        override_action: str | None = None,
        resolution_action: str | None = None,
        termination_date: str | None = None,
        constraint_applicability_type: str | None = None,
        assignment_name: str | None = None,
        resolution_requires_four_eyes_approval: bool | None = None,
        prohibition_rule_configurations: dict[str, Any] | None = None,
        concentration_rule_configurations: dict[str, Any] | None = None,
        value_at_risk_rule_configurations: dict[str, Any] | None = None,
        scripted_rule_configurations: dict[str, Any] | None = None,
        trade_rule_configurations: dict[str, Any] | None = None,
        counterparty_rule_configurations: dict[str, Any] | None = None,
        disclosure_rule_configurations: dict[str, Any] | None = None,
        info_rule_configurations: dict[str, Any] | None = None,
        update_mask: str | None = None,
    ) -> str:
        """Update an existing compliance rule assignment.

        Only the fields provided will be updated. Use update_mask to specify
        exactly which fields to update.

        Args:
            assignment_id: The unique ID of the compliance rule assignment to update.
            portfolio_names: Portfolio name(s) to which the rule is assigned.
            approval_category: Approval category for the assignment.
            rule_assignment_source: Source of the rule assignment.
            category: Category of the rule assignment.
            effective_date: Date when this rule assignment is activated (ISO 8601).
            effective: Whether the rule assignment is currently effective.
            review_state: Review state of the assignment.
            implementation_note: Implementation note for the assignment.
            excerpt: Documentation excerpt for the rule assignment.
            reference: Documentation reference links.
            labels: Labels associated with the assignment.
            regulator: Regulating body of the rule assignment.
            deadline: Deadline for the rule assignment.
            jurisdiction_country_code: Jurisdiction country code.
            documentation_link: Documentation links for the rule assignment.
            override_action: Override action documentation.
            resolution_action: Resolution action documentation.
            termination_date: Date when this rule assignment would be terminated (ISO 8601).
            constraint_applicability_type: Constraint applicability type.
            assignment_name: Name of the assignment.
            resolution_requires_four_eyes_approval: Whether violation resolution requires four-eyes approval.
            prohibition_rule_configurations: Rule names and customizable components of each Prohibition Rule.
            concentration_rule_configurations: Rule names and customizable components of each Concentration Rule.
            value_at_risk_rule_configurations: Rule names and customizable components of each VaR Rule.
            scripted_rule_configurations: Rule names and customizable components of each Scripted Rule.
            trade_rule_configurations: Rule names and customizable components of each Trade Rule.
            counterparty_rule_configurations: Rule names and customizable components of each Counterparty Rule.
            disclosure_rule_configurations: Rule names and customizable components of each Disclosure Rule.
            info_rule_configurations: Rule names and customizable components of each Information Rule.
            update_mask: Comma-separated list of fields to update (e.g. "effective,category").
        """
        body: dict[str, Any] = {"id": assignment_id}
        if portfolio_names is not None:
            body["portfolioNames"] = portfolio_names
        if approval_category is not None:
            body["approvalCategory"] = approval_category
        if rule_assignment_source is not None:
            body["ruleAssignmentSource"] = rule_assignment_source
        if category is not None:
            body["category"] = category
        if effective_date is not None:
            body["effectiveDate"] = effective_date
        if effective is not None:
            body["effective"] = effective
        if review_state is not None:
            body["reviewState"] = review_state
        if implementation_note is not None:
            body["implementationNote"] = implementation_note
        if excerpt is not None:
            body["excerpt"] = excerpt
        if reference is not None:
            body["reference"] = reference
        if labels is not None:
            body["labels"] = labels
        if regulator is not None:
            body["regulator"] = regulator
        if deadline is not None:
            body["deadline"] = deadline
        if jurisdiction_country_code is not None:
            body["jurisdictionCountryCode"] = jurisdiction_country_code
        if documentation_link is not None:
            body["documentationLink"] = documentation_link
        if override_action is not None:
            body["overrideAction"] = override_action
        if resolution_action is not None:
            body["resolutionAction"] = resolution_action
        if termination_date is not None:
            body["terminationDate"] = termination_date
        if constraint_applicability_type is not None:
            body["constraintApplicabilityType"] = constraint_applicability_type
        if assignment_name is not None:
            body["assignmentName"] = assignment_name
        if resolution_requires_four_eyes_approval is not None:
            body["resolutionRequiresFourEyesApproval"] = resolution_requires_four_eyes_approval
        if prohibition_rule_configurations is not None:
            body["prohibitionRuleConfigurations"] = prohibition_rule_configurations
        if concentration_rule_configurations is not None:
            body["concentrationRuleConfigurations"] = concentration_rule_configurations
        if value_at_risk_rule_configurations is not None:
            body["valueAtRiskRuleConfigurations"] = value_at_risk_rule_configurations
        if scripted_rule_configurations is not None:
            body["scriptedRuleConfigurations"] = scripted_rule_configurations
        if trade_rule_configurations is not None:
            body["tradeRuleConfigurations"] = trade_rule_configurations
        if counterparty_rule_configurations is not None:
            body["counterpartyRuleConfigurations"] = counterparty_rule_configurations
        if disclosure_rule_configurations is not None:
            body["disclosureRuleConfigurations"] = disclosure_rule_configurations
        if info_rule_configurations is not None:
            body["infoRuleConfigurations"] = info_rule_configurations

        params: dict[str, Any] | None = None
        if update_mask is not None:
            params = {"updateMask": update_mask}

        return _call_api(
            f"/complianceRuleAssignments/{assignment_id}",
            http_method="patch",
            request_body=body,
            params=params,
        )

    @mcp.tool()
    def filter_compliance_rule_assignments(
        rule_name: str | None = None,
        portfolio_name: str | None = None,
        assignment_ids: list[str] | None = None,
        page_token: str | None = None,
        page_size: int | None = None,
    ) -> str:
        """Filter compliance rule assignments by rule name, portfolio, or assignment IDs.

        Args:
            rule_name: Compliance rule name to filter by.
            portfolio_name: Portfolio name to filter by.
            assignment_ids: List of assignment IDs to filter by.
            page_token: Page token from a previous call for pagination.
            page_size: Maximum number of assignments to return per page.
        """
        body: dict[str, Any] = {}

        query: dict[str, Any] = {}
        if rule_name is not None:
            query["ruleName"] = rule_name
        if portfolio_name is not None:
            query["portfolioName"] = portfolio_name
        if assignment_ids is not None:
            query["assignmentIds"] = assignment_ids
        if query:
            body["query"] = query

        if page_token is not None:
            body["pageToken"] = page_token
        if page_size is not None:
            body["pageSize"] = page_size

        return _call_api("/complianceRuleAssignments:filter", http_method="post", request_body=body)
