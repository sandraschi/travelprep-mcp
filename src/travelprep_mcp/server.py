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
    GET  /api/skills                       -- list registered skills
    GET  /skill/{name}                     -- raw SKILL.md content for one skill
    GET  /api/llm/discover                 -- local Ollama/LM Studio auto-detection

MCP resources:
    skill://travelprep-expert/SKILL.md     -- same skill content, MCP resource form

Run:
    uv run travelprep-mcp                  # stdio (default, for Claude Desktop etc)
    MCP_TRANSPORT=http uv run travelprep-mcp   # streamable HTTP on /mcp, port 11099
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse

from travelprep_mcp import __version__, llm_discovery
from travelprep_mcp.tools.account import account as account_impl
from travelprep_mcp.tools.destination import destination as destination_impl
from travelprep_mcp.tools.hotel_extras import hotel_extras as hotel_extras_impl
from travelprep_mcp.tools.stays import stays as stays_impl

_READ_ONLY = {"readonly": True}
_SKILLS_DIR = Path(__file__).parent / "skills"
_PRIMARY_SKILL = "travelprep-expert"

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


@mcp.tool(annotations=_READ_ONLY)
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


@mcp.tool(annotations=_READ_ONLY)
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


@mcp.tool(annotations=_READ_ONLY)
async def account(operation: str) -> dict:
    """Booking.com account access -- trips, wishlist, rewards.

    operation: "login" | "status" | "trips" | "wishlist" | "rewards"

    Uses a locally-persisted, isolated login session (never Sandra's
    live default browser profile) -- run operation="login" once first.
    No booking-execution capability exists anywhere in this server.
    """
    return await account_impl(operation=operation)  # type: ignore[arg-type]


@mcp.tool(annotations=_READ_ONLY)
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


@mcp.resource(f"skill://{_PRIMARY_SKILL}/SKILL.md")
def get_travelprep_expert_skill() -> str:
    """The travelprep-expert skill content, as an MCP resource."""
    path = _SKILLS_DIR / _PRIMARY_SKILL / "SKILL.md"
    return path.read_text(encoding="utf-8") if path.exists() else "not found"


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
                "resources": True,
                "skills": True,
            },
            "inventory": {
                "workflow_tools": [],
                "prompt_names": [],
                "resource_uris": [f"skill://{_PRIMARY_SKILL}/SKILL.md"],
                "skill_uris": [f"skill://{_PRIMARY_SKILL}/SKILL.md"],
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


@mcp.custom_route("/api/skills", methods=["GET"])
async def api_skills(request: Request) -> JSONResponse:
    """List registered skills (WEBAPP_SOTA_STANDARDS.md §V)."""
    if not _SKILLS_DIR.exists():
        return JSONResponse({"skills": []})
    skills = []
    for skill_dir in sorted(_SKILLS_DIR.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            first_line = skill_file.read_text(encoding="utf-8").splitlines()[0].lstrip("# ")
            skills.append(
                {
                    "id": skill_dir.name,
                    "name": skill_dir.name,
                    "description": first_line,
                    "uri": f"skill://{skill_dir.name}/SKILL.md",
                }
            )
    return JSONResponse({"skills": skills})


@mcp.custom_route("/skill/{skill_name}", methods=["GET"])
async def get_skill(request: Request) -> PlainTextResponse:
    """Raw SKILL.md content for one skill (WEBAPP_SOTA_STANDARDS.md §V)."""
    skill_name = request.path_params["skill_name"]
    skill_path = _SKILLS_DIR / skill_name / "SKILL.md"
    if skill_path.exists():
        return PlainTextResponse(skill_path.read_text(encoding="utf-8"))
    return PlainTextResponse("not found", status_code=404)


@mcp.custom_route("/api/llm/discover", methods=["GET"])
async def api_llm_discover(request: Request) -> JSONResponse:
    """Local Ollama/LM Studio auto-detection (WEBAPP_SOTA_STANDARDS.md §VI, 'Glom On')."""
    return JSONResponse(await llm_discovery.discover())


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio").lower()
    if transport == "http":
        mcp.run(transport="http", host="127.0.0.1", port=11099, path="/mcp")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
