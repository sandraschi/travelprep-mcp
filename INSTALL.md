# INSTALL

## Prerequisites

- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- Node.js + npx on PATH (used to launch the Airbnb and Booking.com
  providers as subprocesses -- no separate npm install needed, `npx -y`
  fetches them on first run)

## Setup

```powershell
cd D:\Dev\repos\travelprep-mcp
uv sync --extra dev
```

## Claude Desktop config

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "travelprep": {
      "command": "uv",
      "args": ["run", "--directory", "D:\\Dev\\repos\\travelprep-mcp", "travelprep-mcp"]
    }
  }
}
```

Restart Claude Desktop. First call to a `stays` tool will trigger an
`npx` download of whichever provider package isn't cached yet (~10-20s
one-time cost).

## HTTP transport (for the eventual webapp)

```powershell
$env:MCP_TRANSPORT = "http"
uv run travelprep-mcp
```

Serves streamable HTTP MCP on `http://127.0.0.1:11099/mcp`.

## Verify it's working

```powershell
uv run pytest tests/test_destination.py -v
```

Should show 4 passed in a few seconds, hitting real Wikipedia/Open-Meteo/
REST Countries endpoints. If that fails, check your network connection
before anything else -- there's no local fallback by design.
