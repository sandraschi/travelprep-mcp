"""Shared subprocess-stdio provider base.

Fleet pattern: wrap an existing, actively-maintained Node/TS MCP server
as a child process over stdio rather than reimplementing its scraping
logic in Python. Same shape as opencode-cli-mcp / goose-mcp wrapping
external CLI agents.

Requires Node.js + npx on PATH. Each concrete provider owns its own
`npx` package name and args; this base just handles session lifecycle.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class StdioProvider:
    """Launches `npx <package> <args>` and speaks MCP over its stdio."""

    def __init__(self, package: str, extra_args: list[str] | None = None) -> None:
        self.package = package
        self.extra_args = extra_args or []

    @asynccontextmanager
    async def session(self) -> AsyncIterator[ClientSession]:
        params = StdioServerParameters(
            command="npx",
            args=["-y", self.package, *self.extra_args],
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        async with self.session() as session:
            result = await session.call_tool(tool_name, arguments=arguments)
            return result

    async def list_tools(self) -> Any:
        async with self.session() as session:
            return await session.list_tools()
