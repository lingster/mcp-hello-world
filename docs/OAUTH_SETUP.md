# AladdinSDK OAuth Setup Guide

This guide walks through setting up OAuth authentication for the AladdinSDK.

---

## Step 1: Create an OAuth Application in Aladdin Studio

1. Go to the **Aladdin Studio UI**.
2. Create or open a **Project**.
3. Under the project, create an **OAuth Application**.
4. Note your **Client ID** and **Client Secret**.
5. Add a localhost callback URI: `http://localhost:<PORT>` (e.g., `http://localhost:8080`).
6. Select the required **API scopes**.

---

## Step 2: Generate a Refresh Token

Use the SDK CLI:

```bash
aladdinsdk-cli
```

1. Select **OAuth** authentication type.
2. Choose **"Refresh Token Flow - Generate Refresh token given Client ID, Secret"**.
3. Enter your localhost callback port (must match the one registered in Studio).
4. Select your API scopes.
5. A browser window opens for authentication — log in with your credentials.
6. The refresh token is displayed upon success.

---

## Step 3: Configure the SDK

You have three options for providing OAuth credentials to the SDK.

### Option A: YAML Config File

Create a config file and point to it with the `ASDK_USER_CONFIG_FILE` environment variable:

```yaml
RUN_MODE: local
USER_CREDENTIALS:
  USERNAME: your_username
API:
  AUTH_TYPE: "OAuth"
  AUTH_FLOW_TYPE: "refresh_token"   # or "client_credentials"
  OAUTH:
    CLIENT_ID: "your-client-id"
    CLIENT_SECRET: "your-client-secret"
    REFRESH_TOKEN: "your-refresh-token"
    AUTH_SERVER_URL: "https://your-auth-server/oauth2/token"
```

```bash
export ASDK_USER_CONFIG_FILE=/path/to/config.yaml
```

### Option B: Environment Variables

```bash
export ASDK_API__AUTH_TYPE=OAuth
export ASDK_API__AUTH_FLOW_TYPE=refresh_token
export ASDK_API__OAUTH__CLIENT_ID=your-client-id
export ASDK_API__OAUTH__CLIENT_SECRET=your-client-secret
export ASDK_API__OAUTH__REFRESH_TOKEN=your-refresh-token
export ASDK_API__OAUTH__AUTH_SERVER_URL=https://your-auth-server/oauth2/token
```

### Option C: File References (Recommended for Production)

Store secrets in separate files and reference their paths:

```yaml
API:
  AUTH_TYPE: "OAuth"
  OAUTH:
    CLIENT_DETAILS_FILEPATH: /path/to/client_details.json
    REFRESH_TOKEN_FILEPATH: /path/to/refresh_token.txt
```

---

## OAuth Flow Types

| Flow | Use Case | Required Fields |
|------|----------|-----------------|
| **Refresh Token** | Interactive / local development | `CLIENT_ID`, `CLIENT_SECRET`, `REFRESH_TOKEN` |
| **Client Credentials** | App-to-app / service accounts | `CLIENT_ID`, `CLIENT_SECRET` |

---

## ADC (Snowflake) OAuth

If you also need OAuth for Snowflake/ADC queries:

```yaml
ADC:
  CONN:
    AUTHENTICATOR: "oauth"
  OAUTH:
    ACCESS_TOKEN: "your-adc-token"
```

The SDK can reuse the API OAuth token for ADC if no separate ADC token is provided.

---

## Security Best Practices

- **Never commit secrets** — keep `CLIENT_SECRET`, `REFRESH_TOKEN`, and `ACCESS_TOKEN` out of version control.
- **Use file references** (Option C) in production to avoid secrets in environment variables or config files.
- **Prefer short-lived tokens** — use refresh token flow so access tokens rotate automatically.
- **Least-privilege scopes** — only request the API scopes you need.

---

## Sources

- [AladdinSDK README — GitHub](https://github.com/blackrock/aladdinsdk)
- [AladdinSDK Installation and Setup — DeepWiki](https://deepwiki.com/blackrock/aladdinsdk/1.1-installation-and-setup)
