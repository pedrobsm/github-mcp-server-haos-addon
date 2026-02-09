ARG BUILD_FROM
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    docker-cli \
    jq \
    curl \
    bash

# Install bashio
RUN curl -J -L -o /tmp/bashio.tar.gz \
    "https://github.com/hassio-addons/bashio/archive/v0.16.2.tar.gz" \
    && mkdir /tmp/bashio \
    && tar zxvf /tmp/bashio.tar.gz --strip 1 -C /tmp/bashio \
    && mv /tmp/bashio/lib /usr/lib/bashio \
    && ln -s /usr/lib/bashio/bashio /usr/bin/bashio \
    && rm -rf /tmp/bashio /tmp/bashio.tar.gz

# Install Python packages
COPY mcp_bridge/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

# Copy rootfs (s6-overlay services)
COPY rootfs /

# Copy application files
COPY mcp_bridge/ /app/mcp_bridge/
COPY run.sh /app/

# Make scripts executable
RUN chmod a+x /app/run.sh && \
    chmod a+x /etc/services.d/github-mcp-server/run && \
    chmod a+x /etc/services.d/github-mcp-server/finish && \
    chmod a+x /etc/cont-init.d/00-init.sh

# Set working directory
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080
