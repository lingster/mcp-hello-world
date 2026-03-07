import json

from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.aladdin_client import validate_sql_identifier
from mcp_server.config import server_config
from mcp_server.tools.api_tools import _get_client


def _get_snowflake_connection():  # type: ignore[no-untyped-def]
    """Create a Snowflake connection using config and OAuth token."""
    import snowflake.connector

    adc = server_config.adc
    oauth = server_config.oauth

    connect_params: dict = {
        "account": adc.account,
        "role": adc.role,
        "warehouse": adc.warehouse,
        "database": adc.database,
        "schema": adc.schema_name,
        "session_parameters": {"QUERY_TAG": "QueryViaSDK-AladdinMCP"},
    }

    if adc.authenticator == "oauth":
        token = adc.oauth_access_token
        if not token:
            # Reuse the shared client's token manager to benefit from token caching
            token = _get_client()._token_manager.get_access_token()
        connect_params["authenticator"] = "oauth"
        connect_params["token"] = token
    else:
        connect_params["user"] = oauth.username
        connect_params["password"] = oauth.password

    return snowflake.connector.connect(**connect_params)


def register_adc_tools(mcp: FastMCP) -> None:
    """Register Aladdin Data Cloud (ADC) tools with the MCP server."""

    @mcp.tool()
    def query_adc(sql: str) -> str:
        """Execute a SQL query against Aladdin Data Cloud (Snowflake).

        Requires ADC connection to be configured via environment variables
        (ASDK_ADC__CONN__ACCOUNT, ASDK_ADC__CONN__ROLE, etc.).

        Args:
            sql: SQL query to execute (e.g. 'SELECT * FROM my_table LIMIT 10')

        Returns:
            JSON string of query results or error message.
        """
        import pandas as pd

        try:
            conn = _get_snowflake_connection()
            try:
                df = pd.read_sql(sql, conn)
                result = df.to_dict(orient="records")
                return json.dumps({
                    "row_count": len(result),
                    "columns": list(df.columns),
                    "data": result,
                }, indent=2, default=str)
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"ADC query failed: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def get_adc_tables(database: str, schema: str) -> str:
        """List available tables in an Aladdin Data Cloud database schema.

        Args:
            database: Snowflake database name
            schema: Snowflake schema name

        Returns:
            JSON list of table names in the specified schema.
        """
        import pandas as pd

        try:
            db = validate_sql_identifier(database, "database")
            sch = validate_sql_identifier(schema, "schema")
            conn = _get_snowflake_connection()
            try:
                df = pd.read_sql(f"SHOW TABLES IN {db}.{sch}", conn)
                return json.dumps({
                    "database": database,
                    "schema": schema,
                    "tables": df.to_dict(orient="records"),
                }, indent=2, default=str)
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Failed to list ADC tables: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool()
    def describe_adc_table(database: str, schema: str, table: str) -> str:
        """Describe the columns and types of an Aladdin Data Cloud table.

        Args:
            database: Snowflake database name
            schema: Snowflake schema name
            table: Table name to describe

        Returns:
            JSON description of table columns and their types.
        """
        import pandas as pd

        try:
            db = validate_sql_identifier(database, "database")
            sch = validate_sql_identifier(schema, "schema")
            tbl = validate_sql_identifier(table, "table")
            conn = _get_snowflake_connection()
            try:
                df = pd.read_sql(f"DESCRIBE TABLE {db}.{sch}.{tbl}", conn)
                return json.dumps({
                    "database": database,
                    "schema": schema,
                    "table": table,
                    "columns": df.to_dict(orient="records"),
                }, indent=2, default=str)
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Failed to describe table: {e}")
            return json.dumps({"error": str(e)})
