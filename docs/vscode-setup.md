# VSCode MCP Client Setup Guide

This guide provides detailed instructions for configuring VSCode to use the GitHub MCP Server running on Home Assistant OS.

## 📋 Prerequisites

- Home Assistant OS with GitHub MCP Server add-on installed and running
- SSH access to Home Assistant
- VSCode installed on your development machine
- VSCode Remote - SSH extension installed

## 🔧 Setup Methods

### Method 1: Remote Development via SSH (Recommended)

This method is ideal when you're developing on a different machine and connecting to Home Assistant via SSH.

#### 1. Establish SSH Tunnel

Open a terminal on your local machine and create an SSH tunnel:

```bash
ssh -L 8080:localhost:8080 root@homeassistant.local
```

**Explanation:**
- `-L 8080:localhost:8080` - Forwards local port 8080 to Home Assistant's port 8080
- `root@homeassistant.local` - Connects to Home Assistant (adjust hostname/IP as needed)

**Keep this terminal open** while developing. The tunnel must remain active for VSCode to communicate with the MCP server.

#### 2. Configure VSCode Workspace

In your workspace, create or edit `.vscode/settings.json`:

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

#### 3. Alternative: User Settings

To make this available across all workspaces, add to your global VSCode settings:

1. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Type "Preferences: Open User Settings (JSON)"
3. Add the MCP configuration as shown above

### Method 2: Direct Access on Home Assistant

If you're developing directly on Home Assistant OS via SSH:

#### 1. Connect via VSCode Remote SSH

1. Install "Remote - SSH" extension in VSCode
2. Press `F1` and select "Remote-SSH: Connect to Host"
3. Enter: `root@homeassistant.local`
4. Open your project folder on the remote machine

#### 2. Configure MCP Client

Create `.vscode/settings.json` in your workspace:

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

### Method 3: Multiple MCP Servers

If you already have other MCP servers configured:

```json
{
  "mcp": {
    "servers": {
      "github-ha": {
        "type": "http",
        "url": "http://localhost:8080/mcp",
        "description": "GitHub via Home Assistant"
      },
      "github-local": {
        "type": "stdio",
        "command": "docker",
        "args": [
          "run", "-i", "--rm",
          "-e", "GITHUB_PERSONAL_ACCESS_TOKEN=${env:GITHUB_TOKEN}",
          "ghcr.io/github/github-mcp-server:latest"
        ],
        "description": "GitHub local Docker"
      }
    }
  }
}
```

## 🧪 Testing the Connection

### 1. Health Check

First, verify the MCP server is accessible:

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "docker_accessible": true,
  "version": "1.0.0"
}
```

### 2. API Documentation

Open in your browser:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

### 3. Test MCP Command

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

### 4. VSCode MCP Test

1. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Type "MCP: Test Connection"
3. Select "github" (or your configured server name)
4. Check for success message

## 🎯 Using MCP with GitHub Copilot

Once configured, you can use natural language with GitHub Copilot:

### Repository Operations
```
"Show me all my GitHub repositories"
"List repositories in organization X"
"Create a new repository called my-project"
```

### Issue Management
```
"What open issues do I have in repo/name?"
"Create a bug issue: Login button not working"
"Close issue #123 in my-repo"
```

### Pull Requests
```
"Show me open pull requests waiting for my review"
"Create a PR from feature-branch to main"
"List recent merged PRs in this repository"
```

### Code Search
```
"Find all occurrences of function_name in my repos"
"Search for TODO comments in repository X"
```

## 🔧 Advanced Configuration

### Custom Port

If using a different port, update both the add-on configuration and VSCode:

**Add-on Configuration:**
```yaml
port: 9000
```

**VSCode Settings:**
```json
{
  "mcp": {
    "servers": {
      "github": {
        "url": "http://localhost:9000/mcp"
      }
    }
  }
}
```

**SSH Tunnel:**
```bash
ssh -L 9000:localhost:9000 root@homeassistant.local
```

### SSH Config File

Create `~/.ssh/config` for easier connections:

```
Host ha
    HostName homeassistant.local
    User root
    LocalForward 8080 localhost:8080
