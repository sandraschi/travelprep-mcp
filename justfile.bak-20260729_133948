# justfile -- travelprep-mcp

set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

default:
    just --list

sync:
    uv sync --extra dev

test:
    uv run pytest tests/test_destination.py -v

test-live:
    uv run pytest tests/ -v -s

lint:
    uv run ruff check src tests

fmt:
    uv run ruff format src tests

run:
    uv run travelprep-mcp

run-http:
    $env:MCP_TRANSPORT = "http"; uv run travelprep-mcp
