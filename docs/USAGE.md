# Usage Guide

This guide provides instructions and examples for using the Playwright Universal MCP server with Claude and other AI assistants.

## Basic Usage

Once installed and configured, the Playwright Universal MCP server enables browser automation through the Model Context Protocol (MCP).

### Starting the Server Manually

You can start the server manually:

```bash
# Basic usage with default options
playwright-universal-mcp

# Specify a browser
playwright-universal-mcp --browser msedge

# Run in headful mode (visible browser window)
playwright-universal-mcp --browser chrome --headful

# Enable debug logging
playwright-universal-mcp --debug
```

### Using with Claude Desktop

1. Configure Claude Desktop as described in the [Configuration Guide](CONFIGURATION.md)
2. Start Claude Desktop
3. Claude will automatically connect to the MCP server
4. Ask Claude to perform browser tasks:

```
Could you browse to microsoft.com and tell me what's on the homepage?
```

```
Please search for "playwright automation" on Bing and summarize the top results.
```

```
Navigate to github.com and take a screenshot of the page.
```

## Available Browser Tools

The MCP server provides the following tools that Claude can use:

### Navigation

```
Please navigate to example.com
```

Claude will use the `navigate` tool to go to the specified URL.

### Clicking Elements

```
Click on the 'Sign In' button
```

Claude will use the `click` tool to interact with elements.

### Typing Text

```
Type "hello world" into the search box
```

Claude will use the `type` tool to enter text.

### Getting Page Content

```
What is the main content of this page?
```

Claude will use the `get_page_content` or `get_text` tools to retrieve content.

### Taking Screenshots

```
Take a screenshot of the current page
```

Claude will use the `take_screenshot` tool to capture the visual state.

### Managing Multiple Pages

```
Open a new page and call it "research"
```

Claude will use the `new_page` tool to create additional browser tabs.

```
Switch to the research page
```

Claude will use the `switch_page` tool to change the active tab.

## Usage Examples

### Example 1: Basic Web Search

```
Using the browser, search for "climate change solutions" on Google and summarize the top 3 results.
```

Claude will:
1. Navigate to Google
2. Type the search query
3. Click search or press Enter
4. Extract and summarize the search results

### Example 2: Comparing Products

```
Compare the pricing and features of Microsoft 365 and Google Workspace. Browse to both their pricing pages and create a comparison table.
```

Claude will:
1. Navigate to Microsoft 365 pricing page
2. Extract pricing information
3. Open a new page
4. Navigate to Google Workspace pricing
5. Extract information
6. Create a comparison table

### Example 3: Filling Forms

```
Go to example.com/contact and fill out the contact form with the following information:
Name: John Doe
Email: john@example.com
Message: Hello, I'm interested in your services
```

Claude will:
1. Navigate to the form
2. Fill in each field
3. Submit the form (if requested)

### Example 4: Technical Documentation Research

```
Find the Playwright documentation about browser contexts and explain how they work.
```

Claude will:
1. Navigate to Playwright documentation
2. Find the relevant section
3. Extract and explain the content

## Usage in Containerized Environments

The Playwright Universal MCP server is designed to work in containerized environments with limited privileges:

```bash
# Run in a Docker container
docker run -it --rm playwright-universal-mcp-image
```

When using in containers, remember:
- Always use headless mode
- Ensure the container has necessary permissions
- Set appropriate browser arguments for container environments

## Advanced Usage

### Handling Authentication

Claude can help with authentication flows:

```
Log into example.com using:
Username: testuser
Password: [User will need to provide this]
```

### Extracting Structured Data

Claude can extract and structure data from web pages:

```
Go to example.com/products and create a CSV list of all products with their names, prices, and ratings.
```

### Multi-step Workflows

Claude can perform complex workflows:

```
Please help me book a flight on expedia.com:
1. Search for flights from New York to London
2. Departure date: next Monday
3. Return date: the following Friday
4. Find the cheapest direct flight
```

## Best Practices

1. **Be Specific**: Provide clear instructions about what URLs to visit and what actions to take
2. **Handle Timeouts**: For slow-loading pages, be patient or ask Claude to wait for specific elements
3. **Page Management**: For complex tasks, use multiple pages to keep different contexts separate
4. **Error Handling**: If Claude reports an error (like element not found), try alternative approaches
5. **Security**: Never ask Claude to visit untrusted websites or perform actions that could be harmful

## Troubleshooting

### Common Issues

1. **Element Not Found**: The page structure might have changed or the element might be in an iframe. Try using different selectors or waiting for the element.

2. **Navigation Timeout**: Some sites might take longer to load. You can ask Claude to try again or provide a more direct URL.

3. **Incomplete Content**: For dynamically loaded content, ask Claude to scroll down or wait for content to load.

4. **Blocked Access**: Some sites block automated browsers. You might need to use a different approach or website.

## Next Steps

- Check the [Development Guide](DEVELOPMENT.md) if you want to extend the MCP server
- See [Contribution Guidelines](CONTRIBUTING.md) if you want to contribute to the project