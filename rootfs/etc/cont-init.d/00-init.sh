#!/usr/bin/with-contenv bashio
# ==============================================================================
# Initialize GitHub MCP Server add-on
# ==============================================================================

bashio::log.info "Initializing GitHub MCP Server..."

# Check configuration file
CONFIG_PATH="/data/options.json"
if [ ! -f "$CONFIG_PATH" ]; then
    bashio::log.error "Configuration file not found: $CONFIG_PATH"
    exit 1
fi

# Validate GitHub token
GITHUB_TOKEN=$(bashio::config 'github_token')
if [ -z "$GITHUB_TOKEN" ]; then
    bashio::log.error "GitHub token is required! Please configure it in the add-on settings."
    exit 1
fi

if [[ ! "$GITHUB_TOKEN" =~ ^ghp_ ]] && [[ ! "$GITHUB_TOKEN" =~ ^github_pat_ ]]; then
    bashio::log.warning "GitHub token format looks incorrect. Expected format: ghp_* or github_pat_*"
fi

bashio::log.info "Configuration validated successfully"
bashio::log.info "Toolsets: $(bashio::config 'toolsets')"
bashio::log.info "Port: $(bashio::config 'port')"
bashio::log.info "Log Level: $(bashio::config 'log_level')"

# Pull GitHub MCP Server Docker image if not present
bashio::log.info "Checking for GitHub MCP Server Docker image..."
if ! docker image inspect ghcr.io/github/github-mcp-server:0.30.3 >/dev/null 2>&1; then
    bashio::log.info "Pulling GitHub MCP Server Docker image..."
    docker pull ghcr.io/github/github-mcp-server:0.30.3 || {
        bashio::log.error "Failed to pull GitHub MCP Server Docker image"
        exit 1
    }
fi

bashio::log.info "Initialization complete"
