import os
import sys
from pathlib import Path

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.config import server_config
from mcp_server.rest_client import set_swagger_dir
from mcp_server.tools.abor_lot_tools import register_abor_lot_tools
from mcp_server.tools.account_info_tools import register_account_info_tools
from mcp_server.tools.adc_dataset_tools import register_adc_dataset_tools
from mcp_server.tools.adc_tools import register_adc_tools
from mcp_server.tools.analyst_coverage_tools import register_analyst_coverage_tools
from mcp_server.tools.api_tools import register_api_tools
from mcp_server.tools.audit_tools import register_audit_tools
from mcp_server.tools.broker_confirm_routing_tools import register_broker_confirm_routing_tools
from mcp_server.tools.broker_desk_tools import register_broker_desk_tools
from mcp_server.tools.broker_external_alias_tools import register_broker_external_alias_tools
from mcp_server.tools.broker_tools import register_broker_tools
from mcp_server.tools.cash_ladder_tools import register_cash_ladder_tools
from mcp_server.tools.cid_reader_tools import register_cid_reader_tools
from mcp_server.tools.cid_writer_tools import register_cid_writer_tools
from mcp_server.tools.climate_tools import register_climate_tools
from mcp_server.tools.collateral_statement_tools import register_collateral_statement_tools
from mcp_server.tools.compliance_rule_assignment_tools import register_compliance_rule_assignment_tools
from mcp_server.tools.compliance_rule_tools import register_compliance_rule_tools
from mcp_server.tools.composite_membership_tools import register_composite_membership_tools
from mcp_server.tools.contact_tools import register_contact_tools
from mcp_server.tools.corporate_action_entitlement_tools import register_corporate_action_entitlement_tools
from mcp_server.tools.corporate_action_tools import register_corporate_action_tools
from mcp_server.tools.counter_party_settlement_instruction_template_tools import register_counter_party_settlement_instruction_template_tools
from mcp_server.tools.counter_party_settlement_instruction_tools import register_counter_party_settlement_instruction_tools
from mcp_server.tools.coupon_reset_tools import register_coupon_reset_tools
from mcp_server.tools.criterion_tools import register_criterion_tools
from mcp_server.tools.engagement_tools import register_engagement_tools
from mcp_server.tools.enriched_capital_flow_tools import register_enriched_capital_flow_tools
from mcp_server.tools.esg_data_tools import register_esg_data_tools
from mcp_server.tools.evaluator_analytics_tools import register_evaluator_analytics_tools
from mcp_server.tools.level_tools import register_level_tools
from mcp_server.tools.miscellaneous_cashflow_tools import register_miscellaneous_cashflow_tools
from mcp_server.tools.order_tools import register_order_tools
from mcp_server.tools.permission_tools import register_permission_tools
from mcp_server.tools.portfolio_configuration_tools import register_portfolio_configuration_tools
from mcp_server.tools.portfolio_group_tools import register_portfolio_group_tools
from mcp_server.tools.portfolio_toolkit_tools import register_portfolio_toolkit_tools
from mcp_server.tools.principal_interest_factor_tools import register_principal_interest_factor_tools
from mcp_server.tools.research_note_tools import register_research_note_tools
from mcp_server.tools.restricted_asset_tools import register_restricted_asset_tools
from mcp_server.tools.risk_config_tools import register_risk_config_tools
from mcp_server.tools.risk_custom_evaluation_metric_tools import register_risk_custom_evaluation_metric_tools
from mcp_server.tools.risk_exception_tools import register_risk_exception_tools
from mcp_server.tools.risk_rule_tools import register_risk_rule_tools
from mcp_server.tools.risk_task_tools import register_risk_task_tools
from mcp_server.tools.risk_workflow_tools import register_risk_workflow_tools
from mcp_server.tools.security_creation_tools import register_security_creation_tools
from mcp_server.tools.storage_tools import register_storage_tools
from mcp_server.tools.strategy_tools import register_strategy_tools
from mcp_server.tools.studio_notification_tools import register_studio_notification_tools
from mcp_server.tools.studio_subscription_tools import register_studio_subscription_tools
from mcp_server.tools.token_tools import register_token_tools
from mcp_server.tools.trade_tools import register_trade_tools
from mcp_server.tools.train_journey_tools import register_train_journey_tools
from mcp_server.tools.user_group_member_tools import register_user_group_member_tools
from mcp_server.tools.user_group_permission_tools import register_user_group_permission_tools
from mcp_server.tools.user_group_tools import register_user_group_tools
from mcp_server.tools.user_tools import register_user_tools
from mcp_server.tools.valuations_tools import register_valuations_tools
from mcp_server.tools.violation_tools import register_violation_tools
from mcp_server.tools.watchlist_tools import register_watchlist_tools

