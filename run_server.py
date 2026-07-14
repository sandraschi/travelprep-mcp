"""PyInstaller entry point for travelprep-mcp-backend.exe.

Dual transport: detects MCP_PORT or PORT env var to switch from stdio
to HTTP mode. Sets MCP_TRANSPORT=http so the server's existing main()
picks up the correct transport.
"""
import os
import sys

sys.path.insert(0, "src")

port = os.environ.get("MCP_PORT") or os.environ.get("PORT")
if port:
    host = os.environ.get("MCP_HOST", "127.0.0.1")
    os.environ["MCP_TRANSPORT"] = "http"

from travelprep_mcp.server import main

main()
