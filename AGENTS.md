# travelprep-mcp — Agent Instructions

## Stack
- FastMCP 3.4.x (dual transport stdio + HTTP)
- Python 3.12+, uv package manager

## Build & Run
```powershell
uv sync --extra dev
just run          # stdio mode (default)
just run-http     # HTTP mode on :11099
```

## Ports
- Backend MCP HTTP: 11099
- Frontend (Vite): 11100 (scaffold only, no pages yet)

## Testing
- `just test` — offline destination tests
- `just test-live` — full live test suite (hits real APIs/networks)

## Key Constraints
- No paid API keys required
- All accommodation data comes from subprocess-wrapped npx packages (MIT)
- Booking.com account scraping uses isolated Playwright profile, not live browser
- No booking-execution capability (deliberate — see budget.py)
