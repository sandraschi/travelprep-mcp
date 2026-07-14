"""Local LLM auto-discovery -- fleet 'Glom On' pattern (WEBAPP_SOTA_STANDARDS.md §VI).

Scans standard local inference ports so the webapp's Chat page can
bind to whatever's running without the user entering a URL by hand.
Read-only probes, short timeouts, never raises -- a probe failure
just means "not detected", not an error surfaced to the user.
"""

from __future__ import annotations

from typing import Any

import httpx

_OLLAMA_URL = "http://localhost:11434"
_LMSTUDIO_URL = "http://localhost:1234"


async def discover() -> dict[str, Any]:
    result: dict[str, Any] = {
        "ollama_detected": False,
        "lmstudio_detected": False,
        "configured_model": None,
    }
    async with httpx.AsyncClient(timeout=2.0) as client:
        try:
            r = await client.get(f"{_OLLAMA_URL}/api/tags")
            if r.status_code == 200:
                result["ollama_detected"] = True
                models = r.json().get("models", [])
                if models:
                    result["configured_model"] = models[0].get("name")
        except httpx.HTTPError:
            pass

        if not result["configured_model"]:
            try:
                r = await client.get(f"{_LMSTUDIO_URL}/v1/models")
                if r.status_code == 200:
                    result["lmstudio_detected"] = True
                    models = r.json().get("data", [])
                    if models:
                        result["configured_model"] = models[0].get("id")
            except httpx.HTTPError:
                pass

    return result
