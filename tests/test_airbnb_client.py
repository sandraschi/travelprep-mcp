"""Live smoke test -- proves the StdioProvider subprocess path actually
works against the real openbnb-org/mcp-server-airbnb package via npx.

Slow (npx cold-start + real network call to Airbnb). Run explicitly:
    uv run pytest tests/test_airbnb_client.py -v -s
"""

import pytest

from travelprep_mcp.providers import airbnb_client


@pytest.mark.asyncio
async def test_airbnb_search_smoke():
    result = await airbnb_client.search(location="Kew, Richmond upon Thames, London, UK")
    assert result is not None
