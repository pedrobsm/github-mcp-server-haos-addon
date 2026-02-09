# GitHub MCP Server Add-on - Quick Start

This is a quick reference guide to get the GitHub MCP Server add-on up and running in minutes.

## ⚡ Quick Installation

### 1. Get GitHub Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Select scopes: `repo`, `read:org`, `project`
4. Copy the token (starts with `ghp_`)

### 2. Install Add-on

**Option A: From repository (after publishing)**
```
Add repository: https://github.com/pedrobsm/github-mcp-server-haos-addon
Install: GitHub MCP Server
```

**Option B: Local installation (development)**
```bash
# Copy to Home Assistant
scp -r /addons/github-mcp-server root@homeassistant.local:/addons/

# In Home Assistant: Supervisor → Add-on Store → ⋮ → Check for updates
# Install "GitHub MCP Server" from local add-ons
```

### 3. Configure

Minimum configuration:
```yaml
github_token: ghp_your_token_here
```

Full configuration:
```yaml
github_token: ghp_your_token_here
toolsets: repos,issues,pull_requests,projects,search,code
port: 8080
log_level: info
```

### 4. Start Add-on

1. Click **Start**
2. Wait ~30 seconds
3. Check logs for "MCP Server ready"

### 5. Connect from VSCode

**On local machine with SSH tunnel:**
```bash
# Terminal 1: SSH tunnel
ssh -L 8080:localhost:8080 root@homeassistant.local

# VSCode: Add to .vscode/settings.json
{
  "mcp": {
    "servers": {
      "github": {
        "type": "http",
        "url": "http://localhost:8080/mcp"
      }
    }
  }
}
```

**Test:**
```bash
curl http://localhost:8080/health
```

## 🎯 Quick Tests

### 1. Health Check
```bash
curl http://localhost:8080/health
# Expected: {"status":"healthy","docker_accessible":true,"version":"1.0.0"}
```

### 2. List Tools
```bash
curl -X POST http://localhost:8080/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
```

### 3. API Documentation
Open in browser: http://localhost:8080/docs

### 4. VSCode Copilot
After VSCode configuration, try:
- "Show me my GitHub repositories"
- "List open issues in my repos"

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Add-on won't start | Check logs: Supervisor → Logs. Verify token format (ghp_*) |
| Connection refused | Verify add-on is running: Supervisor → Info tab |
| SSH tunnel fails | Try: `ssh -v -L 8080:localhost:8080 root@homeassistant.local` |
| Token errors | Check token scopes at https://github.com/settings/tokens |

## 📚 Full Documentation

- **Complete guide**: [README.md](README.md)
- **VSCode setup**: [docs/vscode-setup.md](docs/vscode-setup.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

## 🆘 Get Help

- **Issues**: https://github.com/pedrobsm/github-mcp-server-haos-addon/issues
- **Discussions**: https://github.com/pedrobsm/github-mcp-server-haos-addon/discussions

---

**You're ready! Happy coding! 🚀**
