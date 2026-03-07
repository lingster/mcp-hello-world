# Aladdin MCP Server

MCP server that exposes BlackRock's Aladdin platform capabilities to AI assistants. Provides access to Aladdin Graph APIs, Aladdin Data Cloud (Snowflake), and S3 storage -- with automatic discovery of all installed AladdinSDK plugins.

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Core only (API tools)
uv pip install -e .

# With Aladdin Data Cloud (Snowflake) support
uv pip install -e ".[adc]"

# With S3 storage support
uv pip install -e ".[storage]"

# With all AladdinSDK plugins
uv pip install -e ".[plugins]"

# Everything (ADC + S3 + all plugins)
uv pip install -e ".[all]"
```

### OAuth Setup

Run the interactive setup wizard to configure authentication:

```bash
aladdin-setup-oauth
```

This creates an `.env` file (or shell export script) with your OAuth credentials. Alternatively, set environment variables directly (see [Configuration](#configuration)).

### Running the Server

```bash
# Default: streamable-http on port 8000
aladdin-mcp

# stdio transport (for CLI-based MCP clients like Claude Code)
MCP_TRANSPORT=stdio aladdin-mcp

# SSE transport
MCP_TRANSPORT=sse aladdin-mcp
```

### Connecting from Claude Code

Add to your Claude Code MCP config:

```json
{
  "mcpServers": {
    "aladdin": {
      "command": "aladdin-mcp",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "defaultWebServer": "https://your-client-env.blackrock.com",
        "ASDK_API__OAUTH__CLIENT_ID": "your-client-id",
        "ASDK_API__OAUTH__CLIENT_SECRET": "your-client-secret",
        "ASDK_API__OAUTH__REFRESH_TOKEN": "your-refresh-token"
      }
    }
  }
}
```

## Tools

The server exposes 15 tools across three categories:

### API Tools

| Tool | Description |
|------|-------------|
| `list_available_apis` | List all available APIs from bundled + plugin swagger specs |
| `list_api_endpoints` | List endpoints for a specific API by base_path |
| `get_api_endpoint_details` | Get parameter details for an endpoint from its swagger spec |
| `call_aladdin_api` | Call any Aladdin Graph API endpoint via REST |
| `call_aladdin_api_with_pagination` | Call an API with automatic page token pagination |
| `poll_long_running_operation` | Poll an existing LRO by ID until completion |
| `start_and_poll_long_running_operation` | Start an LRO and auto-poll until done |

### ADC Tools (Aladdin Data Cloud / Snowflake)

| Tool | Description |
|------|-------------|
| `query_adc` | Execute SQL queries against Snowflake |
| `get_adc_tables` | List tables in a database schema |
| `describe_adc_table` | Describe columns and types of a table |
| `write_adc` | Write row data to a Snowflake table |

### Storage Tools (S3)

| Tool | Description |
|------|-------------|
| `list_s3_objects` | List objects in an S3 bucket |
| `download_s3_object` | Download and return text content of an S3 object |
| `upload_s3_object` | Upload text content as an S3 object |
| `delete_s3_object` | Delete an S3 object |

## AladdinSDK Plugins

The server automatically discovers and exposes all installed `asdk_plugin_*` packages. These plugins provide additional Aladdin Graph APIs beyond the four bundled with the core server.

### Available Plugins

| Plugin | Domain | Install |
|--------|--------|---------|
| `asdk_plugin_accounting` | Accounting APIs | `uv pip install asdk_plugin_accounting` |
| `asdk_plugin_analytics` | Analytics APIs | `uv pip install asdk_plugin_analytics` |
| `asdk_plugin_clients` | Client management APIs | `uv pip install asdk_plugin_clients` |
| `asdk_plugin_compliance` | Compliance APIs | `uv pip install asdk_plugin_compliance` |
| `asdk_plugin_data` | Data APIs | `uv pip install asdk_plugin_data` |
| `asdk_plugin_investment_operations` | Investment operations APIs | `uv pip install asdk_plugin_investment_operations` |
| `asdk_plugin_investment_research` | Investment research APIs | `uv pip install asdk_plugin_investment_research` |
| `asdk_plugin_platform` | Platform APIs | `uv pip install asdk_plugin_platform` |
| `asdk_plugin_portfolio` | Portfolio APIs | `uv pip install asdk_plugin_portfolio` |
| `asdk_plugin_portfolio_management` | Portfolio management APIs | `uv pip install asdk_plugin_portfolio_management` |
| `asdk_plugin_trading` | Trading APIs (e.g. OrderAPI) | `uv pip install asdk_plugin_trading` |

### Installing All Plugins

```bash
# Install all plugins at once via the extras group
uv pip install -e ".[plugins]"
```

### How Plugin Discovery Works

1. On startup, the server scans for installed Python packages prefixed with `asdk_plugin_`
2. Each plugin's `api_registry` module is imported and `fetch_api_details_for_asdk()` is called
3. Swagger specs from plugins are loaded and merged alongside the bundled specs
4. All plugin APIs become available through the standard API tools (`list_available_apis`, `call_aladdin_api`, etc.)

No code changes or additional configuration are needed -- just install a plugin package and restart the server.

### Using Plugin APIs

```
# 1. List all APIs (includes plugin APIs)
list_available_apis()

