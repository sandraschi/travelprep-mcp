# travelprep-mcp Core Capabilities

## Overview

travelprep-mcp is a trip preparation MCP server that provides accommodation search across Airbnb and Booking.com, free-source destination information, and Booking.com account access. It requires no paid API keys for any of its data sources. The server runs on FastMCP 3.4+ with dual transport support: stdio mode (default for Claude Desktop integration) and streamable HTTP mode on port 11099 at the /mcp path when MCP_TRANSPORT=http is set.

The server exposes four portmanteau tools: stays, hotel_extras, destination, and account. Each tool accepts an operation parameter that dispatches to the appropriate backend logic. This design keeps the tool surface compact while providing rich sub-operation discovery through the operation enum schema.

All accommodation data comes from subprocess-wrapped open-source npm packages running over npx. The Airbnb provider uses openbnb-org/mcp-server-airbnb (MIT license) and the Booking.com provider uses insprd/hotelzero (MIT license). Both are launched as child processes communicating over MCP stdio. This avoids any dependency on paid RapidAPI keys or Booking.com affiliate partnerships.

Booking.com account access uses an isolated Playwright profile stored under ~/.travelprep-mcp/booking-profile/. This profile is deliberately kept separate from your default browser session -- no cookie decryption or Chrome profile scraping is involved. You log in once interactively through a headed Playwright window, and the session persists locally.

No booking-execution capability exists anywhere in this server. You can search, inspect, compare, check availability, read reviews, and view price calendars, but you cannot complete a purchase. This is a deliberate design choice documented in the budget module. The server ships with hardcoded spend caps of 300 EUR per night and 1500 EUR per total trip, which are echoed in every hotel_extras result for reference.

All destination data sources are free and require no API key: Wikipedia REST API for place overviews, Wikivoyage REST API for practical travel information, Open-Meteo for geocoding and weather forecasts, and REST Countries for currency, language, and timezone data. When a source returns no data for a given place name, the tool returns available: false with a reason string rather than fabricating or guessing data.

## Tool: stays

The stays portmanteau searches for and retrieves details about accommodation listings on Airbnb and Booking.com.

### Operation: search

Performs a location-based search across the specified provider. Requires the location parameter. For Booking.com searches, checkin and checkout are also required. For Airbnb searches, checkin and checkout are optional but recommended for accurate pricing.

Parameters:
- operation (str, required): Must be "search".
- provider (str, required): Must be "airbnb" or "booking".
- location (str, required): The destination name or address. Airbnb uses Photon geocoding with Nominatim fallback and 25% bounding box padding, so location filtering is approximate. Booking.com delegates to hotelzero's Playwright-based search.
- listing_id (str, optional): Not used for search operations.
- checkin (str, optional): Check-in date in YYYY-MM-DD format. Required for provider="booking".
- checkout (str, optional): Check-out date in YYYY-MM-DD format. Required for provider="booking".
- adults (int, default 1): Number of adult guests.
- children (int, default 0): Number of child guests. Airbnb only.
- min_price (int, optional): Minimum nightly price filter. Airbnb only.
- max_price (int, optional): Maximum nightly price filter. Airbnb only.

Return format:
{"provider": str, "operation": "search", "result": dict}

The result structure varies by provider. Airbnb returns listings with id, title, price, location, and amenities. Booking.com returns hotel data from the hotelzero Playwright scraper. Both providers may include coordinates for geographic sanity-checking.

Known issue: Airbnb location matching is loose due to Photon/Nominatim geocoding behavior. A search for "Paris" may return results from the broader Paris metropolitan area. Always check returned coordinates for precise geography.

Known issue: Booking.com actively fingerprints and blocks the Playwright browser behind hotelzero. The first two search attempts may fail with "Request blocked by Booking.com. Please wait a few minutes before retrying" before a third attempt succeeds. hotelzero has built-in retry/backoff and user-agent rotation for this. Do not hammer it in a loop.

### Operation: details

Retrieves detailed information about a specific listing. Requires the listing_id parameter. For Airbnb, listing_id is the numeric property ID. For Booking.com, listing_id is the full hotel URL from booking.com.

Parameters:
- operation (str, required): Must be "details".
- provider (str, required): Must be "airbnb" or "booking".
- listing_id (str, required): Airbnb numeric property ID or Booking.com full hotel URL.
- location (str, optional): Not used for details operations.
- checkin (str, optional): Check-in date for availability checking.
- checkout (str, optional): Check-out date for availability checking.
- adults (int, default 1): Number of adult guests.
- children (int, default 0): Number of child guests. Airbnb only.

