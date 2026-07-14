"""Booking.com provider -- wraps insprd/hotelzero (MIT, Playwright-based) over stdio.

Chosen over the RapidAPI-backed alternatives (esakrissa/hotels_mcp_server,
EmilyThaHuman/booking-mcp-server) because it needs no paid API key --
consistent with the Airbnb provider's scrape-and-parse approach and the
fleet's budget-aware / local-first doctrine. An official Booking.com
remote MCP also exists (https://demandapi-mcp.booking.com/v1/mcp/...)
but requires OAuth via a Booking.com partner account; unverified whether
that's open to an individual/non-affiliate account, so not used here
for v0.1.

Status: LIVE-TESTED 2026-07-14, including a real end-to-end
`search_hotels` call (tests/test_booking_client.py), not just schema
discovery. All seven upstream tools now have Python wrappers below:
`search_hotels` / `find_hotels` / `get_hotel_details` / `compare_hotels`
/ `check_availability` / `get_reviews` / `get_price_calendar`. Only
`search` and `hotel_details` have been individually live-invoked;
the other five were wired from the confirmed `list_tools()` schema
but not yet each exercised with a live call -- check before relying
on their exact response shape.

IMPORTANT operational risk, confirmed live: unlike the Airbnb provider
(server-rendered HTML, no bot-detection friction observed),
Booking.com actively fingerprints and blocks the Playwright browser --
the first two search attempts in testing failed with "Request blocked
by Booking.com. Please wait a few minutes before retrying" before a
third attempt succeeded. hotelzero has built-in retry/backoff and user-
agent rotation for this, but treat this provider as meaningfully more
fragile than Airbnb's. Do not hammer it in a loop.

Upstream: https://github.com/insprd/hotelzero
"""

from __future__ import annotations

from typing import Any

from travelprep_mcp.providers.base import StdioProvider

_provider = StdioProvider(package="hotelzero")


async def search(
    location: str,
    checkin: str,
    checkout: str,
    adults: int = 2,
    rooms: int = 1,
) -> Any:
    """Basic search via `search_hotels`. checkin/checkout are required upstream."""
    return await _provider.call_tool(
        "search_hotels",
        {
            "destination": location,
            "checkIn": checkin,
            "checkOut": checkout,
            "guests": adults,
            "rooms": rooms,
        },
    )


async def hotel_details(hotel_url: str) -> Any:
    return await _provider.call_tool("get_hotel_details", {"url": hotel_url})


async def price_calendar(
    hotel_url: str,
    start_date: str,
    nights: int = 14,
    guests: int = 2,
    rooms: int = 1,
    currency: str = "EUR",
) -> Any:
    """Find the cheapest dates for a given hotel."""
    return await _provider.call_tool(
        "get_price_calendar",
        {
            "hotelUrl": hotel_url,
            "startDate": start_date,
            "nights": nights,
            "guests": guests,
            "rooms": rooms,
            "currency": currency,
        },
    )


async def find_hotels(
    location: str,
    checkin: str,
    checkout: str,
    adults: int = 2,
    rooms: int = 1,
    filters: dict[str, Any] | None = None,
) -> Any:
    """Filtered search via `find_hotels` (80+ filter codes upstream). `filters` is
    passed through as-is -- see hotelzero's README for the filter key catalog;
    we don't re-validate it here."""
    args: dict[str, Any] = {
        "destination": location,
        "checkIn": checkin,
        "checkOut": checkout,
        "guests": adults,
        "rooms": rooms,
    }
    if filters:
        args.update(filters)
    return await _provider.call_tool("find_hotels", args)


async def compare_hotels(hotel_urls: list[str]) -> Any:
    if not (2 <= len(hotel_urls) <= 3):
        raise ValueError("compare_hotels takes 2-3 hotel URLs")
    return await _provider.call_tool("compare_hotels", {"hotelUrls": hotel_urls})


async def check_availability(
    hotel_url: str, checkin: str, checkout: str, guests: int = 2, rooms: int = 1
) -> Any:
    return await _provider.call_tool(
        "check_availability",
        {
            "hotelUrl": hotel_url,
            "checkIn": checkin,
            "checkOut": checkout,
            "guests": guests,
            "rooms": rooms,
        },
    )


async def get_reviews(
    hotel_url: str,
    sort_by: str = "recent",
    filter_by: str | None = None,
) -> Any:
    args: dict[str, Any] = {"hotelUrl": hotel_url, "sortBy": sort_by}
    if filter_by:
        args["filterBy"] = filter_by
    return await _provider.call_tool("get_reviews", args)
