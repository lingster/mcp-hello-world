import json

from loguru import logger
from mcp.server.fastmcp import FastMCP


def register_adc_tools(mcp: FastMCP) -> None:
    """Register Aladdin Data Cloud (ADC) tools with the MCP server."""

    @mcp.tool()
    def query_adc(sql: str) -> str:
        """Execute a SQL query against Aladdin Data Cloud (Snowflake).

        Requires ADC connection to be configured via environment variables or
        the AladdinSDK settings file (account, role, warehouse, database, schema).

        Args:
            sql: SQL query to execute (e.g. 'SELECT * FROM my_table LIMIT 10')

        Returns:
            JSON string of query results (records orientation) or error message.
        """
        from aladdinsdk.adc.client import ADCClient

        try:
            client = ADCClient()
            df = client.query_sql(sql)
            result = df.to_dict(orient="records")
            return json.dumps({
                "row_count": len(result),
                "columns": list(df.columns),
                "data": result,
            }, indent=2, default=str)
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
        from aladdinsdk.adc.client import ADCClient

        try:
            client = ADCClient(database=database, schema=schema)
            sql = f"SHOW TABLES IN {database}.{schema}"
            df = client.query_sql(sql)
            return json.dumps({
                "database": database,
                "schema": schema,
                "tables": df.to_dict(orient="records"),
            }, indent=2, default=str)
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
        from aladdinsdk.adc.client import ADCClient

        try:
            client = ADCClient(database=database, schema=schema)
            sql = f"DESCRIBE TABLE {database}.{schema}.{table}"
            df = client.query_sql(sql)
            return json.dumps({
                "database": database,
                "schema": schema,
                "table": table,
                "columns": df.to_dict(orient="records"),
            }, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to describe table: {e}")
            return json.dumps({"error": str(e)})
