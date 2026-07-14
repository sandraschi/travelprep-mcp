"""Hardcoded sanity caps for accommodation spend.

Not a booking gate -- this server has no booking-execution tool, and
building one is out of scope here on purpose: actually charging a
payment method is something that needs an explicit yes from Sandra on
every single occasion, cap or no cap. What this *is* for: a hard
pre-check that any search/price result can be run through so an absurd
result (three weeks in the Ritz-Carlton presidential suite) shows up
flagged rather than silently sorted to the top of a "cheapest" list,
and a ready-made guard for whenever a booking tool does get built.

Values are Sandra's, hardcoded deliberately rather than configurable
per-call -- the point is a fixed ceiling an agent can't argue its way
around by passing a bigger number.
"""

from __future__ import annotations

MAX_NIGHTLY_RATE_EUR: float = 300.0
MAX_TOTAL_TRIP_EUR: float = 1500.0


def within_budget(
    nightly_rate: float | None = None,
    total: float | None = None,
    nights: int | None = None,
) -> dict[str, bool | str | None]:
    """Check a price against the hardcoded caps.

    Pass whichever of nightly_rate / total you have; if both nightly_rate
    and nights are given but not total, total is derived. Returns a dict
    always safe to merge into a result payload -- never raises.
    """
    if total is None and nightly_rate is not None and nights is not None:
        total = nightly_rate * nights

    nightly_ok = nightly_rate is None or nightly_rate <= MAX_NIGHTLY_RATE_EUR
    total_ok = total is None or total <= MAX_TOTAL_TRIP_EUR

    reason = None
    if not nightly_ok and not total_ok:
        reason = (
            f"nightly rate {nightly_rate} exceeds cap {MAX_NIGHTLY_RATE_EUR} "
            f"and total {total} exceeds cap {MAX_TOTAL_TRIP_EUR}"
        )
    elif not nightly_ok:
        reason = f"nightly rate {nightly_rate} exceeds cap {MAX_NIGHTLY_RATE_EUR}"
    elif not total_ok:
        reason = f"total {total} exceeds cap {MAX_TOTAL_TRIP_EUR}"

    return {
        "within_budget": nightly_ok and total_ok,
        "max_nightly_rate_eur": MAX_NIGHTLY_RATE_EUR,
        "max_total_trip_eur": MAX_TOTAL_TRIP_EUR,
        "reason": reason,
    }
