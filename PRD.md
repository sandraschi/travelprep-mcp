# travelprep-mcp -- Product Requirements Document

## Problem

Users need a unified trip preparation MCP server that provides accommodation
search across multiple providers (Airbnb, Booking.com) alongside free-source
destination information (overview, weather, practical/currency/language facts)
-- all without requiring paid API keys.

## Features

### Core Tools (Portmanteau pattern)

| Tool | Operations | Data sources | Status |
|---|---|---|---|
| `destination` | overview, weather, practical, full | Wikipedia, Wikivoyage, Open-Meteo, REST Countries | Working |
| `stays` | search, details (airbnb or booking provider) | openbnb-org/mcp-server-airbnb (subprocess stdio), insprd/hotelzero (subprocess stdio) | Working (Airbnb: stable; Booking: fragile) |
| `hotel_extras` | find_hotels, compare, check_availability, reviews, price_calendar | insprd/hotelzero (Booking.com only) | Wired, not live-verified |
| `account` | login, status, trips, wishlist, rewards | Isolated Playwright session (Booking.com) | Not live-tested |

### Non-Goals

- **No booking execution.** The server can search, inspect, and compare
  accommodations but never purchase. See `budget.py` for rationale.
- **No paid API keys.** All sources are free (Wikipedia, Open-Meteo, etc.)
  or MIT-licensed subprocess tools.
- **No user authentication system.** Booking.com account access uses a local
  Playwright session, not OAuth or web auth.

## Architecture

- **FastMCP 3.4+** with dual transport (stdio for Claude Desktop, HTTP `/mcp`
  for webapp). Backend port: **11099**. Frontend (future): **11100**.
- **StdioProvider** pattern (src/travelprep_mcp/providers/base.py): wraps
  external Node/TS MCP servers as subprocesses over stdio, avoiding
  reimplementation of scraping logic in Python.
- **Playwright** for Booking.com account auth (isolated profile, not default
  browser session). Used indirectly by hotelzero for Booking.com scraping.
- **Budget guardrails** (src/travelprep_mcp/budget.py): hardcoded spend caps
  of €300/night and €1500/trip. No tool can override these.

## Future

- Webapp dashboard (React/Vite/Tailwind) with dynamic tool discovery,
  local LLM glom-on, Prefab in-chat cards for list/status results.
- Prefab UI cards for destination_info, search results, and hotel comparisons.
- Tauri/NSIS desktop wrapper for single-installer distribution.
- MCPB packaging for Claude Desktop single-click install.
