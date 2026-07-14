"""Unit tests for budget.within_budget."""

from travelprep_mcp.budget import within_budget


def test_nightly_rate_under_300():
    result = within_budget(nightly_rate=250.0)
    assert result["within_budget"] is True
    assert result["reason"] is None


def test_nightly_rate_over_300():
    result = within_budget(nightly_rate=350.0)
    assert result["within_budget"] is False
    assert "nightly rate 350.0 exceeds cap 300.0" in result["reason"]


def test_nightly_rate_at_boundary():
    result = within_budget(nightly_rate=300.0)
    assert result["within_budget"] is True


def test_total_under_1500():
    result = within_budget(total=1200.0)
    assert result["within_budget"] is True


def test_total_over_1500():
    result = within_budget(total=2000.0)
    assert result["within_budget"] is False
    assert "total 2000.0 exceeds cap 1500.0" in result["reason"]


def test_total_at_boundary():
    result = within_budget(total=1500.0)
    assert result["within_budget"] is True


def test_both_over():
    result = within_budget(nightly_rate=400.0, total=2000.0)
    assert result["within_budget"] is False
    assert "nightly rate 400.0 exceeds cap 300.0" in result["reason"]
    assert "total 2000.0 exceeds cap 1500.0" in result["reason"]


def test_total_derived_from_nightly_rate_times_nights():
    result = within_budget(nightly_rate=100.0, nights=5)
    assert result["within_budget"] is True


def test_total_derived_exceeds_cap():
    result = within_budget(nightly_rate=200.0, nights=10)
    assert result["within_budget"] is False
    assert "total 2000.0 exceeds cap 1500.0" in result["reason"]


def test_none_nightly_rate():
    result = within_budget(nightly_rate=None, total=500.0)
    assert result["within_budget"] is True


def test_none_total():
    result = within_budget(nightly_rate=200.0, total=None)
    assert result["within_budget"] is True


def test_no_params():
    result = within_budget()
    assert result["within_budget"] is True
    assert result["reason"] is None


def test_nightly_rate_under_total_over():
    result = within_budget(nightly_rate=200.0, total=1600.0)
    assert result["within_budget"] is False
    assert "total 1600.0 exceeds cap 1500.0" in result["reason"]


def test_caps_always_echoed():
    result = within_budget(nightly_rate=100.0)
    assert result["max_nightly_rate_eur"] == 300.0
    assert result["max_total_trip_eur"] == 1500.0