# 2. Find endpoints for a plugin API (use the base_path from step 1)
list_api_endpoints(base_path="/api/trading/order/v1/")

# 3. Get parameter details
get_api_endpoint_details(
    base_path="/api/trading/order/v1/",
    endpoint_path="/orders:filter",
    http_method="post"
)

# 4. Call the endpoint
call_aladdin_api(
    base_path="/api/trading/order/v1/",
    endpoint_path="/orders:filter",
    http_method="post",
    request_body={"filter": "status = 'OPEN'"}
)
```

### Building Custom Plugins

See the [AladdinSDK Plugin Builder](https://github.com/blackrock/aladdinsdk-plugin-builder) for details on creating your own domain-specific plugins. Any package following the `asdk_plugin_*` naming convention with an `api_registry` module will be auto-discovered.

## Usage Examples

### Paginated API Calls

For APIs that return large result sets with `nextPageToken`:

```
call_aladdin_api_with_pagination(
    base_path="/api/trading/order/v1/",
    endpoint_path="/orders:filter",
    http_method="post",
    request_body={"filter": "status = 'OPEN'"},
    page_size=50,
    max_pages=5
)
```

### Long-Running Operations (LRO)

Some APIs start async operations that must be polled for completion:

```
# Option 1: Start and poll in one call
start_and_poll_long_running_operation(
    base_path="/api/reference-architecture/demo/train-journey/v1/",
    start_endpoint="/trainJourneys:batchProcess",
    http_method="post",
    request_body={"data": "..."},
    check_interval=10,
    timeout=300
)

# Option 2: Poll an existing LRO by ID
poll_long_running_operation(
    base_path="/api/reference-architecture/demo/train-journey/v1/",
    lro_id="abc-123-def",
    check_interval=5,
    timeout=120
)
```

### ADC Queries

```
# Query data
query_adc(sql="SELECT * FROM my_database.my_schema.my_table LIMIT 100")

# Explore schema
get_adc_tables(database="MY_DB", schema="PUBLIC")
describe_adc_table(database="MY_DB", schema="PUBLIC", table="POSITIONS")

# Write data
write_adc(
    data=[{"col1": "value1", "col2": 42}, {"col1": "value2", "col2": 99}],
    table_name="MY_TABLE",
    database="MY_DB",
    schema="PUBLIC",
    auto_create_table=True
)
```

### S3 Storage

```
# List objects
list_s3_objects(bucket_name="my-bucket")

# Upload content
upload_s3_object(key="reports/output.json", content='{"result": "ok"}')

# Download content
download_s3_object(key="reports/output.json")

# Delete object
delete_s3_object(key="reports/output.json")
```

## Configuration

All configuration is via environment variables. Use `aladdin-setup-oauth` for interactive setup, or set them directly.

### Server

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_HOST` | `0.0.0.0` | Server bind host |
| `MCP_PORT` | `8000` | Server bind port |
| `MCP_TRANSPORT` | `streamable-http` | Transport: `stdio`, `streamable-http`, or `sse` |
| `MCP_DEBUG` | `false` | Enable debug logging |
| `defaultWebServer` | | Aladdin client environment URL (required) |

