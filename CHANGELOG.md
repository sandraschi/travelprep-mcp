# Changelog

## Unreleased

- `travelprep-expert` skill — MCP resource (`skill://travelprep-expert/SKILL.md`) + REST (`/api/skills`, `/skill/{name}`), live-verified
- `/api/llm/discover` — Ollama/LM Studio auto-detection (WEBAPP_SOTA_STANDARDS.md §VI "Glom On" pattern), live-tested against real Ollama (qwen3.6:27b)
- Webapp: Dashboard + ToolsHub pages confirmed working against real backend endpoints; ChatPage rewired to the actual fleet reference pattern (chats directly with Ollama, loads skill as base system prompt) instead of a nonexistent backend proxy -- full round trip live-tested
- Known gap: ApiDocsPage still targets `/docs`/`/redoc`, which don't exist and per WEBAPP_SOTA_STANDARDS.md §IX shouldn't for a Starlette (non-FastAPI) server -- unresolved, needs a decision

## 0.1.0 (2026-07-14)

- `destination` tool — free-source overview/weather/practical for any place (live-tested)
- `stays` tool — Airbnb + Booking.com search/details (live-tested with known fragility on Booking bot detection)
- `hotel_extras` tool — Booking.com-only: find_hotels, compare, check_availability, reviews, price_calendar
- `account` tool — Booking.com login/trips/wishlist/rewards via isolated Playwright session
- Budget guardrails — hardcoded caps (€300/night, €1500/trip), no booking-execution capability
- REST layer — `/api/capabilities`, `/api/health`, `/api/tools`
- Webapp scaffold — Vite + React + Tailwind config, zero pages yet
- Dual transport — stdio (default) + streamable HTTP on 127.0.0.1:11099/mcp
