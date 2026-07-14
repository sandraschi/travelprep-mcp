"""Live smoke test -- destination tool hits real, free, keyless APIs.

Not mocked on purpose: this repo's whole selling point is "free sources
that actually work." Run with:  uv run pytest tests/test_destination.py -v
"""

import pytest

from travelprep_mcp.tools.destination import destination


@pytest.mark.asyncio
async def test_overview_kew_gardens():
    result = await destination(operation="overview", place="Kew Gardens")
    assert result["overview"]["available"] is True
    assert "extract" in result["overview"]
    assert len(result["overview"]["extract"]) > 20


@pytest.mark.asyncio
async def test_weather_vienna():
    result = await destination(operation="weather", place="Vienna", forecast_days=3)
    assert result["weather"]["available"] is True
    assert len(result["weather"]["days"]) == 3
    assert result["weather"]["days"][0]["temp_max_c"] is not None


@pytest.mark.asyncio
async def test_practical_richmond_london():
    result = await destination(operation="practical", place="Richmond, London")
    practical = result["practical"]
    # Wikivoyage page may or may not exist under this exact title; the
    # country lookup via Open-Meteo geocoding should still resolve.
    assert "country" in practical or practical.get("available") is False


@pytest.mark.asyncio
async def test_full_unknown_place_degrades_gracefully():
    result = await destination(operation="full", place="Qwzzxnotarealplace123")
    assert result["overview"]["available"] is False
    assert "reason" in result["overview"]