### OAuth / API Authentication

| Variable | Default | Description |
|----------|---------|-------------|
| `ASDK_API__AUTH_TYPE` | `OAuth` | `OAuth` or `Basic Auth` |
| `ASDK_API__AUTH_FLOW_TYPE` | `refresh_token` | `refresh_token` or `client_credentials` |
| `ASDK_API__OAUTH__CLIENT_ID` | | OAuth client ID |
| `ASDK_API__OAUTH__CLIENT_SECRET` | | OAuth client secret |
| `ASDK_API__OAUTH__REFRESH_TOKEN` | | OAuth refresh token |
| `ASDK_API__OAUTH__ACCESS_TOKEN` | | Pre-generated access token (skips token request) |
| `ASDK_API__OAUTH__AUTH_SERVER_URL` | | Custom OAuth token endpoint |
| `ASDK_API__OAUTH__AUTH_SERVER_PROXY` | | HTTPS proxy for OAuth requests |
| `ASDK_API__TOKEN` | | API key (sent as `APIKeyHeader`) |
| `ASDK_USER_CREDENTIALS__USERNAME` | | Username (Basic Auth) |
| `ASDK_USER_CREDENTIALS__PASSWORD` | | Password (Basic Auth) |

### Aladdin Data Cloud (Snowflake)

| Variable | Default | Description |
|----------|---------|-------------|
| `ASDK_ADC__CONN__ACCOUNT` | | Snowflake account identifier |
| `ASDK_ADC__CONN__ROLE` | | Snowflake role |
| `ASDK_ADC__CONN__WAREHOUSE` | | Snowflake warehouse |
| `ASDK_ADC__CONN__DATABASE` | | Default database |
| `ASDK_ADC__CONN__SCHEMA` | | Default schema |
| `ASDK_ADC__CONN__AUTHENTICATOR` | `oauth` | `oauth` or basic |
| `ASDK_ADC__OAUTH__ACCESS_TOKEN` | | Dedicated ADC OAuth token (falls back to API token) |

### S3 Storage

| Variable | Default | Description |
|----------|---------|-------------|
| `ASDK_STORAGE__S3__ENDPOINT_URL` | | S3/StorageGrid endpoint URL |
| `ASDK_STORAGE__S3__ACCESS_KEY_ID` | | S3 access key |
| `ASDK_STORAGE__S3__SECRET_ACCESS_KEY` | | S3 secret key |
| `ASDK_STORAGE__S3__BUCKET_NAME` | | Default bucket name |

### Pagination

| Variable | Default | Description |
|----------|---------|-------------|
| `ASDK_API__PAGINATION__MAX_PAGE_SIZE` | `100` | Default results per page |
| `ASDK_API__PAGINATION__MAX_PAGES` | `10` | Default max pages to fetch |
| `ASDK_API__PAGINATION__TIMEOUT` | `300` | Pagination timeout in seconds |
| `ASDK_API__PAGINATION__INTERVAL` | `0` | Delay between page requests in seconds |

### Long-Running Operations

| Variable | Default | Description |
|----------|---------|-------------|
| `ASDK_API__LRO__STATUS_CHECK_INTERVAL` | `10` | Seconds between LRO status polls |
| `ASDK_API__LRO__STATUS_CHECK_TIMEOUT` | `300` | Max seconds to wait for LRO completion |

## Project Structure

```
aladdin/
  mcp_server/
    __init__.py
    main.py                  # FastMCP server creation and entry point
    config.py                # Pydantic config models from environment variables
    aladdin_client.py        # REST client with OAuth, pagination, and LRO support
    plugin_discovery.py      # Auto-discovery of asdk_plugin_* packages
    models/
      schemas.py             # Pydantic request/response models
    tools/
      api_tools.py           # API discovery, calling, pagination, LRO tools
      adc_tools.py           # Snowflake query, describe, and write tools
      storage_tools.py       # S3 list, download, upload, delete tools
    swagger/                 # Bundled OpenAPI specs (4 core APIs)
      studio_notification_api.json
      studio_subscription_api.json
      token_api.json
      train_journey_api.json
  setup_oauth.py             # Interactive OAuth configuration wizard
  pyproject.toml
```
