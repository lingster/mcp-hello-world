# MCP Hello World — Setup Guide

This guide covers how to use the `mcp-hello-world` server with Microsoft Copilot across three platforms:

1. **VS Code (GitHub Copilot)** — local stdio transport
2. **Microsoft Copilot Studio** — remote HTTP transport for sharing with other users
3. **Microsoft 365 Copilot (Declarative Agents)** — extend M365 Copilot via the Agents Toolkit

---

## 1. VS Code — GitHub Copilot (Local)

This is the simplest setup. The server runs locally on each developer's machine.

### Prerequisites

- [VS Code](https://code.visualstudio.com/) with GitHub Copilot extension
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager

### Steps

1. **Clone the repo and install dependencies:**

   ```bash
   git clone git@github.com:lingster/mcp-hello-world.git
   cd mcp-hello-world
   uv sync
   ```

2. **Open the folder in VS Code.** The server is auto-discovered via `.vscode/mcp.json`:

   ```json
   {
     "servers": {
       "hello-world": {
         "type": "stdio",
         "command": "uv",
         "args": ["run", "python", "server.py"]
       }
     }
   }
   ```

3. **Open Copilot Chat** (`Ctrl+Shift+I` / `Cmd+Shift+I`).

4. **Use the tools** by referencing them with `#` in the chat input, e.g. `#hello` or `#add`.

5. **Verify** the server is running: Command Palette → `MCP: List Servers`.

### User-Level Configuration (All Workspaces)

To make the server available across all your VS Code workspaces, run:

```
MCP: Open User Configuration
```

from the Command Palette and add the same server block.

### Sharing with Your Team

Since `.vscode/mcp.json` is committed to the repo, anyone who clones it and has `uv` installed will automatically get the MCP server in VS Code — no extra setup needed.

---

## 2. Microsoft Copilot Studio (Remote — Multi-User)

To share the MCP server with non-developer users (e.g. via Microsoft Teams or Copilot Studio agents), you need to **deploy the server as a remote HTTP endpoint**.

### Step 2a: Convert to HTTP Transport

The current server uses `stdio` transport (local only). For remote access, switch to HTTP. Update `server.py`:

```python
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
```

> **Note:** Copilot Studio only supports **Streamable HTTP** transport. SSE transport is deprecated and no longer supported.

### Step 2b: Deploy to a Public Endpoint

Deploy the server so it's reachable over HTTPS. Options include:

| Platform           | Approach                                                        |
| ------------------ | --------------------------------------------------------------- |
| **Azure App Service** | Deploy as a Python web app. See [MS Learn guide](https://learn.microsoft.com/en-us/azure/app-service/tutorial-ai-model-context-protocol-server-dotnet). |
| **Azure Container Apps** | Containerize with Docker and deploy.                        |
| **Any cloud VM**   | Run behind a reverse proxy (nginx/caddy) with TLS.             |

Your deployed URL will look like: `https://mcp-hello-world.azurewebsites.net/mcp`

### Step 2c: Connect in Copilot Studio

1. Go to [Copilot Studio](https://copilotstudio.microsoft.com/).
2. Open or create an agent.
3. Navigate to **Tools → Add Tool → New Tool → MCP**.
4. Enter the URL of your deployed server (e.g. `https://mcp-hello-world.azurewebsites.net/mcp`).
5. If authentication is required, configure an API key or OAuth 2.0.
6. The tools (`hello`, `add`) will be automatically discovered and listed.

Users can now interact with these tools through the Copilot Studio agent in **Microsoft Teams**, **Copilot Chat**, or any channel the agent is published to.

For more details, see: [Connect your agent to an MCP server](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent)

---

## 3. Microsoft 365 Copilot (Declarative Agents)

Declarative agents let you extend Microsoft 365 Copilot with custom MCP-powered tools, surfacing them directly in the M365 Copilot experience.

### Prerequisites

- [VS Code](https://code.visualstudio.com/) with [Microsoft 365 Agents Toolkit](https://learn.microsoft.com/en-us/microsoft-365/developer/overview-m365-agents-toolkit) extension
- Microsoft 365 developer tenant with Copilot license
- The MCP server deployed as a remote HTTP endpoint (see Section 2 above)

### Steps

1. **Open VS Code** and select **Microsoft 365 Agents Toolkit → Create a New Declarative Agent**.

2. **Connect to MCP server:** The toolkit will prompt you for the MCP server URL. Enter your deployed endpoint.

3. **Select tools to import:** The toolkit reads the MCP schema and lets you pick which tools (`hello`, `add`) to expose.

4. **Configure authentication:** If your server requires auth, the toolkit walks you through adding OAuth 2.0 or static credentials.

5. **Auto-generated scaffolding:** The toolkit generates:
   - `manifest.json` — app manifest listing the plugin
   - `ai-plugin.json` — MCP action definitions
   - `declarativeAgent.json` — agent configuration

6. **Test locally:** Use the toolkit's **Provision and Start Debugging** feature to sideload the agent into your M365 Copilot app.

7. **Publish:** Once tested, publish the agent through the Microsoft 365 admin center to make it available to your organization.

For a full walkthrough, see:
- [Build declarative agents for M365 Copilot with MCP](https://devblogs.microsoft.com/microsoft365dev/build-declarative-agents-for-microsoft-365-copilot-with-mcp/)
- [Copilot Developer Camp — MCP Server Lab](https://microsoft.github.io/copilot-camp/pages/extend-m365-copilot/08-mcp-server/)

---

## Security Considerations

- **HTTPS in production:** Never expose MCP servers over plain HTTP outside of localhost.
- **Authentication:** Use API keys or OAuth 2.0 for remote deployments. Copilot Studio supports both.
- **Short-lived tokens:** If using OAuth, prefer short-lived access tokens.
- **Least-privilege scopes:** Split access per tool where possible.
- **Never log credentials:** Scrub tokens and API keys from logs.

---

## Quick Reference

| Platform              | Transport         | Scope           | Config Location                |
| --------------------- | ----------------- | --------------- | ------------------------------ |
| VS Code Copilot       | stdio             | Local developer | `.vscode/mcp.json`            |
| Copilot Studio        | Streamable HTTP   | Organization    | Copilot Studio UI             |
| M365 Copilot (Agents) | Streamable HTTP   | Organization    | M365 Agents Toolkit / Manifest |

---

## Sources

- [Add and manage MCP servers in VS Code](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
- [MCP configuration reference](https://code.visualstudio.com/docs/copilot/reference/mcp-configuration)
- [Connect your agent to an MCP server — Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent)
- [MCP is now GA in Copilot Studio](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/model-context-protocol-mcp-is-now-generally-available-in-microsoft-copilot-studio/)
- [Build declarative agents for M365 Copilot with MCP](https://devblogs.microsoft.com/microsoft365dev/build-declarative-agents-for-microsoft-365-copilot-with-mcp/)
- [Build plugins from an MCP server for M365 Copilot](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/build-mcp-plugins)
- [Copilot Developer Camp — MCP Server Lab](https://microsoft.github.io/copilot-camp/pages/extend-m365-copilot/08-mcp-server/)
- [Extending GitHub Copilot Chat with MCP servers](https://docs.github.com/copilot/customizing-copilot/using-model-context-protocol/extending-copilot-chat-with-mcp)
