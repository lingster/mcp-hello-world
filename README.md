# MCP Aladdin

This repository contains two [MCP](https://modelcontextprotocol.io/) (Model Context Protocol) servers:

1. **Hello World MCP Server** -- A minimal MCP server for verifying that VS Code can run and communicate with MCP servers. Use this to validate your setup before moving on to the Aladdin server.
2. **Aladdin MCP Server** -- A full-featured MCP server that connects to BlackRock's Aladdin platform APIs, enabling AI assistants to query and interact with Aladdin data.

## Prerequisites

- Python 3.13+ (hello-world) / Python 3.11+ (aladdin)
- [uv](https://docs.astral.sh/uv/) package manager
- [VS Code](https://code.visualstudio.com/) with GitHub Copilot extension

## Quick Start -- Hello World Server

The hello-world server is a sanity check to confirm MCP works in your VS Code environment.

### 1. Install dependencies

```bash
uv sync
```

### 2. Open in VS Code

Open this folder in VS Code. The server is auto-discovered via `.vscode/mcp.json` -- no extra configuration needed.

### 3. Test in Copilot Chat

Open Copilot Chat (`Ctrl+Shift+I` / `Cmd+Shift+I`) and reference the tools with `#`:

- `#hello` -- Returns a greeting message
- `#add` -- Adds two numbers together

### 4. Verify the server is running

Command Palette -> `MCP: List Servers` -- you should see `hello-world` listed.

### Running manually

```bash
uv run python server.py
```

## Aladdin MCP Server

The `aladdin/` folder contains an MCP server that exposes BlackRock's Aladdin platform to AI assistants. It provides access to Aladdin Graph APIs (with pagination and long-running operation support), Aladdin Data Cloud (Snowflake), and S3 storage.

For full documentation on tools, plugins, usage examples, and project structure, see the [Aladdin README](aladdin/README.md).

### Installing the Aladdin server

```bash
cd aladdin

# Core only (API tools)
uv pip install -e .

# With Aladdin Data Cloud (Snowflake) support
uv pip install -e ".[adc]"

# With S3 storage support
uv pip install -e ".[storage]"

# Everything (ADC + S3)
uv pip install -e ".[all]"
```

### Environment variable configuration

The Aladdin MCP server is configured entirely via environment variables. Create a `.env` file in the `aladdin/` directory, or export them in your shell. You can also use the interactive setup wizard:

```bash
aladdin-setup-oauth
```

For a step-by-step walkthrough of obtaining OAuth credentials from Aladdin Studio, see the [OAuth Setup Guide](docs/OAUTH_SETUP.md).

#### Server

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_HOST` | `0.0.0.0` | Server bind host |
| `MCP_PORT` | `8000` | Server bind port |
| `MCP_TRANSPORT` | `streamable-http` | Transport: `stdio`, `streamable-http`, or `sse` |
| `MCP_DEBUG` | `false` | Enable debug logging |
| `defaultWebServer` | *(required)* | Aladdin client environment URL (e.g. `https://your-client-env.blackrock.com`) |

#### OAuth / API Authentication

| Variable | Default | Description |
|----------|---------|-------------|
| `ASDK_API__AUTH_TYPE` | `OAuth` | `OAuth` or `Basic Auth` |
| `ASDK_API__AUTH_FLOW_TYPE` | `refresh_token` | `refresh_token` or `client_credentials` |
| `ASDK_API__OAUTH__CLIENT_ID` | | OAuth client ID *(required)* |
| `ASDK_API__OAUTH__CLIENT_SECRET` | | OAuth client secret *(required)* |
| `ASDK_API__OAUTH__REFRESH_TOKEN` | | OAuth refresh token *(required for refresh_token flow)* |
| `ASDK_API__OAUTH__ACCESS_TOKEN` | | Pre-generated access token (skips token request) |
| `ASDK_API__OAUTH__AUTH_SERVER_URL` | | Custom OAuth token endpoint |
| `ASDK_API__OAUTH__AUTH_SERVER_PROXY` | | HTTPS proxy for OAuth requests |
| `ASDK_API__TOKEN` | | API key (sent as `APIKeyHeader`) |
| `ASDK_USER_CREDENTIALS__USERNAME` | | Username (Basic Auth) |
| `ASDK_USER_CREDENTIALS__PASSWORD` | | Password (Basic Auth) |

#### Aladdin Data Cloud (Snowflake)

| Variable | Default | Description |
|----------|---------|-------------|
| `ASDK_ADC__CONN__ACCOUNT` | | Snowflake account identifier |
| `ASDK_ADC__CONN__ROLE` | | Snowflake role |
| `ASDK_ADC__CONN__WAREHOUSE` | | Snowflake warehouse |
| `ASDK_ADC__CONN__DATABASE` | | Default database |
| `ASDK_ADC__CONN__SCHEMA` | | Default schema |
| `ASDK_ADC__CONN__AUTHENTICATOR` | `oauth` | `oauth` or basic |
| `ASDK_ADC__OAUTH__ACCESS_TOKEN` | | Dedicated ADC OAuth token (falls back to API token) |

#### S3 Storage

| Variable | Default | Description |
|----------|---------|-------------|
| `ASDK_STORAGE__S3__ENDPOINT_URL` | | S3/StorageGrid endpoint URL |
| `ASDK_STORAGE__S3__ACCESS_KEY_ID` | | S3 access key |
| `ASDK_STORAGE__S3__SECRET_ACCESS_KEY` | | S3 secret key |
| `ASDK_STORAGE__S3__BUCKET_NAME` | | Default bucket name |

#### Pagination

| Variable | Default | Description |
|----------|---------|-------------|
| `ASDK_API__PAGINATION__MAX_PAGE_SIZE` | `100` | Default results per page |
| `ASDK_API__PAGINATION__MAX_PAGES` | `10` | Default max pages to fetch |
| `ASDK_API__PAGINATION__TIMEOUT` | `300` | Pagination timeout in seconds |
| `ASDK_API__PAGINATION__INTERVAL` | `0` | Delay between page requests in seconds |

#### Long-Running Operations

| Variable | Default | Description |
|----------|---------|-------------|
| `ASDK_API__LRO__STATUS_CHECK_INTERVAL` | `10` | Seconds between LRO status polls |
| `ASDK_API__LRO__STATUS_CHECK_TIMEOUT` | `300` | Max seconds to wait for LRO completion |

### Minimum .env example

For most developers, you only need these to get started:

```bash
defaultWebServer=https://your-client-env.blackrock.com
ASDK_API__OAUTH__CLIENT_ID=your-client-id
ASDK_API__OAUTH__CLIENT_SECRET=your-client-secret
ASDK_API__OAUTH__REFRESH_TOKEN=your-refresh-token
```

> **Important:** Never commit your `.env` file or credentials to version control. The `.gitignore` already excludes `.env` files.

### Running the Aladdin server

```bash
# Default: streamable-http on port 8000
aladdin-mcp

# stdio transport (for VS Code or Claude Code)
MCP_TRANSPORT=stdio aladdin-mcp

# SSE transport
MCP_TRANSPORT=sse aladdin-mcp
```

### VS Code integration

Both servers are pre-configured in `.vscode/mcp.json` and will be auto-discovered when you open this folder in VS Code. The Aladdin server uses stdio transport by default in VS Code.

To pass your credentials via VS Code, you can set environment variables in your shell before launching VS Code, or use a `.env` file.

## Further reading

- [Aladdin MCP Server -- full documentation](aladdin/README.md)
- [OAuth Setup Guide](docs/OAUTH_SETUP.md)
- [VS Code / Copilot Studio / M365 Copilot Setup Guide](docs/SETUP_GUIDE.md)
- [Model Context Protocol specification](https://modelcontextprotocol.io/)
