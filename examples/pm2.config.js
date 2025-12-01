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