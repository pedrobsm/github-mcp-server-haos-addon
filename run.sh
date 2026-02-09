#!/usr/bin/with-contenv bashio

# Get configuration from add-on options
GITHUB_TOKEN=$(bashio::config 'github_token')
TOOLSETS=$(bashio::config 'toolsets')
PORT=$(bashio::config 'port')
LOG_LEVEL=$(bashio::config 'log_level')

# Validate token
if [ -z "$GITHUB_TOKEN" ] || [ "$GITHUB_TOKEN" = "null" ]; then
    bashio::log.error "GitHub token is required! Configure in add-on settings."
    exit 1
fi

# Export environment variables
export GITHUB_PERSONAL_ACCESS_TOKEN="${GITHUB_TOKEN}"
export GITHUB_TOOLSETS="${TOOLSETS}"
export MCP_PORT="${PORT}"
export LOG_LEVEL="${LOG_LEVEL}"

bashio::log.info "Starting GitHub MCP Server on port ${PORT}..."
bashio::log.info "Toolsets: ${TOOLSETS}"
bashio::log.info "Log level: ${LOG_LEVEL}"

# Pull GitHub MCP Server Docker image if needed
bashio::log.info "Checking GitHub MCP Server Docker image..."
if ! docker image inspect ghcr.io/github/github-mcp-server:0.30.3 >/dev/null 2>&1; then
    bashio::log.info "Pulling Docker image..."
    docker pull ghcr.io/github/github-mcp-server:0.30.3 || {
        bashio::log.error "Failed to pull Docker image"
        exit 1
    }
fi

# Start FastAPI application
exec python3 -u -m uvicorn mcp_bridge.app:app --host 0.0.0.0 --port "${PORT}" --log-level "${LOG_LEVEL}"
