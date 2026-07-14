"""Account tool -- Booking.com trips/wishlist/rewards via the isolated
Playwright profile (travelprep_mcp.auth.booking_session).

Status: `login` and `status` are simple enough to trust. `trips` /
`wishlist` / `rewards` call into booking_account.py, whose parsing is
an unverified first pass -- see that module's docstring. Not live
tested end-to-end as of 2026-07-14.
"""

from __future__ import annotations

from typing import Any, Literal

from travelprep_mcp.auth import booking_session
from travelprep_mcp.providers import booking_account

AccountOperation = Literal["login", "status", "trips", "wishlist", "rewards"]


async def account(operation: AccountOperation) -> dict[str, Any]:
    """Booking.com account access via a locally-persisted, isolated login session.

    operation:
        login    - opens a headed browser window for Sandra to log in to
                   Booking.com by hand; session then persists locally
        status   - whether a local session profile exists (does not
                   confirm it's still valid -- Booking.com may have
                   expired it; a real fetch will surface that)
        trips    - past and upcoming bookings
        wishlist - saved properties
        rewards  - Genius level / wallet / rewards balance

    No booking-execution capability exists here or anywhere in this
    server -- see budget.py for why that's a deliberate omission.
    """
    if operation == "login":
        detected = await booking_session.login_interactive()
        return {
            "operation": operation,
            "login_detected": detected,
            "profile_dir": str(booking_session.PROFILE_DIR),
        }

    if operation == "status":
        return {"operation": operation, "has_profile": booking_session.has_profile()}

    if operation == "trips":
        return {"operation": operation, "result": await booking_account.trips()}

    if operation == "wishlist":
        return {"operation": operation, "result": await booking_account.wishlist()}

    if operation == "rewards":
        return {"operation": operation, "result": await booking_account.rewards()}

    raise ValueError(f"Unknown operation: {operation}")
