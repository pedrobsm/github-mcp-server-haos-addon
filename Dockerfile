ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install system dependencies
RUN apk add --no-cache \
    bash \
    curl \
    jq \
    tar

# Download and install GitHub MCP Server binary
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then GITHUB_ARCH="linux_x86_64"; \
    elif [ "$ARCH" = "aarch64" ]; then GITHUB_ARCH="linux_arm64"; \
    elif [ "$ARCH" = "armv7l" ]; then GITHUB_ARCH="linux_armv7"; \
    else echo "Unsupported architecture: $ARCH"; exit 1; fi && \
    curl -L "https://github.com/github/github-mcp-server/releases/download/v0.30.3/github-mcp-server_0.30.3_${GITHUB_ARCH}.tar.gz" -o /tmp/mcp.tar.gz && \
    tar -xzf /tmp/mcp.tar.gz -C /usr/local/bin/ github-mcp-server && \
    rm /tmp/mcp.tar.gz && \
    chmod +x /usr/local/bin/github-mcp-server

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application
COPY mcp_bridge/ ./mcp_bridge/
COPY run.sh .

# Make run script executable
RUN chmod +x run.sh

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run
CMD ["./run.sh"]
