#!/usr/bin/env python3

"""
Universal Playwright MCP Server implementation.

Provides browser automation via the Model Context Protocol (MCP),
supporting multiple browsers and containerized environments.
"""

import asyncio
import base64
import sys
import logging
from typing import Dict, List, Optional, Any, Union

from modelcontextprotocol.server.models import InitializationOptions
import modelcontextprotocol.types as types
from modelcontextprotocol.server import NotificationOptions, Server
from pydantic import AnyUrl
import modelcontextprotocol.server.stdio

from playwright.async_api import async_playwright, Browser, Page, BrowserContext

# Global configuration
CONFIG = {
    "browser_type": "chromium",
    "headless": True,
    "debug": False,
    "browser_args": ["--no-sandbox", "--disable-setuid-sandbox"]
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("playwright-universal-mcp")

# Global Playwright state
playwright_instance = None
browser: Optional[Browser] = None
context: Optional[BrowserContext] = None
page: Optional[Page] = None
pages: Dict[str, Page] = {}
current_page_id: Optional[str] = None

# Create the MCP server
server = Server("playwright-universal-mcp")

def configure(browser_type="chromium", headless=True, debug=False, browser_args=None):
    """Configure the server with the specified options."""
    CONFIG["browser_type"] = browser_type
    CONFIG["headless"] = headless
    CONFIG["debug"] = debug
    
    if browser_args:
        CONFIG["browser_args"] = ["--no-sandbox", "--disable-setuid-sandbox"] + browser_args
    
    # Update logging level based on debug flag
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.debug(f"Configured server with: {CONFIG}")

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available browser screenshot resources."""
    resources = []
    
    if pages:
        for page_id, page in pages.items():
            resources.append(
                types.Resource(
                    uri=AnyUrl(f"screenshot://{page_id}"),
                    name=f"Screenshot: {page.url}",
                    description=f"Current screenshot of page at {page.url}",
                    mimeType="image/png",
                )
            )
    
    return resources

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> bytes:
    """Capture and return a screenshot from the requested page."""
    if uri.scheme != "screenshot":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    page_id = uri.host
    if page_id not in pages:
        raise ValueError(f"Page not found: {page_id}")
    
    # Take a screenshot of the page
    screenshot = await pages[page_id].screenshot()
    return screenshot

@server.list_resource_templates()
async def handle_list_resource_templates() -> list[types.ResourceTemplate]:
    """List available resource templates for browser automation."""
    return []

async def ensure_browser():
    """Ensure the browser is launched and ready."""
    global playwright_instance, browser, context, page, current_page_id
    
    if playwright_instance is None:
        playwright_instance = await async_playwright().start()
        
        # Get the browser launcher based on the configured type
        browser_type = CONFIG["browser_type"]
        headless = CONFIG["headless"]
        browser_args = CONFIG["browser_args"]
        
        logger.info(f"Launching {browser_type} browser in {'headless' if headless else 'headful'} mode")
        
        if browser_type == "chromium":
            browser = await playwright_instance.chromium.launch(
                headless=headless,
                args=browser_args
            )
        elif browser_type == "firefox":
            browser = await playwright_instance.firefox.launch(
                headless=headless,
                args=browser_args
            )
        elif browser_type == "webkit":
            browser = await playwright_instance.webkit.launch(
                headless=headless,
                args=browser_args
            )
        elif browser_type == "msedge":
            browser = await playwright_instance.chromium.launch(
                headless=headless,
                channel="msedge",
                args=browser_args
            )
        elif browser_type == "chrome":
            browser = await playwright_instance.chromium.launch(
                headless=headless,
                channel="chrome",
                args=browser_args
            )
        else:
            # Default to chromium if type is not recognized
            logger.warning(f"Unrecognized browser type: {browser_type}. Using chromium.")
            browser = await playwright_instance.chromium.launch(
                headless=headless,
                args=browser_args
            )
        
        # Create context and page
        context = await browser.new_context()
        page = await context.new_page()
        pages["default"] = page
        current_page_id = "default"
        logger.info(f"Browser initialized successfully")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available browser automation tools."""
    return [
        types.Tool(
            name="navigate",
            description="Navigate to a URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "page_id": {"type": "string"},
                },
                "required": ["url"],
            },
        ),
        types.Tool(
            name="click",
            description="Click on an element by selector",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string"},
                    "page_id": {"type": "string"},
                },
                "required": ["selector"],
            },
        ),
        types.Tool(
            name="type",
            description="Type text into an input element",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string"},
                    "text": {"type": "string"},
                    "page_id": {"type": "string"},
                },
                "required": ["selector", "text"],
            },
        ),
        types.Tool(
            name="get_text",
            description="Get text content from an element",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string"},
                    "page_id": {"type": "string"},
                },
                "required": ["selector"],
            },
        ),
        types.Tool(
            name="get_page_content",
            description="Get the current page HTML content",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string"},
                },
            },
        ),
        types.Tool(
            name="take_screenshot",
            description="Take a screenshot of the current page",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string"},
                    "selector": {"type": "string"},
                },
            },
        ),
        types.Tool(
            name="new_page",
            description="Create a new browser page",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string"},
                },
                "required": ["page_id"],
            },
        ),
        types.Tool(
            name="switch_page",
            description="Switch to a different browser page",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string"},
                },
                "required": ["page_id"],
            },
        ),
        types.Tool(
            name="get_pages",
            description="List all available browser pages",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="wait_for_selector",
            description="Wait for an element to be visible on the page",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string"},
                    "page_id": {"type": "string"},
                    "timeout": {"type": "number"},
                },
                "required": ["selector"],
            },
        ),
        types.Tool(
            name="get_browser_info",
            description="Get information about the current browser session",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]

