# Configuration Guide

This guide covers how to configure the Playwright Universal MCP server for different use cases.

## Command Line Options

The Playwright Universal MCP server accepts several command line options to customize its behavior:

```
usage: playwright-universal-mcp [-h] [--browser {chromium,firefox,webkit,msedge,chrome}] 
                               [--headless] [--headful] [--debug] 
                               [--browser-arg BROWSER_ARG]

Universal Playwright MCP server with multi-browser support

options:
  -h, --help            
    Show this help message and exit
  
  --browser {chromium,firefox,webkit,msedge,chrome}, -b {chromium,firefox,webkit,msedge,chrome}
    Browser to use (default: chromium)
  
  --headless            
    Run browser in headless mode (default: true)
  
  --headful             
    Run browser in headful mode (with GUI)
  
  --debug               
    Enable debug logging
  
  --browser-arg BROWSER_ARG
    Additional browser arguments (can be specified multiple times)
```

## Browser Selection

You can choose between different browsers:

```bash
# Use Microsoft Edge
playwright-universal-mcp --browser msedge

# Use Firefox
playwright-universal-mcp --browser firefox

# Use Chrome
playwright-universal-mcp --browser chrome

# Use WebKit (Safari engine)
playwright-universal-mcp --browser webkit

# Use default Chromium
playwright-universal-mcp --browser chromium
```

## Headless vs Headful Mode

By default, the browser runs in headless mode (no visible window). For debugging or visual monitoring, you can use headful mode:

```bash
# Run in headful mode (shows browser window)
playwright-universal-mcp --headful

# Explicitly specify headless mode
playwright-universal-mcp --headless
```

## Browser Arguments

You can pass additional arguments to the browser:

```bash
# Set window size
playwright-universal-mcp --browser-arg="--window-size=1920,1080"

# Disable GPU acceleration
playwright-universal-mcp --browser-arg="--disable-gpu"

# Multiple arguments
playwright-universal-mcp --browser-arg="--disable-gpu" --browser-arg="--disable-dev-shm-usage"
```

## Debug Logging

Enable debug logging to see more detailed information:

```bash
playwright-universal-mcp --debug
```

## Claude Desktop Configuration

To use the Playwright Universal MCP with Claude Desktop:

1. Create or edit the Claude Desktop configuration file at `~/.config/Claude/claude_desktop_config.json`
2. Add the MCP server configuration:

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

### Multiple Browser Configurations

You can configure multiple browsers in Claude Desktop:

```json
{
  "mcpServers": {
    "browser-chromium": {
      "command": "playwright-universal-mcp",
      "args": ["--browser", "chromium", "--headless"]
    },
    "browser-edge": {
      "command": "playwright-universal-mcp",
      "args": ["--browser", "msedge", "--headless"]
    },
    "browser-firefox": {
      "command": "playwright-universal-mcp",
      "args": ["--browser", "firefox", "--headless"]
    }
  }
}
```

## Running as a PM2 Service

To run the MCP server as a persistent service with PM2:

1. Create a PM2 configuration file:

```javascript
// playwright-universal-mcp.config.js
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
```

2. Start the service:

```bash
pm2 start playwright-universal-mcp.config.js
```

3. View logs:

```bash
pm2 logs playwright-universal-mcp
```

4. Save the PM2 process list to survive system restarts:

```bash
pm2 save
```

5. Configure PM2 to start on system boot:

```bash
pm2 startup
```

## Docker Configuration

To run the MCP server in a Docker container:

```dockerfile
FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install the package
RUN pip install playwright-universal-mcp

# Install browser
RUN playwright install chromium

# Run the MCP server
ENTRYPOINT ["playwright-universal-mcp", "--headless"]
```

Build and run:

```bash
docker build -t playwright-universal-mcp .
docker run -it --rm playwright-universal-mcp
```

## Advanced Configuration

### Customizing Browser Context

For advanced users who want to modify the browser context configuration, you can edit the server.py file if you're installing from source:

```python
# Modify the ensure_browser function to customize the context
context = await browser.new_context(
    viewport={'width': 1920, 'height': 1080},
    user_agent='Custom User Agent String',
    locale='en-US',
    timezone_id='America/Los_Angeles',
    geolocation={'latitude': 37.774929, 'longitude': -122.419416},
    permissions=['geolocation'],
    # ...other options...
)
```

## Environment Variables

You can use environment variables to configure the MCP server:

```bash
# Set browser type
export PLAYWRIGHT_UNIVERSAL_MCP_BROWSER=firefox

# Set headless mode
export PLAYWRIGHT_UNIVERSAL_MCP_HEADLESS=true

# Start the server (will use environment variables)
playwright-universal-mcp
```

## Troubleshooting Configuration Issues

### Invalid Configuration

If Claude Desktop fails to start the MCP server, check:

1. The command path is correct
2. The browser you specified is installed
3. The arguments are valid

### Browser Launch Failures

If the browser fails to launch:

1. Ensure you have the necessary dependencies:
   ```bash
   playwright install-deps
   ```

2. For headful mode in container environments, use a virtual display:
   ```bash
   xvfb-run playwright-universal-mcp --headful
   ```

3. Check browser-specific issues:
   - Microsoft Edge: Ensure it's installed and in the default location
   - Firefox: Some features might require extensions
   - WebKit: Might have additional dependencies on Linux

## Next Steps

After configuring the MCP server, proceed to:

1. [Usage Guide](USAGE.md) for examples of how to use the MCP server with Claude and other applications
2. [Development Guide](DEVELOPMENT.md) for information on extending or modifying the MCP server