"""travelprep-mcp server -- FastMCP 3.2+, dual transport (stdio + HTTP /mcp).

Tools:
    stays(operation, provider, ...)        -- Airbnb / Booking.com search+details
    destination(operation, place, ...)     -- free-source destination info

Run:
    uv run travelprep-mcp                  # stdio (default, for Claude Desktop etc)
    MCP_TRANSPORT=http uv run travelprep-mcp   # streamable HTTP on /mcp, port 11099
"""

from __future__ import annotations

import os

from fastmcp import FastMCP

from travelprep_mcp.tools.destination import destination as destination_impl
from travelprep_mcp.tools.stays import stays as stays_impl

mcp = FastMCP(
    name="travelprep-mcp",
    instructions=(
        "Trip preparation tools: search and inspect accommodation listings "
        "on Airbnb and Booking.com (stays tool), and pull free-source "
        "destination info -- overview, weather, practical/currency/language "
        "facts (destination tool). No paid API keys required for anything "
        "in this server."
    ),
)


@mcp.tool()
async def stays(
    operation: str,
    provider: str,
    location: str | None = None,
    listing_id: str | None = None,
    checkin: str | None = None,
    checkout: str | None = None,
    adults: int = 1,
    children: int = 0,
    min_price: int | None = None,
    max_price: int | None = None,
) -> dict:
    """Search or fetch details for accommodation via Airbnb or Booking.com.

    operation: "search" | "details"
    provider: "airbnb" | "booking"
    """
    return await stays_impl(
        operation=operation,  # type: ignore[arg-type]
        provider=provider,  # type: ignore[arg-type]
        location=location,
        listing_id=listing_id,
        checkin=checkin,
        checkout=checkout,
        adults=adults,
        children=children,
        min_price=min_price,
        max_price=max_price,
    )


@mcp.tool()
async def destination(
    operation: str,
    place: str,
    forecast_days: int = 7,
) -> dict:
    """Free-source destination info.

    operation: "overview" | "weather" | "practical" | "full"
    """
    return await destination_impl(
        operation=operation,  # type: ignore[arg-type]
        place=place,
        forecast_days=forecast_days,
    )


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio").lower()
    if transport == "http":
        mcp.run(transport="http", host="127.0.0.1", port=11099, path="/mcp")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
