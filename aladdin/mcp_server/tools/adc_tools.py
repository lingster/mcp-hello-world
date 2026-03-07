import json

import snowflake.connector
from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.auth import _get_oauth_access_token
from mcp_server.config import server_config


def _get_snowflake_connection(
    database: str | None = None,
    schema: str | None = None,
) -> snowflake.connector.SnowflakeConnection:
    """Create a Snowflake connection using configured credentials."""
    conn_params: dict[str, str | dict[str, str]] = {
        "account": server_config.adc_account or "",
        "role": server_config.adc_role or "",
        "warehouse": server_config.adc_warehouse or "",
        "database": database or server_config.adc_database or "",
        "schema": schema or server_config.adc_schema or "",
        "session_parameters": {"QUERY_TAG": "QueryViaSDK-AladdinMCP"},
    }

    if server_config.auth_type == "OAuth":
        token = _get_oauth_access_token()
        if token:
            conn_params["authenticator"] = "oauth"
            conn_params["token"] = token
    else:
        conn_params["user"] = server_config.username or ""
        conn_params["password"] = server_config.password or ""

    return snowflake.connector.connect(**conn_params)


def register_adc_tools(mcp: FastMCP) -> None:
    """Register Aladdin Data Cloud (ADC) tools with the MCP server."""

    @mcp.tool()
    def query_adc(sql: str) -> str:
        """Execute a SQL query against Aladdin Data Cloud (Snowflake).

        Requires ADC connection to be configured via environment variables
        (account, role, warehouse, database, schema).

        Args:
            sql: SQL query to execute (e.g. 'SELECT * FROM my_table LIMIT 10')

        Returns:
            JSON string of query results (records orientation) or error message.
        """
        try:
            conn = _get_snowflake_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                data = [dict(zip(columns, row)) for row in rows]
                return json.dumps({
                    "row_count": len(data),
                    "columns": columns,
                    "data": data,
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
        try:
            conn = _get_snowflake_connection(database=database, schema=schema)
            try:
                cursor = conn.cursor()
                cursor.execute(f"SHOW TABLES IN {database}.{schema}")
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                data = [dict(zip(columns, row)) for row in rows]
                return json.dumps({
                    "database": database,
                    "schema": schema,
                    "tables": data,
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
        try:
            conn = _get_snowflake_connection(database=database, schema=schema)
            try:
                cursor = conn.cursor()
                cursor.execute(f"DESCRIBE TABLE {database}.{schema}.{table}")
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                data = [dict(zip(columns, row)) for row in rows]
                return json.dumps({
                    "database": database,
                    "schema": schema,
                    "table": table,
                    "columns": data,
                }, indent=2, default=str)
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Failed to describe table: {e}")
            return json.dumps({"error": str(e)})
