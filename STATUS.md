# travelprep-mcp -- Status

| Piece | Status |
|---|---|
| `destination` tool (free-source: Wikipedia, Wikivoyage, Open-Meteo, REST Countries) | **Working.** 4/4 live tests pass against real APIs. |
| `stays` tool, Airbnb provider | **Working.** Live-tested end-to-end (`airbnb_search`, 18 real results). |
| `stays` tool, Booking.com provider | **Working but fragile.** Live-tested end-to-end, but Booking.com bot-detects the Playwright scraper. |
| `hotel_extras` tool (Booking.com-only: find_hotels, compare, reviews, price_calendar) | **Wired, not live-verified.** `find_hotels` hit bot-detection; other operations not exercised. |
| `account` tool (Booking.com login/trips/wishlist/rewards) | **Not live-tested.** Requires a logged-in session; all selectors unverified. |
| Budget guardrails (€300/night, €1500/trip) | **Implemented.** No booking-execution capability exists by design. |
| REST layer (FastAPI, mounted MCP at /mcp) | **Working, migrated to FastAPI 2026-07-14.** Was bare Starlette (`mcp.custom_route`); now mirrors the `arxiv-mcp` reference pattern -- `mcp.http_app(path="/")` mounted under a FastAPI app via `build_app()`, CORS middleware, direct `uvicorn.run()` (not `run_http_async()`, which drops custom middleware/routes per CORS_STANDARD.md). All 6 REST routes + the mounted MCP JSON-RPC transport live-verified (real `initialize` handshake succeeded through the mount). |
| Skills (travelprep-expert) | **Working.** MCP resource + REST both confirmed live. |
| Webapp (Vite + React + Tailwind) | **Builds clean, 1544 modules.** Dashboard + ToolsHub fully wired to real endpoints. Chat rewired 2026-07-14 to match the real fleet pattern (direct-to-Ollama, not a backend proxy) -- builds and live-tested end-to-end. **ApiDocsPage fixed 2026-07-14**: now gets real, auto-generated Swagger UI + ReDoc from FastAPI (`/docs`, `/redoc`, `/openapi.json` all confirmed live, 200s, 6 paths). Vite dev-proxy extended so the iframe stays same-origin (needed for the dark-theme CSS injection to actually reach `contentDocument`). |
| Tauri/NSIS desktop wrapper | **Built.** `native/` with backend.rs, build.ps1, spec file, run_server.py. |
| MCPB packaging | **Built.** Available via `mcpb pack`. |
| Unit tests | **Coverage for `destination` (4 live tests).** Airbnb and Booking client tests exist but are live-only (`-s` flag). |
