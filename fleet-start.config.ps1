# Per-repo fleet start config for travelprep-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'travelprep-mcp'
    BackendPort  = 11099
    FrontendPort = 11100
    HealthPath   = '/api/health'
    WebRoot      = 'webapp'
    Backend = @{
        Kind    = 'custom'
        Command = "`$env:MCP_TRANSPORT='http'; uv run --no-sync --project '$PSScriptRoot' travelprep-mcp"
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
    }
}
