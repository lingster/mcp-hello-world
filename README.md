# MCP Hello World

A simple hello world [MCP](https://modelcontextprotocol.io/) server for use with Microsoft Copilot in VS Code.

## Tools

- **hello(name)** — Returns a greeting message
- **add(a, b)** — Adds two numbers together

## Setup

```bash
uv sync
```

## Usage with VS Code Copilot

1. Open this folder in VS Code
2. The server is configured in `.vscode/mcp.json` and will be discovered automatically
3. Open Copilot Chat and reference tools with `#` (e.g. `#hello`, `#add`)

## Running manually

```bash
uv run python server.py
```
