# Per-repo fleet start config for travelprep-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'travelprep-mcp'
    BackendPort  = 11099
    FrontendPort = 11100
    HealthPath   = '/health'
    WebRoot      = 'webapp'
    Backend = @{
        Kind = 'none'
    }
    Frontend = @{
        Kind = 'none'
    }
}
