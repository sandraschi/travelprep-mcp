"""Isolated, persistent Playwright profile for Booking.com account access.

Design note -- deliberately NOT what booking-com-pp-cli does. That tool's
`auth login --chrome` decrypts session cookies straight out of your live
default Chrome profile (via a Go cookie-capture tool, falling back to
pycookiecheat). That works, but it means bugs or a supply-chain problem
in that tool can act as you anywhere you're logged in in Chrome, not
just on Booking.com.

Instead: a dedicated Chromium profile directory under
~/.travelprep-mcp/booking-profile, isolated from any other browser
profile on this machine. Sandra logs in once, interactively, in a
headed window (`login_interactive()`); Playwright's persistent context
then keeps that session on disk like any browser profile would. No
cookie decryption, no touching Chrome's encrypted cookie store.
Revoke access at any time by deleting the profile directory.

Status: UNTESTED. Written 2026-07-14, not yet run against a real
Booking.com login. `login_interactive()` in particular needs a live
run to confirm the post-login detection heuristic actually fires.
"""

from __future__ import annotations

from pathlib import Path

from playwright.async_api import BrowserContext, async_playwright

PROFILE_DIR = Path.home() / ".travelprep-mcp" / "booking-profile"

# Heuristic only -- not yet confirmed live. Booking.com's logged-in header
# shows the account name/avatar; this selector is a best guess pending a
# real login to inspect the actual DOM.
_LOGGED_IN_SELECTOR = "[data-testid='header-profile-menu-trigger']"


async def login_interactive(timeout_ms: int = 300_000) -> bool:
    """Open a headed browser for Sandra to log in to Booking.com by hand.

    Waits up to `timeout_ms` for the logged-in header element to appear.
    Returns True if detected, False on timeout (session may still have
    succeeded -- the selector is unverified, see module docstring).
    """
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        context = await pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1280, "height": 900},
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://www.booking.com/signin.html", wait_until="domcontentloaded")
        try:
            await page.wait_for_selector(_LOGGED_IN_SELECTOR, timeout=timeout_ms)
            detected = True
        except Exception:
            detected = False
        await context.close()
        return detected


async def get_context(pw, headless: bool = True) -> BrowserContext:
    """Reuse the persisted profile for a scripted (headless) session.

    Caller owns the `async_playwright()` context manager and passes the
    `pw` handle in, so this can be composed with other Playwright calls
    in the same session. Raises FileNotFoundError if no profile exists
    yet -- call `login_interactive()` first.
    """
    if not PROFILE_DIR.exists():
        raise FileNotFoundError(
            f"No Booking.com session profile at {PROFILE_DIR}. "
            "Run the account tool's 'login' operation first."
        )
    return await pw.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=headless,
    )


def has_profile() -> bool:
    return PROFILE_DIR.exists() and any(PROFILE_DIR.iterdir())
