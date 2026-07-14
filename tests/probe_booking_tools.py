"""Discovers hotelzero's real tool names/schema via list_tools().

Not a pass/fail test -- a one-shot probe to replace the guessed tool
names in booking_client.py with the real ones. Run manually:
    uv run pytest tests/probe_booking_tools.py -v -s
"""

import json

import pytest

from travelprep_mcp.providers.base import StdioProvider


@pytest.mark.asyncio
async def test_probe_hotelzero_tools():
    provider = StdioProvider(package="hotelzero")
    tools = await provider.list_tools()
    print(json.dumps([t.model_dump() for t in tools.tools], indent=2, default=str))
