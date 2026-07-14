function Require-Command {
    param([string]$Name, [string]$WingetId)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Host "$Name not found. Installing via winget ($WingetId)..."
        winget install --id $WingetId --accept-source-agreements --accept-package-agreements -e
    }
}

Require-Command -Name "uv" -WingetId "astral-sh.uv"
Require-Command -Name "node" -WingetId "OpenJS.NodeJS.LTS"

Set-Location $PSScriptRoot

Write-Host "Syncing dependencies..."
uv sync --extra dev
if ($LASTEXITCODE -ne 0) {
    Write-Host "uv sync failed (exit $LASTEXITCODE). See output above."
    exit 1
}

Write-Host "Import smoke test..."
uv run python -c "import travelprep_mcp; print('travelprep_mcp OK:', travelprep_mcp.__version__)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Import smoke test failed. Check the uv sync output above for missing dependencies."
    exit 1
}

Write-Host "No webapp yet for this repo (v0.1) -- starting stdio MCP server directly."
Write-Host "For Claude Desktop, point mcpServers.travelprep at:"
Write-Host "  command: uv"
Write-Host "  args: [run, --directory, $PSScriptRoot, travelprep-mcp]"
Write-Host ""
Write-Host "Starting stdio server now (Ctrl+C to stop)..."
uv run travelprep-mcp
