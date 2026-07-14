"""Live end-to-end test -- actual call_tool invocation, not just schema probe."""

import pytest

from travelprep_mcp.providers import booking_client


@pytest.mark.asyncio
async def test_booking_search_smoke():
    result = await booking_client.search(
        location="Richmond, London, UK", checkin="2026-08-10", checkout="2026-08-13"
    )
    assert result is not None
