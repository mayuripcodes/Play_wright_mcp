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
        description="Universal Playwright MCP server"
    )

    parser.add_argument(
        "--browser",
        "-b",
        choices=["chromium", "firefox", "webkit", "msedge", "chrome"],
        default="chromium",
        help="Browser to use",
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode",
    )

    parser.add_argument(
        "--headful",
        action="store_true",
        help="Run browser in headful mode",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    parser.add_argument(
        "--browser-arg",
        action="append",
        default=[],
        help="Additional browser arguments",
    )

    args = parser.parse_args()

    if args.headful:
        args.headless = False

    server.configure(
        browser_type=args.browser,
        headless=args.headless,
        debug=args.debug,
        browser_args=args.browser_arg,
    )

    if args.debug:
        mode = "headless" if args.headless else "headful"
        print(
            f"Starting server with {args.browser} in {mode} mode",
            file=sys.stderr,
        )

    asyncio.run(server.main())


if __name__ == "__main__":
    main()
