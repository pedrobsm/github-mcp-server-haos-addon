# Contributing to GitHub MCP Server Add-on

Thank you for your interest in contributing to the GitHub MCP Server add-on for Home Assistant! 🎉

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

1. **Clear title and description**
2. **Steps to reproduce** the issue
3. **Expected vs actual behavior**
4. **Logs** from the add-on (redact sensitive information)
5. **Environment details** (HA version, architecture, etc.)

Use the bug report template when creating issues.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

1. **Use case** - Why is this enhancement needed?
2. **Proposed solution** - How should it work?
3. **Alternatives** - What other approaches have you considered?

Use the feature request template when creating issues.

### Pull Requests

1. **Fork the repository** and create a branch from `main`
2. **Make your changes** following the coding standards
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Submit a pull request**

## Development Setup

### Prerequisites

- Docker
- Python 3.11+
- Home Assistant test environment (optional but recommended)

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/pedrobsm/github-mcp-server-haos-addon.git
   cd github-mcp-server-haos-addon
   ```

2. Make your changes to the code

3. Test the FastAPI wrapper locally:
   ```bash
   cd mcp_bridge
   pip install -r requirements.txt
   export GITHUB_PERSONAL_ACCESS_TOKEN=your_token
   export GITHUB_TOOLSETS=repos
   export MCP_PORT=8080
   export LOG_LEVEL=debug
   python3 app.py
   ```

4. Build the Docker image:
   ```bash
   docker build -t local/github-mcp-server .
   ```

5. Test the add-on:
   ```bash
   docker run -it --rm \
     -e GITHUB_PERSONAL_ACCESS_TOKEN=your_token \
     -e GITHUB_TOOLSETS=repos \
     -e MCP_PORT=8080 \
     -e LOG_LEVEL=info \
     -p 8080:8080 \
     local/github-mcp-server
   ```

6. Test endpoints:
   ```bash
   # Health check
   curl http://localhost:8080/health

   # MCP command
   curl -X POST http://localhost:8080/mcp/execute \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
   ```

### Testing in Home Assistant

1. Copy the add-on to your Home Assistant instance:
   ```bash
   scp -r . root@homeassistant.local:/addons/github-mcp-server/
   ```

2. Install as a local add-on:
   - Supervisor → Add-on Store → ⋮ → Check for updates
   - Find "GitHub MCP Server" in local add-ons
   - Install and configure

3. Check logs for any issues

## Coding Standards

### Python

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints where possible
- Document functions with docstrings
- Keep functions focused and small
- Use meaningful variable names

### Example:

```python
async def execute_command(request: MCPRequest) -> MCPResponse:
    """
    Execute MCP command via GitHub MCP Server.
    
    Args:
        request: MCP request object with method and parameters
        
    Returns:
        MCPResponse with result or error
        
    Raises:
        HTTPException: If execution fails
    """
    # Implementation
```

### Shell Scripts

- Use `#!/usr/bin/with-contenv bashio` for add-on scripts
- Quote variables: `"$VAR"` instead of `$VAR`
- Check exit codes of important commands
- Use `bashio::log.*` for logging

### Docker

- Keep images small
- Use specific base image versions
- Clean up in the same layer when installing packages
- Add health checks

### Configuration

- Validate all user inputs
- Provide sensible defaults
- Document all options in README
- Use appropriate schema types (password, port, etc.)

## Documentation

When making changes that affect users:

1. Update `README.md` with new features or configuration
2. Update `CHANGELOG.md` with changes
3. Update `docs/vscode-setup.md` if VSCode configuration changes
4. Update version in `config.json`

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add support for GitHub search toolset
fix: Resolve Docker connectivity issue on aarch64
docs: Update VSCode setup instructions
refactor: Simplify MCP client error handling
```

**Commit message format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding/updating tests
- `chore:` - Maintenance tasks

## Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

Update version in:
- `config.json`
- `CHANGELOG.md`
- Git tag when releasing

## Release Process

1. Update `CHANGELOG.md` with all changes
2. Update version in `config.json`
3. Commit changes: `git commit -m "chore: Bump version to X.Y.Z"`
4. Create tag: `git tag -a vX.Y.Z -m "Release X.Y.Z"`
5. Push: `git push && git push --tags`
6. GitHub Actions will build and create release automatically

## Questions?

- Open a [Discussion](https://github.com/pedrobsm/github-mcp-server-haos-addon/discussions) for general questions
- Open an [Issue](https://github.com/pedrobsm/github-mcp-server-haos-addon/issues) for bugs or features
- Check existing issues and discussions first

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing! 🚀**
