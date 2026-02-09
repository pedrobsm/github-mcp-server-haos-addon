# GitHub MCP Server Add-on for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)
[![Home Assistant][ha-shield]][ha-url]

![GitHub MCP Server Logo](https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png)

A Home Assistant add-on that runs the **GitHub Model Context Protocol (MCP) Server**, enabling seamless integration with VSCode for remote development, vibecoding, and AI-assisted GitHub workflows directly from your Home Assistant OS installation.

## 🚀 Features

- **Full GitHub MCP Server** - Access all GitHub APIs via MCP protocol
- **HTTP REST API** - Convert MCP stdio to HTTP for remote access
- **VSCode Integration** - Perfect for remote development via SSH
- **Vibecoding Support** - AI-assisted development with GitHub Copilot
- **Secure Configuration** - GitHub token managed via Home Assistant UI
- **Configurable Toolsets** - Enable only the GitHub features you need
- **Multi-Architecture** - Supports amd64, aarch64, and armv7
- **Health Monitoring** - Built-in health checks and logging

## 📋 Prerequisites

- Home Assistant OS or Supervised installation
- SSH access to your Home Assistant instance
- GitHub Personal Access Token ([Create one here](https://github.com/settings/tokens))
- VSCode with SSH Remote extension (for remote development)

## 🔧 Installation

### 1. Add Repository

Add this repository to your Home Assistant add-on store:

1. Navigate to **Supervisor** → **Add-on Store** → **⋮** (three dots menu)
2. Select **Repositories**
3. Add the repository URL:
   ```
   https://github.com/pedrobsm/github-mcp-server-haos-addon
   ```

### 2. Install Add-on

1. Find **GitHub MCP Server** in the add-on store
2. Click **Install**
3. Wait for installation to complete

### 3. Configure Add-on

Go to the **Configuration** tab and set:

```yaml
github_token: ghp_your_token_here
toolsets: repos,issues,pull_requests,projects
port: 8080
log_level: info
```

**Configuration Options:**

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `github_token` | GitHub Personal Access Token | - | ✅ Yes |
| `toolsets` | Comma-separated list of enabled toolsets | `repos,issues,pull_requests,projects` | No |
| `port` | HTTP API port | `8080` | No |
| `log_level` | Logging level (debug/info/warning/error) | `info` | No |

**Available Toolsets:**
- `repos` - Repository management
- `issues` - Issue tracking
- `pull_requests` - Pull request operations
- `projects` - GitHub Projects
- `search` - Code and repository search
- `code` - Code navigation

### 4. Start Add-on

1. Go to the **Info** tab
2. Enable **Start on boot** (optional)
3. Click **Start**
4. Check the **Log** tab for successful startup

## 🔌 VSCode Setup

### Method 1: SSH Port Forwarding (Recommended)

When developing remotely via SSH on your Home Assistant OS:

#### Step 1: Create SSH Tunnel

```bash
# From your local machine
ssh -L 8080:localhost:8080 root@homeassistant.local
```

This forwards port 8080 from Home Assistant to your local machine.

#### Step 2: Configure VSCode MCP Client

Create or edit `.vscode/settings.json` in your workspace:

```json
{
  "mcp": {
    "servers": {
      "github": {
        "type": "http",
        "url": "http://localhost:8080/mcp",
        "description": "GitHub MCP Server via Home Assistant"
      }
    }
  }
}
```

#### Step 3: Test Connection

1. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Search for "MCP: Test Connection"
3. Select "github" server
4. You should see a success message

### Method 2: Direct Access

If developing directly on Home Assistant OS via SSH:

```json
{
  "mcp": {
    "servers": {
      "github": {
        "type": "http",
        "url": "http://localhost:8080/mcp",
        "description": "GitHub MCP Server"
      }
    }
  }
}
```

## 📚 Usage Examples

### Vibecoding with GitHub Copilot

Once configured, GitHub Copilot in VSCode can access your GitHub data through MCP:

- **List your repositories**: "Show me all my GitHub repos"
- **Check issues**: "What open issues do I have in project X?"
- **Pull request status**: "Show me recent PRs waiting for review"
- **Create issues**: "Create a bug issue for this error"

### API Endpoints

The add-on exposes the following HTTP endpoints:

- `GET /health` - Health check
- `GET /` - API information
- `POST /mcp/execute` - Execute MCP command
- `POST /mcp/initialize` - Initialize MCP session
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

### Example API Call

```bash
curl -X POST http://localhost:8080/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
  }'
```

## 🔒 Security Considerations

### GitHub Token

- **Never commit** your token to version control
- Use **fine-grained tokens** with minimal required scopes
- **Rotate tokens** regularly
- **Revoke tokens** if compromised

### Required Token Permissions

For full functionality, your token needs:
- **Repository access**: Read/write to repositories
- **Issues**: Read/write issues
- **Pull requests**: Read/write pull requests
- **Projects**: Read/write projects (if using project toolset)

### Network Security

- The add-on only exposes port 8080 locally
- Use SSH tunneling for remote access
- Never expose the port directly to the internet
- Home Assistant authentication is **not** applied (use SSH for security)

## 🐛 Troubleshooting

### Add-on won't start

Check the logs for:
- Invalid GitHub token format
- Missing token configuration
- Docker connectivity issues

```bash
# View logs
ha addons logs github-mcp-server
```

### "Docker not accessible" error

The add-on needs access to Docker. Ensure:
- Home Assistant Supervisor is running
- Docker daemon is accessible
- Add-on has necessary permissions

### VSCode can't connect

1. Verify add-on is running: Check **Info** tab shows "Running"
2. Test health endpoint:
   ```bash
   curl http://localhost:8080/health
   ```
3. Check SSH tunnel is active:
   ```bash
   netstat -an | grep 8080
   ```

### Token validation fails

Ensure your token:
- Starts with `ghp_` or `github_pat_`
- Has not expired
- Has required permissions
- Is correctly pasted (no extra spaces)

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8080/health
```

Response:
```json
{
  "status": "healthy",
  "docker_accessible": true,
  "version": "1.0.0"
}
```

### Logs

View real-time logs from Home Assistant:
- **UI**: Supervisor → GitHub MCP Server → Logs
- **CLI**: `ha addons logs github-mcp-server -f`

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [GitHub MCP Server](https://github.com/github/github-mcp-server) - Official GitHub implementation
- [Home Assistant](https://www.home-assistant.io/) - Open source home automation
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/pedrobsm/github-mcp-server-haos-addon/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pedrobsm/github-mcp-server-haos-addon/discussions)
- **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)

---

**Made with ❤️ for the Home Assistant and GitHub communities**

[releases-shield]: https://img.shields.io/github/release/pedrobsm/github-mcp-server-haos-addon.svg
[releases]: https://github.com/pedrobsm/github-mcp-server-haos-addon/releases
[license-shield]: https://img.shields.io/github/license/pedrobsm/github-mcp-server-haos-addon.svg
[ha-shield]: https://img.shields.io/badge/Home%20Assistant-Add--on-blue.svg
[ha-url]: https://www.home-assistant.io/
