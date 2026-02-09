#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: GitHub MCP Server
# Runs the GitHub MCP Server with FastAPI HTTP wrapper
# ==============================================================================

# Read configuration from add-on
export GITHUB_PERSONAL_ACCESS_TOKEN=$(bashio::config 'github_token')
export GITHUB_TOOLSETS=$(bashio::config 'toolsets')
export MCP_PORT=$(bashio::config 'port')
export LOG_LEVEL=$(bashio::config 'log_level')

bashio::log.info "Starting FastAPI HTTP wrapper on port ${MCP_PORT}..."

# Start FastAPI wrapper
cd /app/mcp_bridge
exec python3 -u app.py