def get_active_page(page_id: Optional[str] = None) -> Page:
    """Get the active page based on page_id or current default."""
    global current_page_id
    
    if page_id is None:
        page_id = current_page_id
    
    if page_id not in pages:
        raise ValueError(f"Page not found: {page_id}")
    
    return pages[page_id]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests for browser automation."""
    global current_page_id
    
    if not arguments:
        arguments = {}
    
    # Ensure browser is initialized
    await ensure_browser()
    
    # Process tool calls based on name
    if name == "navigate":
        url = arguments.get("url")
        if not url:
            raise ValueError("URL is required")
            
        page = get_active_page(arguments.get("page_id"))
        await page.goto(url)
        title = await page.title()
        return [types.TextContent(type="text", text=f"Navigated to {url}\nTitle: {title}")]
    
    elif name == "click":
        selector = arguments.get("selector")
        if not selector:
            raise ValueError("Selector is required")
            
        page = get_active_page(arguments.get("page_id"))
        
        # Try to find the element
        try:
            await page.click(selector)
            return [types.TextContent(type="text", text=f"Clicked element at selector: {selector}")]
        except Exception as e:
            logger.warning(f"Failed to click element at {selector}: {e}")
            
            # Try to find by text as a fallback
            try:
                await page.get_by_text(selector).first.click()
                return [types.TextContent(type="text", text=f"Clicked element with text: {selector}")]
            except Exception as text_err:
                raise ValueError(f"Could not find element with selector or text '{selector}'")
    
    elif name == "type":
        selector = arguments.get("selector")
        text = arguments.get("text")
        if not selector or text is None:
            raise ValueError("Selector and text are required")
            
        page = get_active_page(arguments.get("page_id"))
        await page.fill(selector, text)
        return [types.TextContent(type="text", text=f"Typed '{text}' into {selector}")]
    
    elif name == "get_text":
        selector = arguments.get("selector")
        if not selector:
            raise ValueError("Selector is required")
            
        page = get_active_page(arguments.get("page_id"))
        text = await page.text_content(selector)
        return [types.TextContent(type="text", text=text or "")]
    
    elif name == "get_page_content":
        page = get_active_page(arguments.get("page_id"))
        content = await page.content()
        return [types.TextContent(type="text", text=content)]
    
    elif name == "take_screenshot":
        page = get_active_page(arguments.get("page_id"))
        selector = arguments.get("selector")
        
        if selector:
            screenshot = await page.locator(selector).screenshot()
        else:
            screenshot = await page.screenshot()
        
        # Convert the bytes to base64
        base64_image = base64.b64encode(screenshot).decode('utf-8')
        
        # Return as ImageContent - using the correct structure
        return [types.ImageContent(
            type="image",
            image={
                "mime_type": "image/png",
                "data": base64_image
            }
        )]
    
    elif name == "new_page":
        page_id = arguments.get("page_id")
        if not page_id:
            raise ValueError("Page ID is required")
            
        if page_id in pages:
            raise ValueError(f"Page ID '{page_id}' already exists")
            
        new_page = await context.new_page()
        pages[page_id] = new_page
        current_page_id = page_id
        
        return [types.TextContent(type="text", text=f"Created new page with ID: {page_id}")]
    
    elif name == "switch_page":
        page_id = arguments.get("page_id")
        if not page_id:
            raise ValueError("Page ID is required")
            
        if page_id not in pages:
            raise ValueError(f"Page ID '{page_id}' not found")
            
        current_page_id = page_id
        
        return [types.TextContent(type="text", text=f"Switched to page: {page_id}")]
    
    elif name == "get_pages":
        page_info = []
        for page_id, page in pages.items():
            page_info.append(f"{page_id}: {page.url}")
            
        return [types.TextContent(type="text", text="Available pages:\n" + "\n".join(page_info))]
    
    elif name == "wait_for_selector":
        selector = arguments.get("selector")
        if not selector:
            raise ValueError("Selector is required")
            
        timeout = arguments.get("timeout", 30000)  # Default 30 seconds
        page = get_active_page(arguments.get("page_id"))
        
        try:
            await page.wait_for_selector(selector, timeout=timeout)
            return [types.TextContent(type="text", text=f"Element found: {selector}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Timeout waiting for element: {selector}")]
    
    elif name == "get_browser_info":
        info = {
            "browser_type": CONFIG["browser_type"],
            "headless": CONFIG["headless"],
            "pages": list(pages.keys()),
            "current_page": current_page_id
        }
        return [types.TextContent(type="text", text=f"Browser Info:\n{info}")]
    
    else:
        raise ValueError(f"Unknown tool: {name}")
    
    # Notify clients that resources may have changed
    await server.request_context.session.send_resource_list_changed()

async def cleanup():
    """Clean up Playwright resources."""
    global browser, playwright_instance
    
    if browser:
        await browser.close()
    
    if playwright_instance:
        await playwright_instance.stop()

async def main():
    """Main entry point for the server."""
    logger.info(f"Starting Playwright Universal MCP Server ({CONFIG['browser_type']})")
    try:
        # Run the server using stdin/stdout streams
        async with modelcontextprotocol.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
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
        # Ensure we clean up resources when the server shuts down
        logger.info("Cleaning up browser resources...")
        await cleanup()

if __name__ == "__main__":
    asyncio.run(main())