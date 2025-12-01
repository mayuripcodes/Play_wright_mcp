#!/bin/bash

# Install script for Playwright Universal MCP
#
# This script:
# 1. Installs the Playwright Universal MCP server
# 2. Installs the required browsers
# 3. Configures Claude Desktop (optional)
# 4. Sets up PM2 service (optional)

set -e

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default installation path for the pipx virtual environment
INSTALL_DIR="${HOME}/.local/share/pipx/venvs/playwright-universal-mcp"

# Default browsers to install
BROWSERS=("chromium")

# Default server configuration
HEADLESS=true
BROWSER="chromium"
RUN_AS_SERVICE=false
CONFIGURE_CLAUDE=false

# Function to print usage information
print_usage() {
    echo -e "${BLUE}Usage:${NC} $0 [options]"
    echo
    echo "Options:"
    echo "  --help                    Show this help message"
    echo "  --browser BROWSER         Browser to use (chromium, firefox, webkit, msedge, chrome)"
    echo "  --headful                 Run browser in headful mode (default: headless)"
    echo "  --install-browsers LIST   Comma-separated list of browsers to install (default: chromium)"
    echo "  --pm2                     Configure and run as a PM2 service"
    echo "  --configure-claude        Configure for Claude Desktop"
    echo
    echo "Example:"
    echo "  $0 --browser msedge --install-browsers chromium,msedge --pm2 --configure-claude"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            print_usage
            exit 0
            ;;
        --browser)
            BROWSER="$2"
            shift 2
            ;;
        --headful)
            HEADLESS=false
            shift
            ;;
        --install-browsers)
            IFS=',' read -ra BROWSERS <<< "$2"
            shift 2
            ;;
        --pm2)
            RUN_AS_SERVICE=true
            shift
            ;;
        --configure-claude)
            CONFIGURE_CLAUDE=true
            shift
            ;;
        *)
            echo -e "${RED}Error:${NC} Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Check for pipx
if ! command -v pipx &> /dev/null; then
    echo -e "${YELLOW}pipx not found. Installing...${NC}"
    pip install --user pipx
    python -m pipx ensurepath
    
    # Source the updated PATH
    if [[ -f ~/.bashrc ]]; then
        source ~/.bashrc
    fi
fi

# Check for PM2 if service is requested
if [[ "$RUN_AS_SERVICE" == true ]] && ! command -v pm2 &> /dev/null; then
    echo -e "${YELLOW}PM2 not found. Installing...${NC}"
    npm install -g pm2
fi

# Install the Playwright Universal MCP package
echo -e "${GREEN}Installing Playwright Universal MCP...${NC}"
# Check if we're in the source directory
if [[ -f "$(pwd)/pyproject.toml" ]]; then
    echo -e "${BLUE}Installing from local source...${NC}"
    pipx install "$(pwd)" --force
else
    # Install from GitHub
    echo -e "${BLUE}Installing from GitHub...${NC}"
    pipx install "git+https://github.com/xkiranj/playwright-universal-mcp.git" --force
fi

# Install the selected browsers
echo -e "${GREEN}Installing browsers...${NC}"
for browser in "${BROWSERS[@]}"; do
    echo -e "${BLUE}Installing $browser...${NC}"
    playwright install "$browser"
done

# Configure for Claude Desktop if requested
if [[ "$CONFIGURE_CLAUDE" == true ]]; then
    echo -e "${GREEN}Configuring for Claude Desktop...${NC}"
    CONFIG_DIR="${HOME}/.config/Claude"
    CONFIG_FILE="${CONFIG_DIR}/claude_desktop_config.json"
    
    # Create config directory if it doesn't exist
    mkdir -p "$CONFIG_DIR"
    
    # Check if config file exists
    if [[ -f "$CONFIG_FILE" ]]; then
        # Make a backup of the existing file
        cp "$CONFIG_FILE" "${CONFIG_FILE}.bak"
        echo -e "${BLUE}Created backup of existing configuration at ${CONFIG_FILE}.bak${NC}"
        
        # Check if the file is valid JSON
        if ! jq '.' "$CONFIG_FILE" &> /dev/null; then
            echo -e "${RED}Error: Existing config file is not valid JSON. Please fix it manually.${NC}"
            exit 1
        fi
        
        # Check if mcpServers already exists
        if jq -e '.mcpServers' "$CONFIG_FILE" &> /dev/null; then
            # Update the existing configuration
            HEADFUL_ARG=""
            if [[ "$HEADLESS" == false ]]; then
                HEADFUL_ARG=',"--headful"'
            fi
            
            jq --arg browser "$BROWSER" --arg headful "$HEADFUL_ARG" '.mcpServers.browser = {"command":"playwright-universal-mcp","args":["--browser", $browser $headful]}' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp"
            mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
        else
            # Add mcpServers section
            HEADFUL_ARG=""
            if [[ "$HEADLESS" == false ]]; then
                HEADFUL_ARG=',"--headful"'
            fi
            
            jq --arg browser "$BROWSER" --arg headful "$HEADFUL_ARG" '. + {"mcpServers":{"browser":{"command":"playwright-universal-mcp","args":["--browser", $browser $headful]}}}' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp"
            mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
        fi
    else
        # Create a new config file
        HEADFUL_ARG=""
        if [[ "$HEADLESS" == false ]]; then
            HEADFUL_ARG=',"--headful"'
        fi
        
        echo '{
  "mcpServers": {
    "browser": {
      "command": "playwright-universal-mcp",
      "args": ["--browser", "'"$BROWSER"'"'"$HEADFUL_ARG"']
    }
  }
}' > "$CONFIG_FILE"
    fi
    
    echo -e "${GREEN}Claude Desktop configuration updated. Please restart Claude Desktop.${NC}"
fi

# Configure PM2 service if requested
if [[ "$RUN_AS_SERVICE" == true ]]; then
    echo -e "${GREEN}Setting up PM2 service...${NC}"
    
    # Generate the PM2 configuration file
    HEADFUL_ARG=""
    if [[ "$HEADLESS" == false ]]; then
        HEADFUL_ARG=" --headful"
    fi
    
    echo 'module.exports = {
  apps: [{
    name: "playwright-universal-mcp",
    script: "playwright-universal-mcp",
    args: "--browser '"$BROWSER"''"$HEADFUL_ARG"'",
    watch: false,
    autorestart: true,
    restart_delay: 3000
  }]
}' > "${HOME}/playwright-universal-mcp.config.js"
    
    # Stop any existing service
    pm2 stop playwright-universal-mcp 2>/dev/null || true
    pm2 delete playwright-universal-mcp 2>/dev/null || true
    
    # Start the service
    pm2 start "${HOME}/playwright-universal-mcp.config.js"
    
    # Save the PM2 process list
    pm2 save
    
    echo -e "${GREEN}PM2 service configured and started.${NC}"
    echo -e "${BLUE}Use 'pm2 logs playwright-universal-mcp' to view logs.${NC}"
fi

echo -e "${GREEN}Installation complete!${NC}"
echo
echo -e "${BLUE}To run the MCP server manually:${NC}"
echo "playwright-universal-mcp --browser $BROWSER $([ "$HEADLESS" == false ] && echo "--headful")"
echo
echo -e "${YELLOW}Enjoy using Playwright Universal MCP!${NC}"