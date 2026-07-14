"""Airbnb provider -- wraps openbnb-org/mcp-server-airbnb (MIT) over stdio.

Status: LIVE-TESTED 2026-07-14 (tests/test_airbnb_client.py, npx cold
start + real network call, 18 results returned). Confirmed root cause
of loose location matching: Photon resolves e.g. "Kew" to a district
with no extent, the server falls back to Nominatim, and Nominatim's
result gets a 25% bounding-box padding applied before the Airbnb query
-- so a "Kew" search can legitimately return Wembley or Hampstead.
Callers must filter results by returned lat/lng, not trust the search
radius. See stays.py.

Upstream: https://github.com/openbnb-org/mcp-server-airbnb

Known upstream limitation, not ours to fix here: the location-bounding-box
geocoding (Photon/Nominatim client-side) is loose, so a query like
"Richmond, London, UK" can return results from well outside the named
area. Callers should filter by returned lat/lng against a known reference
point rather than trusting the search radius. See stays.py.
"""

from __future__ import annotations

from typing import Any

from travelprep_mcp.providers.base import StdioProvider

_provider = StdioProvider(
    package="@openbnb/mcp-server-airbnb",
    extra_args=["--ignore-robots-txt"],
)


async def search(
    location: str,
    checkin: str | None = None,
    checkout: str | None = None,
    adults: int = 1,
    children: int = 0,
    min_price: int | None = None,
    max_price: int | None = None,
) -> Any:
    args: dict[str, Any] = {"location": location, "adults": adults, "children": children}
    if checkin:
        args["checkin"] = checkin
    if checkout:
        args["checkout"] = checkout
    if min_price is not None:
        args["minPrice"] = min_price
    if max_price is not None:
        args["maxPrice"] = max_price
    return await _provider.call_tool("airbnb_search", args)


async def listing_details(
    listing_id: str,
    checkin: str | None = None,
    checkout: str | None = None,
    adults: int = 1,
) -> Any:
    args: dict[str, Any] = {"id": listing_id, "adults": adults}
    if checkin:
        args["checkin"] = checkin
    if checkout:
        args["checkout"] = checkout
    return await _provider.call_tool("airbnb_listing_details", args)
