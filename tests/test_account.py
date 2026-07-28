"""Unit tests for account tool -- mocked booking_session and booking_account."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from travelprep_mcp.tools.account import account


@pytest.mark.asyncio
async def test_login_delegates_correctly():
    with (
        patch(
            "travelprep_mcp.tools.account.booking_session.login_interactive", new_callable=AsyncMock
        ) as mock_login,
        patch(
            "travelprep_mcp.tools.account.booking_session.PROFILE_DIR", new_callable=MagicMock
        ) as mock_dir,
    ):
        mock_login.return_value = True
        mock_dir.__str__.return_value = "/fake/.travelprep-mcp/booking-profile"
        result = await account(operation="login")
    mock_login.assert_awaited_once()
    assert result["operation"] == "login"
    assert result["login_detected"] is True
    assert "profile_dir" in result


@pytest.mark.asyncio
async def test_status_has_profile_true():
    with patch(
        "travelprep_mcp.tools.account.booking_session.has_profile", return_value=True
    ) as mock_status:
        result = await account(operation="status")
    mock_status.assert_called_once()
    assert result["operation"] == "status"
    assert result["has_profile"] is True


@pytest.mark.asyncio
async def test_status_has_profile_false():
    with patch(
        "travelprep_mcp.tools.account.booking_session.has_profile", return_value=False
    ) as mock_status:
        result = await account(operation="status")
    mock_status.assert_called_once()
    assert result["has_profile"] is False


@pytest.mark.asyncio
async def test_trips_delegates_correctly():
    mock_result = {"trips": []}
    with patch(
        "travelprep_mcp.tools.account.booking_account.trips", new_callable=AsyncMock
    ) as mock_trips:
        mock_trips.return_value = mock_result
        result = await account(operation="trips")
    mock_trips.assert_awaited_once()
    assert result["operation"] == "trips"
    assert result["result"] == mock_result


@pytest.mark.asyncio
async def test_wishlist_delegates_correctly():
    mock_result = {"properties": []}
    with patch(
        "travelprep_mcp.tools.account.booking_account.wishlist", new_callable=AsyncMock
    ) as mock_wl:
        mock_wl.return_value = mock_result
        result = await account(operation="wishlist")
    mock_wl.assert_awaited_once()
    assert result["operation"] == "wishlist"
    assert result["result"] == mock_result


@pytest.mark.asyncio
async def test_rewards_delegates_correctly():
    mock_result = {"genius_level": 3}
    with patch(
        "travelprep_mcp.tools.account.booking_account.rewards", new_callable=AsyncMock
    ) as mock_rw:
        mock_rw.return_value = mock_result
        result = await account(operation="rewards")
    mock_rw.assert_awaited_once()
    assert result["operation"] == "rewards"
    assert result["result"] == mock_result


@pytest.mark.asyncio
async def test_unknown_operation():
    with pytest.raises(ValueError, match="Unknown operation: delete_account"):
        await account(operation="delete_account")
