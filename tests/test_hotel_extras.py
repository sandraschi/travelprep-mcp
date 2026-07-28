"""Unit tests for hotel_extras tool -- mocked booking_client calls."""

from unittest.mock import AsyncMock, patch

import pytest

from travelprep_mcp.tools.hotel_extras import hotel_extras


@pytest.mark.asyncio
async def test_find_hotels_delegates_correctly():
    mock_result = {"some": "data"}
    with patch(
        "travelprep_mcp.tools.hotel_extras.booking_client.find_hotels", new_callable=AsyncMock
    ) as mock_find:
        mock_find.return_value = mock_result
        result = await hotel_extras(
            operation="find_hotels",
            location="London",
            checkin="2026-09-01",
            checkout="2026-09-07",
            adults=2,
            rooms=1,
        )
    mock_find.assert_awaited_once_with(
        location="London",
        checkin="2026-09-01",
        checkout="2026-09-07",
        adults=2,
        rooms=1,
        filters=None,
    )
    assert result["operation"] == "find_hotels"
    assert result["result"] == mock_result
    assert "budget_caps" in result


@pytest.mark.asyncio
async def test_find_hotels_missing_params():
    with pytest.raises(ValueError, match="find_hotels requires location, checkin, checkout"):
        await hotel_extras(operation="find_hotels")
    with pytest.raises(ValueError, match="find_hotels requires location, checkin, checkout"):
        await hotel_extras(operation="find_hotels", location="Paris", checkin="2026-09-01")


@pytest.mark.asyncio
async def test_compare_delegates_correctly():
    mock_result = {"comparison": "done"}
    urls = ["https://booking.com/hotel/a", "https://booking.com/hotel/b"]
    with patch(
        "travelprep_mcp.tools.hotel_extras.booking_client.compare_hotels", new_callable=AsyncMock
    ) as mock_cmp:
        mock_cmp.return_value = mock_result
        result = await hotel_extras(operation="compare", hotel_urls=urls)
    mock_cmp.assert_awaited_once_with(urls)
    assert result["operation"] == "compare"
    assert result["result"] == mock_result


@pytest.mark.asyncio
async def test_compare_missing_urls():
    with pytest.raises(ValueError, match="compare requires hotel_urls"):
        await hotel_extras(operation="compare")


@pytest.mark.asyncio
async def test_check_availability_delegates_correctly():
    mock_result = {"available": True}
    with patch(
        "travelprep_mcp.tools.hotel_extras.booking_client.check_availability",
        new_callable=AsyncMock,
    ) as mock_avail:
        mock_avail.return_value = mock_result
        result = await hotel_extras(
            operation="check_availability",
            hotel_url="https://booking.com/hotel/test",
            checkin="2026-09-01",
            checkout="2026-09-07",
            adults=2,
            rooms=1,
        )
    mock_avail.assert_awaited_once_with(
        hotel_url="https://booking.com/hotel/test",
        checkin="2026-09-01",
        checkout="2026-09-07",
        guests=2,
        rooms=1,
    )
    assert result["operation"] == "check_availability"


@pytest.mark.asyncio
async def test_check_availability_missing_params():
    with pytest.raises(
        ValueError, match="check_availability requires hotel_url, checkin, checkout"
    ):
        await hotel_extras(
            operation="check_availability", hotel_url="https://booking.com/hotel/test"
        )


@pytest.mark.asyncio
async def test_reviews_delegates_correctly():
    mock_result = {"reviews": []}
    with patch(
        "travelprep_mcp.tools.hotel_extras.booking_client.get_reviews", new_callable=AsyncMock
    ) as mock_rev:
        mock_rev.return_value = mock_result
        result = await hotel_extras(
            operation="reviews",
            hotel_url="https://booking.com/hotel/test",
            sort_by="recent",
            filter_by=None,
        )
    mock_rev.assert_awaited_once_with(
        hotel_url="https://booking.com/hotel/test",
        sort_by="recent",
        filter_by=None,
    )
    assert result["operation"] == "reviews"


@pytest.mark.asyncio
async def test_reviews_missing_url():
    with pytest.raises(ValueError, match="reviews requires hotel_url"):
        await hotel_extras(operation="reviews")


@pytest.mark.asyncio
async def test_price_calendar_delegates_correctly():
    mock_result = {"cheapest_dates": []}
    with patch(
        "travelprep_mcp.tools.hotel_extras.booking_client.price_calendar", new_callable=AsyncMock
    ) as mock_cal:
        mock_cal.return_value = mock_result
        result = await hotel_extras(
            operation="price_calendar",
            hotel_url="https://booking.com/hotel/test",
            price_calendar_start="2026-09-01",
            price_calendar_nights=14,
            adults=2,
            rooms=1,
        )
    mock_cal.assert_awaited_once_with(
        hotel_url="https://booking.com/hotel/test",
        start_date="2026-09-01",
        nights=14,
        guests=2,
        rooms=1,
    )
    assert result["operation"] == "price_calendar"


@pytest.mark.asyncio
async def test_price_calendar_missing_params():
    with pytest.raises(ValueError, match="price_calendar requires hotel_url, price_calendar_start"):
        await hotel_extras(operation="price_calendar", hotel_url="https://booking.com/hotel/test")


@pytest.mark.asyncio
async def test_unknown_operation():
    with pytest.raises(ValueError, match="Unknown operation: invalid_op"):
        await hotel_extras(operation="invalid_op")


@pytest.mark.asyncio
async def test_budget_caps_echoed():
    with patch(
        "travelprep_mcp.tools.hotel_extras.booking_client.find_hotels", new_callable=AsyncMock
    ) as mock_find:
        mock_find.return_value = {}
        result = await hotel_extras(
            operation="find_hotels",
            location="Paris",
            checkin="2026-09-01",
            checkout="2026-09-07",
        )
    caps = result["budget_caps"]
    assert caps["max_nightly_rate_eur"] == 300.0
    assert caps["max_total_trip_eur"] == 1500.0
    assert "note" in caps
