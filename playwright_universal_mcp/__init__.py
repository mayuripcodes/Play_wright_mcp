"""
Playwright Universal MCP Server.

A Model Context Protocol (MCP) server for browser automation that works in
containerized environments with limited privileges.

Supports multiple browsers: Chromium, Microsoft Edge, Firefox, Webkit.
"""

__version__ = "0.1.0"

from . import server
from . import cli