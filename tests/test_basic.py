"""
Basic tests for the playwright_universal_mcp package.
"""

import pytest
from playwright_universal_mcp import __version__


def test_version():
    """Test that version is a string."""
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_imports():
    """Test that modules can be imported."""
    from playwright_universal_mcp import cli, server
    assert cli is not None
    assert server is not None