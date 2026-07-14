# travelprep-mcp -- Claude Code instructions

## Entry Points
- `just run` — stdio mode
- `MCP_TRANSPORT=http just run-http` — HTTP mode on port 11099
- `just lint` — ruff check
- `just test-live` — live tests (hit real APIs)

## Key Files
- `src/travelprep_mcp/server.py` — FastMCP server + admin tools
- `src/travelprep_mcp/tools/` — MCP tool implementations
- `src/travelprep_mcp/providers/` — Provider-specific wrappers
- `src/travelprep_mcp/auth/booking_session.py` — Playwright-based login session
- `src/travelprep_mcp/budget.py` — Spend caps

## Standards
- Follow TOOL_DESIGN_STANDARDS.md: Annotated+Field over Args docstrings
- Follow DOCSTRINGS_SOTA.md: ## Return Format and ## Examples in all tool docstrings
- All tools are portmanteau (operation enum param)
- No booking-execution tool — see budget.py for why
