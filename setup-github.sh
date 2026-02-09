#!/bin/bash
# GitHub MCP Server Add-on - Repository Setup Script
# This script helps you prepare the add-on for GitHub publication

set -e

echo "========================================"
echo "GitHub MCP Server Add-on"
echo "Repository Setup Wizard"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "config.json" ]; then
    echo "❌ Error: config.json not found!"
    echo "Please run this script from the /addons/github-mcp-server directory"
    exit 1
fi

# Ask for GitHub username
echo "📝 Step 1: GitHub Configuration"
echo "--------------------------------"
read -p "Enter your GitHub username: " GITHUB_USER

if [ -z "$GITHUB_USER" ]; then
    echo "❌ Username cannot be empty"
    exit 1
fi

# Ask for maintainer name
read -p "Enter your name (for repository.json): " MAINTAINER_NAME
read -p "Enter your email: " MAINTAINER_EMAIL

REPO_URL="https://github.com/${GITHUB_USER}/ha-addon-github-mcp"

# Update repository.json
echo ""
echo "📝 Step 2: Updating repository.json..."
cat > repository.json <<EOF
{
  "name": "GitHub MCP Server Add-on Repository",
  "url": "${REPO_URL}",
  "maintainer": "${MAINTAINER_NAME} <${MAINTAINER_EMAIL}>"
}
EOF
echo "✅ repository.json updated"

# Update config.json
echo ""
echo "📝 Step 3: Updating config.json..."
sed -i "s|https://github.com/YOUR_USERNAME/ha-addon-github-mcp|${REPO_URL}|g" config.json
echo "✅ config.json updated"

# Update README.md
echo ""
echo "📝 Step 4: Updating documentation..."
for file in README.md QUICKSTART.md CONTRIBUTING.md docs/vscode-setup.md; do
    sed -i "s/YOUR_USERNAME/${GITHUB_USER}/g" "$file"
    echo "  ✅ Updated $file"
done

# Initialize git if not already
echo ""
echo "📝 Step 5: Git Repository Setup"
echo "--------------------------------"
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "feat: Initial implementation of GitHub MCP Server add-on

- Complete Home Assistant add-on structure
- FastAPI HTTP wrapper for GitHub MCP Server
- Multi-architecture support (amd64, aarch64, armv7)
- Comprehensive documentation
- GitHub Actions CI/CD pipeline
- VSCode integration guide"
    echo "✅ Git repository initialized"
else
    echo "ℹ️  Git repository already exists"
fi

# Display instructions
echo ""
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Create GitHub repository:"
echo "   - Go to: https://github.com/new"
echo "   - Repository name: ha-addon-github-mcp"
echo "   - Description: GitHub MCP Server add-on for Home Assistant"
echo "   - Visibility: Public"
echo "   - DO NOT initialize with README, license, or .gitignore"
echo ""
echo "2. Push to GitHub:"
echo "   git remote add origin ${REPO_URL}.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Create first release:"
echo "   git tag -a v1.0.0 -m \"Release v1.0.0: Initial public release\""
echo "   git push origin v1.0.0"
echo ""
echo "4. Enable GitHub Actions:"
echo "   - Go to repository → Actions tab"
echo "   - Click 'I understand my workflows, go ahead and enable them'"
echo ""
echo "5. Configure repository:"
echo "   - Add topics: home-assistant, addon, mcp-server, github, vscode"
echo "   - Add description: GitHub MCP Server add-on for Home Assistant"
echo "   - Enable Issues and Discussions"
echo ""
echo "6. Test the add-on:"
echo "   - Install in Home Assistant from your repository"
echo "   - Configure with your GitHub token"
echo "   - Test VSCode integration"
echo ""
echo "📚 For detailed instructions, see: IMPLEMENTATION.md"
echo ""
echo "🔒 SECURITY REMINDER:"
echo "   Before committing, ensure no GitHub tokens are in:"
echo "   - ha_and_esphome.code-workspace"
echo "   - Any configuration files"
echo "   REVOKE exposed token: https://github.com/settings/tokens"
echo ""
echo "========================================"
