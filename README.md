# travelprep-mcp

**Trip preparation MCP server (v0.1.0)** -- FastMCP 3.4+ tools mounted
under FastAPI (dual transport: stdio + MCP streamable-HTTP at `/mcp` on
port **11099**, plus a real FastAPI REST layer with auto-generated
`/docs`/`/redoc`). Four tools: `stays` (Airbnb +
Booking.com, subprocess-wrapped open-source scrapers, no paid API keys),
`hotel_extras` (Booking.com-only: filtered search, compare, availability,
reviews, price calendar), `destination` (free-source
overview/weather/practical info -- no API keys at all), and `account`
(Booking.com login/trips/wishlist/rewards via isolated Playwright session).

## Status -- read this before trusting anything

This is a genuine v0.1, not a polished fleet-SOTA server. Here's exactly
what's real and what isn't, as of 2026-07-14:

| Piece | Status |
|---|---|
| `destination` tool (Wikipedia, Wikivoyage, Open-Meteo, REST Countries) | **Working.** 4/4 live tests pass against real APIs, no mocks. |
| `stays` tool, Airbnb branch | **Working.** Live-tested end-to-end (`airbnb_search`, 18 real results). |
| `stays` tool, Booking.com branch | **Working but fragile.** Live-tested end-to-end, but Booking.com actively bot-detects the Playwright browser -- first 2/3 attempts in testing were blocked before a retry succeeded. Don't hammer it. |
| `hotel_extras` tool | **Wired, not live-verified.** `find_hotels` was attempted live and hit the same bot-detection block; `compare`/`check_availability`/`reviews`/`price_calendar` haven't been exercised at all. |
| `account` tool (Booking.com trips/wishlist/rewards) | **Not live-tested at all.** Written 2026-07-14 with no logged-in session to test against -- every CSS selector and JSON-shape guess in `providers/booking_account.py` is unverified. Requires running `account(operation="login")` once (opens a headed browser) before anything else works. |
| Webapp (React/Vite dashboard, Prefab cards) | **Not built yet.** Server is stdio/HTTP-only for v0.1. Ports 11099 (backend) / 11100 (frontend) are reserved in `WEBAPP_PORTS.md`. |
| MCPB packaging, Tauri desktop wrapper | **Not built yet.** |
| Playwright e2e (mandatory for webapp per fleet standard) | **N/A until webapp exists.** |
| `destination_info` bulk/list Prefab card | **Not built yet** -- fleet mandate is list/status/stats tools get Prefab cards; neither current tool is quite that shape, revisit once webapp lands. |

## Why two accommodation providers are subprocess-wrapped, not native Python

Both `openbnb-org/mcp-server-airbnb` and `insprd/hotelzero` are
actively-maintained, MIT-licensed, no-API-key Node/TS MCP servers that
already do the hard part (scraping + parsing two sites that actively
resist it). Reimplementing that in Python buys nothing but maintenance
burden. Instead, `travelprep_mcp.providers.base.StdioProvider` launches
each one via `npx` and speaks MCP to it over stdio -- same pattern as
`opencode-cli-mcp` / `goose-mcp` wrapping external CLI agents. Requires
Node.js + npx on PATH (already present on Goliath).

## Known limitations (found by actually running this, not guessed)

- **Airbnb location matching is loose.** The upstream server geocodes
  via Photon, falls back to Nominatim when Photon has no extent for a
  place, and pads the resulting bounding box by 25%. A search for "Kew"
  can legitimately return listings in Wembley or Hampstead. Filter
  results by returned `lat`/`lng` against a known reference point --
  don't trust the search radius. (This is the exact bug that made the
  original Kew Gardens search in chat return half of London.)
- **Booking.com bot-detects the scraper.** `hotelzero` uses Playwright
  with retry/backoff and UA rotation, but expect occasional "Request
  blocked by Booking.com" failures that resolve on retry, not always.
- **`find_hotels`, `compare_hotels`, `check_availability`, `get_reviews`,
  `get_price_calendar`** are now wired via the `hotel_extras` tool. Only
  `search_hotels` and `get_hotel_details` (on `stays`) have been
  individually live-invoked; the `hotel_extras` operations were wired
  from the confirmed `list_tools()` schema but not each exercised with
  a live call -- `find_hotels` was attempted live on 2026-07-14 and hit
  Booking.com's bot-detection block, so treat response shapes as
  unverified until confirmed.

## Tools

### `stays(operation, provider, ...)`

- `operation`: `"search"` | `"details"`
- `provider`: `"airbnb"` | `"booking"`
- `search` needs `location`; `booking` search additionally requires
  `checkin` + `checkout` (upstream-mandatory, Airbnb's are optional)
- `details` needs `listing_id` (Airbnb: the numeric ID; Booking.com:
  the full hotel URL)

### `hotel_extras(operation, ...)`

Booking.com-only, beyond basic `stays` search/details.

- `operation`: `"find_hotels"` | `"compare"` | `"check_availability"` | `"reviews"` | `"price_calendar"`
- `find_hotels` needs `location`, `checkin`, `checkout`; optional `filters` dict (80+ upstream filter codes, passed through as-is)
- `compare` needs `hotel_urls` (2-3 Booking.com URLs)
- `check_availability` needs `hotel_url`, `checkin`, `checkout`
- `reviews` needs `hotel_url`; optional `sort_by`/`filter_by`
- `price_calendar` needs `hotel_url`, `price_calendar_start` (YYYY-MM-DD)

Not yet individually live-verified beyond `find_hotels` (which hit a bot-detection block on the one live attempt so far) -- see Known limitations.

### `destination(operation, place, forecast_days=7)`

- `operation`: `"overview"` | `"weather"` | `"practical"` | `"full"`
- All free, keyless: Wikipedia + Wikivoyage REST summary APIs,
  Open-Meteo geocoding + forecast, REST Countries

### `account(operation)`

Booking.com account access: trips, wishlist, rewards.

- `operation`: `"login"` | `"status"` | `"trips"` | `"wishlist"` | `"rewards"`
- Run `login` once first -- opens a headed browser for an interactive
  sign-in, session then persists in an isolated Chromium profile at
  `~/.travelprep-mcp/booking-profile`, deliberately separate from
  Sandra's daily Chrome profile (see `auth/booking_session.py`
  docstring for why, vs. how third-party tools like
  `booking-com-pp-cli` do live-Chrome cookie import instead)
- `trips`/`wishlist`/`rewards` are UNVERIFIED -- written without a live
  logged-in session to test selectors against; see
  `providers/booking_account.py` docstring
- No booking-execution tool exists anywhere in this server -- see
  `budget.py` for why that's deliberate, not an oversight

## Budget guardrail

`budget.py` hardcodes `MAX_NIGHTLY_RATE_EUR = 300` and
`MAX_TOTAL_TRIP_EUR = 1500`. Not a booking gate (no booking tool
exists) -- a sanity pre-check any future price data can be run
through, plus caps echoed into every `hotel_extras` response today.
Per-result auto-flagging isn't wired in yet since the upstream price
field shape isn't confirmed live.

## Run it

```powershell
uv sync --extra dev
uv run travelprep-mcp                      # stdio, for Claude Desktop
$env:MCP_TRANSPORT = "http"
uv run travelprep-mcp                      # HTTP on :11099/mcp
```

See `INSTALL.md` for Claude Desktop config.

## Test it

```powershell
uv run pytest tests/test_destination.py -v          # fast, no browser
uv run pytest tests/test_airbnb_client.py -v -s      # npx cold start, real search
uv run pytest tests/test_booking_client.py -v -s     # Playwright, slower, may retry
```

## License

MIT.
