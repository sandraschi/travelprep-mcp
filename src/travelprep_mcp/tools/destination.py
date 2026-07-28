"""Destination info tool -- free, keyless sources only.

Sources used (no API key required for any of these):
- Wikipedia REST summary API        (city/place overview)
- Wikivoyage REST summary API       (practical travel info, "Get in", etc.)
- Open-Meteo geocoding + forecast   (coordinates + weather, no key)
- REST Countries                    (currency, languages, calling code)

Everything here does a real HTTP call. Nothing is mocked. If a source
is down or the place name doesn't resolve, the tool returns a
structured error rather than fabricating data -- see
IMPLEMENTATION_HONESTY_STANDARD.md.
"""

from __future__ import annotations

from typing import Any, Literal

import httpx

USER_AGENT = "travelprep-mcp/0.1.0 (+https://github.com/sandraschi/travelprep-mcp)"

WIKIPEDIA_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
WIKIVOYAGE_SUMMARY = "https://en.wikivoyage.org/api/rest_v1/page/summary/{title}"
OPEN_METEO_GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST = "https://api.open-meteo.com/v1/forecast"
REST_COUNTRIES = "https://restcountries.com/v3.1/name/{name}"

DestinationOperation = Literal["overview", "weather", "practical", "full"]


async def _get_json(client: httpx.AsyncClient, url: str, **params: Any) -> dict | None:
    try:
        resp = await client.get(url, params=params or None, headers={"User-Agent": USER_AGENT})
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError:
        return None


async def _geocode(client: httpx.AsyncClient, place: str) -> dict | None:
    """Resolve a place name to coordinates via Open-Meteo's geocoder (free, no key)."""
    data = await _get_json(client, OPEN_METEO_GEOCODE, name=place, count=1, language="en")
    results = (data or {}).get("results") or []
    return results[0] if results else None


async def _overview(client: httpx.AsyncClient, place: str) -> dict[str, Any]:
    title = place.replace(" ", "_")
    wiki = await _get_json(client, WIKIPEDIA_SUMMARY.format(title=title))
    if not wiki:
        return {"available": False, "reason": f"No Wikipedia summary found for '{place}'"}
    return {
        "available": True,
        "title": wiki.get("title"),
        "extract": wiki.get("extract"),
        "wikipedia_url": (wiki.get("content_urls") or {}).get("desktop", {}).get("page"),
        "thumbnail": (wiki.get("thumbnail") or {}).get("source"),
    }


async def _practical(client: httpx.AsyncClient, place: str) -> dict[str, Any]:
    title = place.replace(" ", "_")
    voyage = await _get_json(client, WIKIVOYAGE_SUMMARY.format(title=title))
    result: dict[str, Any] = {"available": bool(voyage)}
    if voyage:
        result["extract"] = voyage.get("extract")
        result["wikivoyage_url"] = (voyage.get("content_urls") or {}).get("desktop", {}).get("page")
    else:
        result["reason"] = f"No Wikivoyage page found for '{place}'"

    geo = await _geocode(client, place)
    country_name = geo.get("country") if geo else None
    if country_name:
        countries = await _get_json(client, REST_COUNTRIES.format(name=country_name))
        if countries:
            c = countries[0]
            result["country"] = {
                "name": (c.get("name") or {}).get("common"),
                "currencies": list((c.get("currencies") or {}).keys()),
                "languages": list((c.get("languages") or {}).values()),
                "calling_code": (
                    (c.get("idd") or {}).get("root", "")
                    + "".join((c.get("idd") or {}).get("suffixes", [""])[:1])
                ),
                "capital": (c.get("capital") or [None])[0],
                "region": c.get("region"),
                "timezones": c.get("timezones"),
            }
    return result


async def _weather(client: httpx.AsyncClient, place: str, days: int) -> dict[str, Any]:
    geo = await _geocode(client, place)
    if not geo:
        return {"available": False, "reason": f"Could not geocode '{place}'"}

    forecast = await _get_json(
        client,
        OPEN_METEO_FORECAST,
        latitude=geo["latitude"],
        longitude=geo["longitude"],
        daily="temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode",
        forecast_days=max(1, min(days, 16)),
        timezone="auto",
    )
    if not forecast:
        return {"available": False, "reason": "Open-Meteo forecast request failed"}

    daily = forecast.get("daily") or {}
    dates = daily.get("time", [])
    days_out = []
    for i, date in enumerate(dates):
        days_out.append(
            {
                "date": date,
                "temp_max_c": daily.get("temperature_2m_max", [None] * len(dates))[i],
                "temp_min_c": daily.get("temperature_2m_min", [None] * len(dates))[i],
                "precip_probability_pct": daily.get(
                    "precipitation_probability_max", [None] * len(dates)
                )[i],
            }
        )
    return {
        "available": True,
        "resolved_place": geo.get("name"),
        "country": geo.get("country"),
        "latitude": geo["latitude"],
        "longitude": geo["longitude"],
        "days": days_out,
    }


async def destination(
    operation: DestinationOperation,
    place: str,
    forecast_days: int = 7,
) -> dict[str, Any]:
    """Look up free-source travel info for a place.

    operation:
        overview  - Wikipedia summary (what/where it is)
        weather   - Open-Meteo forecast for the next `forecast_days` days
        practical - Wikivoyage extract + country facts (currency, languages, calling code)
        full      - all three combined

    All sources are free and require no API key. Returns available=False
    with a reason string per section if a source has no data, rather than
    guessing.

    ## Return Format
    {"place": str, "overview"|"weather"|"practical": {"available": bool, ...}}

    ## Examples
    destination(operation="full", place="Kyoto")
    destination(operation="weather", place="Vienna", forecast_days=3)
    destination(operation="overview", place="Machu Picchu")
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        if operation == "overview":
            return {"place": place, "overview": await _overview(client, place)}
        if operation == "weather":
            return {"place": place, "weather": await _weather(client, place, forecast_days)}
        if operation == "practical":
            return {"place": place, "practical": await _practical(client, place)}
        if operation == "full":
            overview = await _overview(client, place)
            weather = await _weather(client, place, forecast_days)
            practical = await _practical(client, place)
            return {
                "place": place,
                "overview": overview,
                "weather": weather,
                "practical": practical,
            }
    raise ValueError(f"Unknown operation: {operation}")
