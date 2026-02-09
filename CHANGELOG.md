# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-09

### Added
- Initial release of GitHub MCP Server add-on for Home Assistant OS
- FastAPI HTTP wrapper for GitHub MCP Server stdio communication
- Configurable GitHub Personal Access Token via add-on UI
- Configurable toolsets (repos, issues, pull_requests, projects, search, code)
- Configurable HTTP port (default: 8080)
- Health check endpoint for monitoring
- Comprehensive logging with configurable levels
- Support for amd64, aarch64, and armv7 architectures
- VSCode remote development support via SSH tunneling
- Complete documentation for installation and VSCode setup
- Docker-based implementation using official GitHub MCP Server image

### Security
- GitHub token stored as password type (hidden in UI)
- Token validation on startup
- No token exposure in logs (only last 4 characters shown)

[1.0.0]: https://github.com/YOUR_USERNAME/github-mcp-server-haos-addon/releases/tag/v1.0.0
