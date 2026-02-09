---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''

---

## Describe the Bug
A clear and concise description of what the bug is.

## Steps to Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Configure '....'
3. Run '....'
4. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Actual Behavior
What actually happened.

## Logs
```
Paste relevant logs from Home Assistant Supervisor → GitHub MCP Server → Logs
```

## Environment
- Home Assistant Version: [e.g. 2026.2.1]
- Add-on Version: [e.g. 1.0.0]
- Architecture: [e.g. amd64, aarch64, armv7]
- Installation Type: [e.g. Home Assistant OS, Supervised]

## Configuration
```yaml
# Paste your add-on configuration (REMOVE your GitHub token!)
github_token: ghp_***
toolsets: repos,issues,pull_requests,projects
port: 8080
log_level: info
```

## Additional Context
Add any other context about the problem here.

## Screenshots
If applicable, add screenshots to help explain your problem.

## Checklist
- [ ] I have checked the logs for errors
- [ ] I have verified my GitHub token has correct permissions
- [ ] I have tested the health endpoint (`/health`)
- [ ] I have checked existing issues for duplicates
