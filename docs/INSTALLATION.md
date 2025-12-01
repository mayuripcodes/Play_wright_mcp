# Installation Guide

This guide covers various ways to install and configure the Playwright Universal MCP server.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- For headful mode: A windowing system (X11, Wayland, etc.)

## Installation Methods

### Method 1: Install with pipx (Recommended)

[pipx](https://pypa.github.io/pipx/) creates isolated environments for Python applications, which helps avoid dependency conflicts.

```bash
# Install pipx if not already installed
pip install --user pipx
python -m pipx ensurepath

# Install the Playwright Universal MCP package
pipx install playwright-universal-mcp

# Install required browsers
# You only need to install the browsers you plan to use
playwright install chromium
# Optional: Install other browsers
playwright install firefox webkit msedge chrome
```

### Method 2: Install in a Python Virtual Environment

```bash
# Create a virtual environment
python -m venv playwright-mcp-venv

# Activate the virtual environment
# On Linux/macOS:
source playwright-mcp-venv/bin/activate
# On Windows:
# playwright-mcp-venv\Scripts\activate

# Install the package
pip install playwright-universal-mcp

# Install required browsers
playwright install chromium
```

### Method 3: Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/playwright-universal-mcp.git
cd playwright-universal-mcp

# Install the package
pip install -e .

# Install required browsers
playwright install chromium
```

### Method 4: Using the Install Script

The project comes with an installation script that automates the setup process:

```bash
# Download and run the install script
curl -sSL https://raw.githubusercontent.com/yourusername/playwright-universal-mcp/main/scripts/install.sh -o install.sh
chmod +x install.sh

# Run with default options (installs chromium in headless mode)
./install.sh

# Or customize the installation
./install.sh --browser msedge --install-browsers chromium,msedge --configure-claude --pm2
```

## Browser Installation

The Playwright Universal MCP relies on the Playwright framework to control browsers. You need to install at least one browser:

```bash
# Install specific browsers
playwright install chromium
playwright install firefox
playwright install webkit
playwright install msedge
playwright install chrome

# Or install all browsers
playwright install
```

## Installation Location

Depending on your installation method, the package will be installed in different locations:

- **pipx installation**: `~/.local/share/pipx/venvs/playwright-universal-mcp/`
- **pip installation**: Within your Python environment's site-packages directory
- **Source installation**: Wherever you cloned the repository

## Troubleshooting

### Browser Launch Issues

If you encounter issues with browsers not launching:

1. **Missing Dependencies**: Install browser dependencies
   ```bash
   # On Ubuntu/Debian
   playwright install-deps
   ```

2. **Headful Mode in Containers**: To run in headful mode inside containers, you need to configure X11 forwarding or use a virtual framebuffer like Xvfb:
   ```bash
   # Using Xvfb
   xvfb-run playwright-universal-mcp --browser chromium --headful
   ```

3. **Browser Not Found**: Ensure the browser is installed
   ```bash
   # Check browser installations
   playwright --version
   ```

### MCP Server Communication Issues

If Claude or other applications can't communicate with the MCP server:

1. **Check Permissions**: Ensure the MCP server has permissions to create and access files
2. **Check Configuration**: Verify the MCP configuration in your application (e.g., Claude Desktop)
3. **Check Logs**: Look for error messages in the terminal or PM2 logs

## Next Steps

After installation, proceed to:

1. [Configuration Guide](CONFIGURATION.md) for details on configuring the MCP server
2. [Usage Guide](USAGE.md) for examples of how to use the MCP server with Claude and other applications