```

Then simply connect with:
```bash
ssh ha
```

### Automatic Tunnel with VSCode

Add to `.vscode/settings.json`:

```json
{
  "remote.SSH.localServerDownload": "always",
  "remote.SSH.enableRemoteCommand": true,
  "terminal.integrated.profiles.linux": {
    "ssh-tunnel": {
      "path": "/bin/bash",
      "args": ["-c", "ssh -L 8080:localhost:8080 root@homeassistant.local"]
    }
  }
}
```

## 🐛 Troubleshooting

### Connection Refused

**Symptoms:** VSCode can't connect to MCP server

**Solutions:**
1. Verify add-on is running:
   ```bash
   ha addons info github-mcp-server
   ```

2. Check if port is listening:
   ```bash
   netstat -tlnp | grep 8080
   ```

3. Test local connection on Home Assistant:
   ```bash
   curl http://localhost:8080/health
   ```

### SSH Tunnel Drops

**Symptoms:** Connection works then fails intermittently

**Solutions:**
1. Use persistent SSH connection:
   ```bash
   ssh -L 8080:localhost:8080 -N -f root@homeassistant.local
   ```
   - `-N` - Don't execute commands
   - `-f` - Run in background

2. Add keep-alive to `~/.ssh/config`:
   ```
   Host ha
       ServerAliveInterval 60
       ServerAliveCountMax 3
   ```

### Token Permission Errors

**Symptoms:** MCP commands fail with authorization errors

**Solutions:**
1. Verify token scopes at: https://github.com/settings/tokens
2. Required scopes:
   - `repo` - Full repository access
   - `read:org` - Organization read access
   - `project` - Project access (if using projects)

3. Update token in add-on configuration

### VSCode MCP Not Detected

**Symptoms:** MCP features don't appear in VSCode

**Solutions:**
1. Ensure MCP extension is installed
2. Reload VSCode window: `Ctrl+Shift+P` → "Reload Window"
3. Check VSCode output panel: "View" → "Output" → Select "MCP"

## 📊 Monitoring

### View MCP Server Logs

From Home Assistant:
```bash
ha addons logs github-mcp-server -f
```

From VSCode terminal (if SSH connected):
```bash
docker logs -f addon_github-mcp-server
```

### Enable Debug Logging

Update add-on configuration:
```yaml
log_level: debug
```

Restart add-on and check logs for detailed information.

## 🔐 Security Best Practices

1. **Never expose port 8080 to the internet**
   - Always use SSH tunneling for remote access
   - Don't open port in firewall/router

2. **Use fine-grained tokens**
   - Create tokens with minimal required permissions
   - Set token expiration dates
   - Use different tokens for different purposes

3. **Rotate tokens regularly**
   - Update token in add-on configuration
   - Revoke old tokens in GitHub settings

4. **Monitor access**
   - Check add-on logs regularly
   - Review GitHub token usage

## 💡 Tips & Tricks

### Quick Connect Script

Create `~/bin/ha-mcp-connect.sh`:

```bash
#!/bin/bash
echo "Connecting to Home Assistant MCP..."
ssh -L 8080:localhost:8080 -N root@homeassistant.local &
SSH_PID=$!
echo "SSH tunnel established (PID: $SSH_PID)"
echo "Press Ctrl+C to disconnect"
trap "kill $SSH_PID" EXIT
wait $SSH_PID
```

Make executable and use:
```bash
chmod +x ~/bin/ha-mcp-connect.sh
~/bin/ha-mcp-connect.sh
```

### VSCode Task

Add to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Connect to HA MCP",
      "type": "shell",
      "command": "ssh",
      "args": [
        "-L", "8080:localhost:8080",
        "-N", "root@homeassistant.local"
      ],
      "isBackground": true,
      "problemMatcher": []
    }
  ]
}
```

Run with: `Ctrl+Shift+P` → "Tasks: Run Task" → "Connect to HA MCP"

---

**Happy coding with GitHub MCP on Home Assistant! 🚀**