Return format:
{"provider": str, "operation": "details", "result": dict}

## Tool: hotel_extras

The hotel_extras portmanteau provides Booking.com-specific operations beyond basic search and details. All operations delegate to the same hotelzero subprocess used by stays(provider="booking"). These operations were wired from a confirmed list_tools() schema and may not all have been individually exercised with live calls.

Every hotel_extras result includes a budget_caps object with max_nightly_rate_eur (300.0), max_total_trip_eur (1500.0), and a note explaining that per-result auto-flagging against these caps is not yet wired in because the upstream result shape is not confirmed live.

### Operation: find_hotels

Filtered search using Booking.com's 80+ filter code system. Requires location, checkin, and checkout. Accepts an optional filters dict that is passed through as-is to the hotelzero tool -- see hotelzero's README for the filter key catalog.

Parameters:
- location (str, required): Destination name.
- checkin (str, required): Check-in date in YYYY-MM-DD format.
- checkout (str, required): Check-out date in YYYY-MM-DD format.
- adults (int, default 2): Number of adult guests.
- rooms (int, default 1): Number of rooms.
- filters (dict, optional): Passed through to hotelzero's find_hotels tool.

### Operation: compare

Compares 2-3 Booking.com hotel URLs side by side. Requires hotel_urls as a list of 2-3 Booking.com hotel page URLs.

Parameters:
- hotel_urls (list[str], required): 2-3 full Booking.com hotel URLs.

### Operation: check_availability

Checks whether a specific hotel has rooms available for given dates. Requires hotel_url, checkin, and checkout.

Parameters:
- hotel_url (str, required): Full Booking.com hotel URL.
- checkin (str, required): Check-in date in YYYY-MM-DD format.
- checkout (str, required): Check-out date in YYYY-MM-DD format.
- adults (int, default 2): Number of adult guests.
- rooms (int, default 1): Number of rooms.

### Operation: reviews

Retrieves guest reviews for a specific hotel. Requires hotel_url. Optional sort_by (default "recent") and filter_by parameters control review ordering and filtering.

Parameters:
- hotel_url (str, required): Full Booking.com hotel URL.
- sort_by (str, default "recent"): Review sort order.
- filter_by (str, optional): Review filter criterion.

### Operation: price_calendar

Finds the cheapest dates for a given hotel over a configurable window. Requires hotel_url and price_calendar_start (YYYY-MM-DD). Optional price_calendar_nights (default 14) controls how many nights of pricing to return.

Parameters:
- hotel_url (str, required): Full Booking.com hotel URL.
- price_calendar_start (str, required): Start date in YYYY-MM-DD format for the calendar window.
- price_calendar_nights (int, default 14): Number of nights to show pricing for.
- adults (int, default 2): Number of adult guests.
- rooms (int, default 1): Number of rooms.

## Tool: destination

The destination portmanteau retrieves free-source travel information for any place name. All sources are free and require no API key. Returns available: false with a reason string per section when a source has no data, rather than fabricating results.

### Operation: overview

Fetches a Wikipedia summary for the given place. Returns the page title, extract text, desktop Wikipedia URL, and thumbnail image URL when available.

Parameters:
- place (str, required): The place name to look up. Spaces are converted to underscores for the Wikipedia API.

### Operation: weather

Fetches a multi-day weather forecast from Open-Meteo for the given place. The place is geocoded via Open-Meteo's geocoding API, then a forecast is retrieved for the specified number of days. Returns daily temperature highs and lows in Celsius, precipitation probability as a percentage, and a weather code.

Parameters:
- place (str, required): The place name to geocode and forecast.
- forecast_days (int, default 7): Number of forecast days (1-16).

### Operation: practical

Retrieves practical travel information from Wikivoyage and REST Countries. Returns a Wikivoyage extract and URL when available, plus country-level data including currency codes, spoken languages, calling code, capital city, region, and timezones.

Parameters:
- place (str, required): The place name to look up.

### Operation: full

Combines overview, weather, and practical into a single response. Runs all three fetches in parallel within a single httpx client session for efficiency.

Parameters:
- place (str, required): The place name.
- forecast_days (int, default 7): Number of forecast days for the weather section.

## Tool: account

