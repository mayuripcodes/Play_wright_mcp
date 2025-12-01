#!/usr/bin/env python3

"""
Command-line interface for the Playwright Universal MCP server.
"""

import argparse
import asyncio
import sys
from . import server

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Universal Playwright MCP server with multi-browser support"
    )
    
    # Browser selection
    parser.add_argument(
        "--browser", "-b",
        choices=["chromium", "firefox", "webkit", "msedge", "chrome"],
        default="chromium",
        help="Browser to use (default: chromium)"
    )
    
    # Headless mode
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: true)"
    )
    
    parser.add_argument(
        "--headful",
        action="store_true",
        help="Run browser in headful mode (with GUI)"
    )
    
    # Debugging
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    # Browser arguments
    parser.add_argument(
        "--browser-arg",
        action="append",
        default=[],
        help="Additional browser arguments (can be specified multiple times)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Override headless if headful is specified
    if args.headful:
        args.headless = False
    
    # Configure the server
    server.configure(
        browser_type=args.browser,
        headless=args.headless,
        debug=args.debug,
        browser_args=args.browser_arg
    )
    
    # Print startup message
    if args.debug:
        browser_mode = "headless" if args.headless else "headful"
        print(f"Starting Playwright Universal MCP with {args.browser} in {browser_mode} mode",
              file=sys.stderr)
    
    # Run the server
    asyncio.run(server.main())

if __name__ == "__main__":
    main()