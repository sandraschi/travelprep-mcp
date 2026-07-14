# travelprep-mcp -- Status

| Piece | Status |
|---|---|
| `destination` tool (free-source: Wikipedia, Wikivoyage, Open-Meteo, REST Countries) | **Working.** 4/4 live tests pass against real APIs. |
| `stays` tool, Airbnb provider | **Working.** Live-tested end-to-end (`airbnb_search`, 18 real results). |
| `stays` tool, Booking.com provider | **Working but fragile.** Live-tested end-to-end, but Booking.com bot-detects the Playwright scraper. |
| `hotel_extras` tool (Booking.com-only: find_hotels, compare, reviews, price_calendar) | **Wired, not live-verified.** `find_hotels` hit bot-detection; other operations not exercised. |
| `account` tool (Booking.com login/trips/wishlist/rewards) | **Not live-tested.** Requires a logged-in session; all selectors unverified. |
| Budget guardrails (€300/night, €1500/trip) | **Implemented.** No booking-execution capability exists by design. |
| REST layer (/api/capabilities, /api/health, /api/tools, /api/skills, /skill/{name}, /api/llm/discover) | **Working, live-verified 2026-07-14** against real Ollama (qwen3.6:27b) end-to-end. |
| Skills (travelprep-expert) | **Working.** MCP resource + REST both confirmed live. |
| Webapp (Vite + React + Tailwind) | **Builds clean, 1544 modules.** Dashboard + ToolsHub fully wired to real endpoints. Chat rewired 2026-07-14 to match the real fleet pattern (direct-to-Ollama, not a backend proxy) -- builds and live-tested end-to-end. **ApiDocsPage still calls /docs and /redoc, which don't exist and per WEBAPP_SOTA_STANDARDS.md §IX shouldn't -- this server is FastMCP/Starlette, not FastAPI, and fleet policy says "do not manually wire Swagger into a Starlette app." Unresolved -- needs a decision, not yet fixed.** |
| Tauri/NSIS desktop wrapper | **Built.** `native/` with backend.rs, build.ps1, spec file, run_server.py. |
| MCPB packaging | **Built.** Available via `mcpb pack`. |
| Unit tests | **Coverage for `destination` (4 live tests).** Airbnb and Booking client tests exist but are live-only (`-s` flag). |