The account portmanteau provides access to Booking.com account data via an isolated, locally-persisted Playwright login session. The session profile is stored under ~/.travelprep-mcp/booking-profile/ and is created by running the login operation once in a headed browser window.

### Operation: login

Opens a headed Playwright browser window at Booking.com's sign-in page. You log in manually through the browser window. The session is persisted to the local profile directory so subsequent operations can use it in headless mode. The operation waits up to 300 seconds for the logged-in state to be detected.

### Operation: status

Checks whether a local session profile exists on disk. Returns True if the profile directory exists and is non-empty. Does not confirm that the session is still valid -- Booking.com may have expired it. A real account fetch (trips, wishlist, or rewards) will surface an expired session through a redirect to the sign-in page.

### Operation: trips

Retrieves past and upcoming bookings from the Booking.com account. This operation calls booking_account.trips() which navigates to the Booking.com mytrips.html page within the persisted Playwright session. The parsing logic is an unverified first pass -- CSS selectors and JSON-shape guesses have not been confirmed against real markup.

### Operation: wishlist

Retrieves saved/wishlisted properties from the Booking.com account. Navigates to mywishlist.html within the Playwright session. Like trips, the parsing is an unverified first pass.

### Operation: rewards

Retrieves Genius level, wallet balance, and rewards information from the Booking.com account. Navigates to rewards_and_wallet.html. Parsing is an unverified first pass pending live testing against a real account.

## Budget System

The budget module provides hardcoded sanity caps for accommodation pricing. These are not booking gates -- no booking-execution tool exists. Instead they serve as a reference ceiling that search results can be checked against.

Constants:
- MAX_NIGHTLY_RATE_EUR: 300.0 -- maximum acceptable nightly rate.
- MAX_TOTAL_TRIP_EUR: 1500.0 -- maximum acceptable total trip cost.

The within_budget function accepts optional nightly_rate, total, and nights parameters. If total is omitted but nightly_rate and nights are provided, total is derived as nightly_rate * nights. Returns a dict with within_budget (bool), both cap values, and a reason string when over budget.

## Transport Modes

stdio mode (default): The server speaks MCP over stdin/stdout. Use this for Claude Desktop integration and other MCP hosts that connect via stdio.

HTTP mode: Set MCP_TRANSPORT=http. The server listens on 127.0.0.1:11099 with the MCP endpoint at /mcp. In HTTP mode, three REST health/introspection endpoints are also available: GET /api/capabilities (tool surface introspection per fleet standards), GET /api/health (liveness check returning status and version), and GET /api/tools (dynamic tool list with names, descriptions, and input schemas).

## Provider Notes

The Airbnb provider (openbnb-org/mcp-server-airbnb) runs as an npx subprocess. It scrapes Airbnb's server-rendered HTML pages. In testing, Airbnb showed no bot-detection friction -- the provider appears to be treated as a regular browser session. Location filtering uses Photon geocoding with Nominatim fallback, which produces approximate bounding boxes. Results should be sanity-checked against returned coordinates.

The Booking.com provider (insprd/hotelzero) runs as an npx subprocess using Playwright. Unlike Airbnb, Booking.com actively fingerprints and blocks automated browsers. In live testing, the first two search attempts were blocked before a third succeeded. hotelzero has built-in retry/backoff and user-agent rotation. This provider is meaningfully more fragile than the Airbnb one.

The account system uses an isolated Chromium profile (Playwright persistent context) at ~/.travelprep-mcp/booking-profile/. This approach deliberately avoids decrypting cookies from your default Chrome profile. You log in once through a headed window; the profile persists the session across restarts like any normal browser profile. To revoke access, delete the profile directory.

## Truth and Transparency

All destination tools return available: false with a human-readable reason string when their upstream data source has no information for the requested place. No data is ever fabricated or guessed. If Wikivoyage has no page for a small village, the practical section returns available: false rather than synthesizing travel tips. If Open-Meteo cannot geocode an obscure location name, the weather section returns available: false rather than returning a forecast for the wrong coordinates.

Accommodation search results reflect what the underlying scrapers return. Airbnb location matching is loose and results should be checked against returned coordinates. Booking.com search may fail transiently due to bot detection -- retry after a brief pause. All provider parsing status is documented in per-module docstrings.

The server has no booking-execution capability. It searches, inspects, compares, checks availability, reads reviews, and views price calendars, but never purchases anything. The budget caps are informative reference values, not automated enforcement gates -- they are echoed in results so you can use them as decision input, but no tool enforces them transactionally.