logger.remove()
logger.add(sys.stderr, level="DEBUG" if server_config.debug else "INFO")


def create_mcp_server() -> FastMCP:
    """Create and configure the Aladdin MCP server."""
    swagger_dir = os.getenv("ALADDIN_SWAGGER_DIR")
    if swagger_dir:
        set_swagger_dir(Path(swagger_dir))
        logger.info(f"Swagger directory configured: {swagger_dir}")

    mcp = FastMCP(
        name="aladdin-mcp",
        instructions=(
            "Aladdin MCP Server provides access to BlackRock's Aladdin platform. "
            "Use API tools to call Aladdin Graph APIs (with pagination and LRO support), "
            "ADC tools to query/write to Aladdin Data Cloud (Snowflake), "
            "and storage tools to manage S3 objects. "
            "Start by listing available APIs with list_available_apis(). "
            "Installed asdk_plugin_* packages are auto-discovered and available."
        ),
        host=server_config.host,
        port=server_config.port,
        streamable_http_path="/mcp",
    )

    # Core tools
    register_api_tools(mcp)
    register_adc_tools(mcp)
    register_storage_tools(mcp)

    # Domain-specific API tools
    register_abor_lot_tools(mcp)
    register_account_info_tools(mcp)
    register_adc_dataset_tools(mcp)
    register_analyst_coverage_tools(mcp)
    register_audit_tools(mcp)
    register_broker_confirm_routing_tools(mcp)
    register_broker_desk_tools(mcp)
    register_broker_external_alias_tools(mcp)
    register_broker_tools(mcp)
    register_cash_ladder_tools(mcp)
    register_cid_reader_tools(mcp)
    register_cid_writer_tools(mcp)
    register_climate_tools(mcp)
    register_collateral_statement_tools(mcp)
    register_compliance_rule_assignment_tools(mcp)
    register_compliance_rule_tools(mcp)
    register_composite_membership_tools(mcp)
    register_contact_tools(mcp)
    register_corporate_action_entitlement_tools(mcp)
    register_corporate_action_tools(mcp)
    register_counter_party_settlement_instruction_template_tools(mcp)
    register_counter_party_settlement_instruction_tools(mcp)
    register_coupon_reset_tools(mcp)
    register_criterion_tools(mcp)
    register_engagement_tools(mcp)
    register_enriched_capital_flow_tools(mcp)
    register_esg_data_tools(mcp)
    register_evaluator_analytics_tools(mcp)
    register_level_tools(mcp)
    register_miscellaneous_cashflow_tools(mcp)
    register_order_tools(mcp)
    register_permission_tools(mcp)
    register_portfolio_configuration_tools(mcp)
    register_portfolio_group_tools(mcp)
    register_portfolio_toolkit_tools(mcp)
    register_principal_interest_factor_tools(mcp)
    register_research_note_tools(mcp)
    register_restricted_asset_tools(mcp)
    register_risk_config_tools(mcp)
    register_risk_custom_evaluation_metric_tools(mcp)
    register_risk_exception_tools(mcp)
    register_risk_rule_tools(mcp)
    register_risk_task_tools(mcp)
    register_risk_workflow_tools(mcp)
    register_security_creation_tools(mcp)
    register_strategy_tools(mcp)
    register_studio_notification_tools(mcp)
    register_studio_subscription_tools(mcp)
    register_token_tools(mcp)
    register_trade_tools(mcp)
    register_train_journey_tools(mcp)
    register_user_group_member_tools(mcp)
    register_user_group_permission_tools(mcp)
    register_user_group_tools(mcp)
    register_user_tools(mcp)
    register_valuations_tools(mcp)
    register_violation_tools(mcp)
    register_watchlist_tools(mcp)

    logger.info(f"Registered MCP tools: {[t.name for t in mcp._tool_manager.list_tools()]}")
    return mcp


mcp = create_mcp_server()


def main() -> None:
    """Run the MCP server with the configured transport."""
    transport = server_config.transport

    if transport == "stdio":
        logger.info("Starting Aladdin MCP server (stdio transport)")
        mcp.run(transport="stdio")
    elif transport in ("streamable-http", "sse"):
        logger.info(
            f"Starting Aladdin MCP server ({transport}) on "
            f"{server_config.host}:{server_config.port}"
        )
        mcp.run(transport=transport)
    else:
        logger.error(f"Unsupported transport: {transport}")
        sys.exit(1)


if __name__ == "__main__":
    main()
