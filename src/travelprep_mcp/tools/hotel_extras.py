"""Hotel extras -- Booking.com-only operations beyond basic search/details.

Booking.com's hotelzero backend has no Airbnb equivalent for these, so
this is its own portmanteau rather than folded into `stays`. Wired from
a confirmed live `list_tools()` schema (2026-07-14); `find_hotels` and
`price_calendar` have not each been individually exercised with a live
call yet -- see providers/booking_client.py docstring.
"""

from __future__ import annotations

from typing import Any, Literal

from travelprep_mcp.providers import booking_client

HotelExtrasOperation = Literal[
    "find_hotels", "compare", "check_availability", "reviews", "price_calendar"
]


async def hotel_extras(
    operation: HotelExtrasOperation,
    location: str | None = None,
    hotel_url: str | None = None,
    hotel_urls: list[str] | None = None,
    checkin: str | None = None,
    checkout: str | None = None,
    adults: int = 2,
    rooms: int = 1,
    filters: dict[str, Any] | None = None,
    sort_by: str = "recent",
    filter_by: str | None = None,
    price_calendar_start: str | None = None,
    price_calendar_nights: int = 14,
) -> dict[str, Any]:
    """Booking.com-specific tools beyond basic search/details.

    operation:
        find_hotels        - filtered search (80+ filter codes upstream);
                              needs location, checkin, checkout; optional
                              `filters` dict passed through as-is
        compare             - needs hotel_urls (2-3 Booking.com URLs)
        check_availability  - needs hotel_url, checkin, checkout
        reviews             - needs hotel_url; optional sort_by/filter_by
        price_calendar      - needs hotel_url, price_calendar_start
                              (YYYY-MM-DD); finds cheapest dates over
                              price_calendar_nights nights
    """
    if operation == "find_hotels":
        if not (location and checkin and checkout):
            raise ValueError("find_hotels requires location, checkin, checkout")
        result = await booking_client.find_hotels(
            location=location,
            checkin=checkin,
            checkout=checkout,
            adults=adults,
            rooms=rooms,
            filters=filters,
        )
    elif operation == "compare":
        if not hotel_urls:
            raise ValueError("compare requires hotel_urls (2-3 URLs)")
        result = await booking_client.compare_hotels(hotel_urls)
    elif operation == "check_availability":
        if not (hotel_url and checkin and checkout):
            raise ValueError("check_availability requires hotel_url, checkin, checkout")
        result = await booking_client.check_availability(
            hotel_url=hotel_url, checkin=checkin, checkout=checkout, guests=adults, rooms=rooms
        )
    elif operation == "reviews":
        if not hotel_url:
            raise ValueError("reviews requires hotel_url")
        result = await booking_client.get_reviews(
            hotel_url=hotel_url, sort_by=sort_by, filter_by=filter_by
        )
    elif operation == "price_calendar":
        if not (hotel_url and price_calendar_start):
            raise ValueError("price_calendar requires hotel_url, price_calendar_start")
        result = await booking_client.price_calendar(
            hotel_url=hotel_url,
            start_date=price_calendar_start,
            nights=price_calendar_nights,
            guests=adults,
            rooms=rooms,
        )
    else:
        raise ValueError(f"Unknown operation: {operation}")

    return {"operation": operation, "result": result}
