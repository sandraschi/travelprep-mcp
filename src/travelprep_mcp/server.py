"""travelprep-mcp server -- FastMCP 3.4+, dual transport (stdio + HTTP /mcp).

MCP tools:
    stays(operation, provider, ...)        -- Airbnb / Booking.com search+details
    hotel_extras(operation, ...)           -- Booking.com-only: find_hotels,
                                               compare, check_availability,
                                               reviews, price_calendar
    account(operation)                     -- Booking.com trips/wishlist/rewards
                                               via a locally-persisted login
                                               session (see auth/booking_session.py)
    destination(operation, place, ...)     -- free-source destination info

REST (webapp-facing, HTTP transport only, added via custom_route):
    GET  /api/capabilities                 -- mandatory capability introspection
    GET  /api/tools                        -- dynamic tool list for Tools Hub
    GET  /api/health                       -- liveness

Run:
    uv run travelprep-mcp                  # stdio (default, for Claude Desktop etc)
    MCP_TRANSPORT=http uv run travelprep-mcp   # streamable HTTP on /mcp, port 11099
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from travelprep_mcp import __version__
from travelprep_mcp.tools.account import account as account_impl
from travelprep_mcp.tools.destination import destination as destination_impl
from travelprep_mcp.tools.hotel_extras import hotel_extras as hotel_extras_impl
from travelprep_mcp.tools.stays import stays as stays_impl

mcp = FastMCP(
    name="travelprep-mcp",
    instructions=(
        "Trip preparation tools: search and inspect accommodation listings "
        "on Airbnb and Booking.com (stays, hotel_extras tools), and pull "
        "free-source destination info -- overview, weather, "
        "practical/currency/language facts (destination tool). No paid API "
        "keys required for anything in this server."
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
async def hotel_extras(
    operation: str,
    location: str | None = None,
    hotel_url: str | None = None,
    hotel_urls: list[str] | None = None,
    checkin: str | None = None,
    checkout: str | None = None,
    adults: int = 2,
    rooms: int = 1,
    filters: dict | None = None,
    sort_by: str = "recent",
    filter_by: str | None = None,
    price_calendar_start: str | None = None,
    price_calendar_nights: int = 14,
) -> dict:
    """Booking.com-only extras beyond basic search/details.

    operation: "find_hotels" | "compare" | "check_availability" | "reviews" | "price_calendar"
    """
    return await hotel_extras_impl(
        operation=operation,  # type: ignore[arg-type]
        location=location,
        hotel_url=hotel_url,
        hotel_urls=hotel_urls,
        checkin=checkin,
        checkout=checkout,
        adults=adults,
        rooms=rooms,
        filters=filters,
        sort_by=sort_by,
        filter_by=filter_by,
        price_calendar_start=price_calendar_start,
        price_calendar_nights=price_calendar_nights,
    )


@mcp.tool()
async def account(operation: str) -> dict:
    """Booking.com account access -- trips, wishlist, rewards.

    operation: "login" | "status" | "trips" | "wishlist" | "rewards"

    Uses a locally-persisted, isolated login session (never Sandra's
    live default browser profile) -- run operation="login" once first.
    No booking-execution capability exists anywhere in this server.
    """
    return await account_impl(operation=operation)  # type: ignore[arg-type]


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


# --- REST layer for the webapp (HTTP transport only) -----------------------


@mcp.custom_route("/api/capabilities", methods=["GET"])
async def api_capabilities(request: Request) -> JSONResponse:
    """Mandatory capability introspection endpoint (WEBAPP_STANDARDS.md §1.4)."""
    tools = await mcp.list_tools()

    portmanteau_tools = []
    atomic_tools = []
    for t in tools:
        props = (t.parameters or {}).get("properties", {})
        op_schema = props.get("operation", {})
        has_operation = isinstance(op_schema, dict) and "enum" in op_schema
        if has_operation:
            portmanteau_tools.append(t.name)
        else:
            atomic_tools.append(t.name)

    return JSONResponse(
        {
            "status": "ok",
            "server": {
                "name": "travelprep-mcp",
                "version": __version__,
                "fastmcp": "3.4+",
            },
            "tool_surface": {
                "total": len(tools),
                "portmanteau_count": len(portmanteau_tools),
                "atomic_count": len(atomic_tools),
                "portmanteau_tools": portmanteau_tools,
                "atomic_tools": atomic_tools,
            },
            "features": {
                "sampling": False,
                "agentic_workflows": False,
                "prompts": False,
                "resources": False,
                "skills": False,
            },
            "inventory": {
                "workflow_tools": [],
                "prompt_names": [],
                "resource_uris": [],
                "skill_uris": [],
            },
            "runtime": {
                "transport": "dual",
                "surface_mode": "portmanteau",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )


@mcp.custom_route("/api/health", methods=["GET"])
async def api_health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "version": __version__})


@mcp.custom_route("/api/tools", methods=["GET"])
async def api_tools(request: Request) -> JSONResponse:
    """Dynamic tool list for the Tools Hub -- never hardcode this in the frontend."""
    tools = await mcp.list_tools()
    return JSONResponse(
        [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.parameters,
            }
            for t in tools
        ]
    )


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio").lower()
    if transport == "http":
        mcp.run(transport="http", host="127.0.0.1", port=11099, path="/mcp")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
