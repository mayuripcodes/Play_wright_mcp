#!/usr/bin/env python3
"""
Universal Playwright MCP Server implementation.
"""

import asyncio
import base64
import sys
import logging
from typing import Dict, Optional

from pydantic import AnyUrl
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


# =========================
# MCP SAFE IMPORT
# =========================
try:
    from modelcontextprotocol.server.models import InitializationOptions
    import modelcontextprotocol.types as types
    from modelcontextprotocol.server import NotificationOptions, Server
    import modelcontextprotocol.server.stdio
except ImportError as exc:
    raise RuntimeError(
        "\nMCP SDK is required to run this server.\n"
        "Install it with:\n"
        "pip install git+https://github.com/microsoft/mcp-python-sdk.git\n"
    ) from exc


# =========================
# GLOBAL CONFIG
# =========================
CONFIG = {
    "browser_type": "chromium",
    "headless": True,
    "debug": False,
    "browser_args": ["--no-sandbox", "--disable-setuid-sandbox"],
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("playwright-universal-mcp")


# =========================
# PLAYWRIGHT STATE
# =========================
playwright_instance = None
browser: Optional[Browser] = None
context: Optional[BrowserContext] = None
pages: Dict[str, Page] = {}
current_page_id: Optional[str] = None


# =========================
# MCP SERVER
# =========================
server = Server("playwright-universal-mcp")


def configure(browser_type="chromium", headless=True, debug=False, browser_args=None):
    CONFIG["browser_type"] = browser_type
    CONFIG["headless"] = headless
    CONFIG["debug"] = debug
    if browser_args:
        CONFIG["browser_args"] = ["--no-sandbox", "--disable-setuid-sandbox"] + browser_args
    logger.setLevel(logging.DEBUG if debug else logging.INFO)


# =========================
# RESOURCES
# =========================
@server.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri=AnyUrl(f"screenshot://{pid}"),
            name=f"Screenshot: {page.url}",
            description=f"Screenshot of {page.url}",
            mimeType="image/png",
        )
        for pid, page in pages.items()
    ]


@server.read_resource()
async def read_resource(uri: AnyUrl) -> bytes:
    page_id = uri.host
    if page_id not in pages:
        raise ValueError(f"Page not found: {page_id}")
    return await pages[page_id].screenshot()


@server.list_resource_templates()
async def list_resource_templates() -> list[types.ResourceTemplate]:
    return []


# =========================
# BROWSER CONTROL
# =========================
async def ensure_browser():
    global playwright_instance, browser, context, current_page_id

    if playwright_instance:
        return

    playwright_instance = await async_playwright().start()
    launcher = getattr(playwright_instance, CONFIG["browser_type"])

    browser = await launcher.launch(
        headless=CONFIG["headless"],
        args=CONFIG["browser_args"],
    )

    context = await browser.new_context()
    page = await context.new_page()
    pages["default"] = page
    current_page_id = "default"


def get_page(page_id: Optional[str]) -> Page:
    pid = page_id or current_page_id
    if pid not in pages:
        raise ValueError(f"Page not found: {pid}")
    return pages[pid]


# =========================
# TOOLS
# =========================
@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="navigate",
            description="Navigate to URL",
            inputSchema={
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict | None):
    await ensure_browser()
    arguments = arguments or {}

    if name == "navigate":
        page = get_page(arguments.get("page_id"))
        await page.goto(arguments["url"])
        return [types.TextContent(type="text", text=f"Navigated to {arguments['url']}")]

    raise ValueError(f"Unknown tool: {name}")


# =========================
# CLEANUP
# =========================
async def cleanup():
    if browser:
        await browser.close()
    if playwright_instance:
        await playwright_instance.stop()


# =========================
# MAIN
# =========================
async def main():
    logger.info("Starting Playwright Universal MCP Server")
    try:
        async with modelcontextprotocol.server.stdio.stdio_server() as (r, w):
            await server.run(
                r,
                w,
                InitializationOptions(
                    server_name="playwright-universal-mcp",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    finally:
        await cleanup()


if __name__ == "__main__":
    asyncio.run(main())
