"""Stays tool -- portmanteau front for accommodation search providers.

Status: provider dispatch is real; the underlying `airbnb_client` has
its tool names/schema confirmed (see that module's docstring) but the
StdioProvider subprocess path itself is untested pending
tests/test_airbnb_client.py. `booking_client` (hotelzero) tool names
are unverified. Do not treat this as a working end-to-end tool yet --
see README "Status" section.
"""

from __future__ import annotations

from typing import Any, Literal

from travelprep_mcp.providers import airbnb_client, booking_client

StaysOperation = Literal["search", "details"]
StaysProvider = Literal["airbnb", "booking"]


async def stays(
    operation: StaysOperation,
    provider: StaysProvider,
    location: str | None = None,
    listing_id: str | None = None,
    checkin: str | None = None,
    checkout: str | None = None,
    adults: int = 1,
    children: int = 0,
    min_price: int | None = None,
    max_price: int | None = None,
) -> dict[str, Any]:
    """Search or fetch details for a stay via Airbnb or Booking.com.

    operation:
        search  - requires `location`; optional checkin/checkout/adults/
                  children/min_price/max_price
        details - requires `listing_id` (airbnb) or `listing_id` as the
                  hotel URL (booking); optional checkin/checkout/adults

    provider: "airbnb" or "booking". Both are subprocess-wrapped
    open-source scrapers (MIT), no paid API key involved. Neither
    provider's location filtering is tight -- results should be
    sanity-checked against returned coordinates for anything where
    precise geography matters. See individual provider docstrings.

    ## Return Format
    {"provider": str, "operation": str, "result": dict}

    ## Examples
    stays(operation="search", provider="airbnb", location="Paris", checkin="2026-08-01", checkout="2026-08-07")
    stays(operation="details", provider="booking", listing_id="https://www.booking.com/hotel/fr/example")
    """
    if operation == "search":
        if not location:
            raise ValueError("operation='search' requires 'location'")
        if provider == "airbnb":
            result = await airbnb_client.search(
                location=location,
                checkin=checkin,
                checkout=checkout,
                adults=adults,
                children=children,
                min_price=min_price,
                max_price=max_price,
            )
        else:
            if not checkin or not checkout:
                raise ValueError("provider='booking' requires both 'checkin' and 'checkout'")
            result = await booking_client.search(
                location=location, checkin=checkin, checkout=checkout, adults=adults
            )
        return {"provider": provider, "operation": operation, "result": result}

    if operation == "details":
        if not listing_id:
            raise ValueError("operation='details' requires 'listing_id'")
        if provider == "airbnb":
            result = await airbnb_client.listing_details(
                listing_id=listing_id, checkin=checkin, checkout=checkout, adults=adults
            )
        else:
            result = await booking_client.hotel_details(hotel_url=listing_id)
        return {"provider": provider, "operation": operation, "result": result}

    raise ValueError(f"Unknown operation: {operation}")
