# Playwright Universal MCP

A universal [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for browser automation that works reliably in containerized environments with limited privileges. It provides browser control capabilities to AI assistants like Claude, GPT-4, etc.

## Features

- 🌐 **Multi-browser support**: Choose between Chromium, Chrome, Microsoft Edge, Firefox, or WebKit
- 🐳 **Container-friendly**: Works in environments with limited privileges (like Docker containers)
- 👁️ **Headless/Headful modes**: Run in headless mode for server environments or headful mode for debugging
- 🛠️ **Extensive browser control**: Navigate, click, type, take screenshots, and more
- 📄 **Multiple page support**: Create and manage multiple browser pages/tabs

## Installation

### Option 1: Install with pipx (recommended)

```bash
# Install the MCP Python SDK
pip install git+https://github.com/microsoft/mcp-python-sdk.git

# Install the MCP server globally
pipx install playwright-universal-mcp

# Install the required browsers
playwright install chromium
# Optional: install other browsers
playwright install firefox webkit msedge chrome
```

### Option 2: Install in a Python virtual environment

```bash
# Create and activate a virtual environment
python -m venv playwright-mcp-venv
source playwright-mcp-venv/bin/activate

# Install the MCP Python SDK
pip install git+https://github.com/microsoft/mcp-python-sdk.git

# Install the package
pip install playwright-universal-mcp

# Install browsers
playwright install chromium
```

### Option 3: Install from source

```bash
# Clone the repository
git clone https://github.com/xkiranj/playwright-universal-mcp.git
cd playwright-universal-mcp

# Install the MCP Python SDK
pip install git+https://github.com/microsoft/mcp-python-sdk.git

# Install the package
pip install -e .

# Install browsers
playwright install chromium
```

## Usage

### Command Line Options

```
playwright-universal-mcp --help
```

```
usage: playwright-universal-mcp [-h] [--browser {chromium,firefox,webkit,msedge,chrome}] [--headless] [--headful] [--debug] [--browser-arg BROWSER_ARG]

Universal Playwright MCP server with multi-browser support

options:
  -h, --help            show this help message and exit
  --browser {chromium,firefox,webkit,msedge,chrome}, -b {chromium,firefox,webkit,msedge,chrome}
                        Browser to use (default: chromium)
  --headless            Run browser in headless mode (default: true)
  --headful             Run browser in headful mode (with GUI)
  --debug               Enable debug logging
  --browser-arg BROWSER_ARG
                        Additional browser arguments (can be specified multiple times)
```

### Basic Examples

```bash
# Start with default options (Chromium in headless mode)
playwright-universal-mcp

# Use Microsoft Edge
playwright-universal-mcp --browser msedge

# Use Firefox in headful mode (visible browser window)
playwright-universal-mcp --browser firefox --headful

# Enable debug logging
playwright-universal-mcp --debug

# Pass additional arguments to the browser
playwright-universal-mcp --browser-arg="--disable-gpu" --browser-arg="--window-size=1920,1080"
```

## MCP Configuration

To use this MCP server with Claude Desktop or other MCP-enabled applications, add the following configuration:

### Claude Desktop Configuration

Add the following to your `~/.config/Claude/claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "browser": {
      "command": "playwright-universal-mcp",
      "args": ["--browser", "msedge", "--headless"]
    }
  }
}
```

### Running as a PM2 Service

To run the MCP server as a persistent service with PM2:

1. Create a PM2 configuration file:

```bash
cat > ~/playwright-universal-mcp.config.js << 'EOF'
module.exports = {
  apps: [{
    name: "playwright-universal-mcp",
    script: "playwright-universal-mcp",
    args: "--browser msedge --headless",
    watch: false,
    autorestart: true,
    restart_delay: 3000
  }]
}
EOF
```

2. Start the service:

```bash
pm2 start ~/playwright-universal-mcp.config.js
```

3. Save the PM2 process list:

```bash
pm2 save
```

## Containerized Usage

This MCP server works well in containerized environments. Here's a simple Dockerfile example:

```dockerfile
FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install the package
RUN pip install playwright-universal-mcp

# Install browsers (install the ones you need)
RUN playwright install chromium

# Run the MCP server
ENTRYPOINT ["playwright-universal-mcp", "--headless"]
```

## Available Browser Tools

The MCP server provides the following tools:

- `navigate`: Navigate to a URL
- `click`: Click on an element by selector or text
- `type`: Type text into an input element
- `get_text`: Get text content from an element
- `get_page_content`: Get the current page HTML content
- `take_screenshot`: Take a screenshot of the current page
- `new_page`: Create a new browser page
- `switch_page`: Switch to a different browser page
- `get_pages`: List all available browser pages
- `wait_for_selector`: Wait for an element to be visible on the page
- `get_browser_info`: Get information about the current browser session

## License

MIT License

## Acknowledgments

This project builds upon:
- [Playwright](https://playwright.dev/) for browser automation
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) for the connection standard
- [MCP Python SDK](https://github.com/microsoft/mcp-python-sdk) for the MCP implementation