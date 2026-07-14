"""Booking.com account data (trips, wishlist, rewards) via the isolated
Playwright profile in travelprep_mcp.auth.booking_session.

Status: UNTESTED / FIRST PASS. Written 2026-07-14 without a live logged-in
session to inspect real markup against -- there was no session to test
with yet. Every CSS selector and JSON-shape guess below is exactly that,
a guess based on booking-com-pp-cli's documented candidate endpoints
(mytrips.html, mywishlist.html, rewards_and_wallet, all cookie-auth SSR
pages per their generation notes) and generic Booking.com UI conventions.
Treat every field in the returned dicts as unverified until this has
been run once against a real account and adjusted to match. Do not build
anything downstream that assumes these shapes are stable.

The parsing strategy: try `__NEXT_DATA__` / embedded JSON script tags
first (common on modern Booking.com pages), fall back to scraping
visible card elements by best-guess selector, and always include the
raw page text truncated for manual inspection so a failed parse is
still debuggable rather than silently empty.
"""

from __future__ import annotations

import json
import re
from typing import Any

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from travelprep_mcp.auth import booking_session

_URLS = {
    "trips": "https://secure.booking.com/mytrips.html",
    "wishlist": "https://www.booking.com/mywishlist.html",
    "rewards": "https://secure.booking.com/rewards_and_wallet.html",
}


def _extract_embedded_json(html: str) -> dict[str, Any] | None:
    """Look for a __NEXT_DATA__ or similar embedded JSON state blob."""
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script", attrs={"type": "application/json"}):
        try:
            return json.loads(script.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
    next_data = soup.find("script", id="__NEXT_DATA__")
    if next_data and next_data.string:
        try:
            return json.loads(next_data.string)
        except json.JSONDecodeError:
            pass
    return None


async def _fetch(page_key: str) -> dict[str, Any]:
    async with async_playwright() as pw:
        context = await booking_session.get_context(pw, headless=True)
        page = await context.new_page()
        await page.goto(_URLS[page_key], wait_until="networkidle")

        if re.search(r"sign[\-_]?in", page.url, re.IGNORECASE):
            await context.close()
            return {"error": "not_logged_in", "detail": f"redirected to {page.url}"}

        html = await page.content()
        await context.close()

    embedded = _extract_embedded_json(html)
    return {
        "page": page_key,
        "embedded_json_found": embedded is not None,
        "embedded_json": embedded,
        "raw_html_excerpt": html[:2000] if embedded is None else None,
    }


async def trips() -> dict[str, Any]:
    """Past and upcoming bookings. UNVERIFIED shape, see module docstring."""
    return await _fetch("trips")


async def wishlist() -> dict[str, Any]:
    """Saved/wishlisted properties. UNVERIFIED shape, see module docstring."""
    return await _fetch("wishlist")


async def rewards() -> dict[str, Any]:
    """Genius level / wallet / rewards balance. UNVERIFIED shape, see module docstring."""
    return await _fetch("rewards")
