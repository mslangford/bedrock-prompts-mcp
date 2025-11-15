#!/bin/bash
# Quick GitHub setup script
# Usage: ./setup_github.sh YOUR_GITHUB_USERNAME

set -e

if [ -z "$1" ]; then
    echo "Usage: ./setup_github.sh YOUR_GITHUB_USERNAME"
    echo "Example: ./setup_github.sh mlangford29"
    exit 1
fi

USERNAME=$1
REPO_NAME="bedrock-prompts-mcp"
REPO_URL="https://github.com/${USERNAME}/${REPO_NAME}.git"

echo "========================================="
echo "GitHub Setup for Bedrock Prompts MCP"
echo "========================================="
echo ""
echo "Repository: ${REPO_URL}"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Error: git is not installed"
    echo "Install: https://git-scm.com/downloads"
    exit 1
fi

# Check if already initialized
if [ -d ".git" ]; then
    echo "✓ Git repository already initialized"
else
    echo "→ Initializing git repository..."
    git init
    echo "✓ Git repository initialized"
fi

# Configure git if needed
if ! git config user.name > /dev/null 2>&1; then
    echo ""
    read -p "Enter your name for git commits: " GIT_NAME
    git config user.name "$GIT_NAME"
fi

if ! git config user.email > /dev/null 2>&1; then
    echo ""
    read -p "Enter your email for git commits: " GIT_EMAIL
    git config user.email "$GIT_EMAIL"
fi

echo ""
echo "→ Adding files to git..."
git add .

echo "→ Creating initial commit..."
git commit -m "Initial commit: Bedrock Prompts MCP Server v0.2.0

Features:
- List and manage Bedrock prompts
- Invoke prompts with variable substitution
- Batch invocation with parallel execution
- Streaming responses
- Multi-model support (Claude, Titan, Llama, Mistral, Cohere, AI21)
- Claude Desktop integration"

echo "✓ Initial commit created"

# Check if remote already exists
if git remote | grep -q "origin"; then
    echo ""
    echo "! Remote 'origin' already exists"
    echo "  Current URL: $(git remote get-url origin)"
    read -p "Update to ${REPO_URL}? (y/N): " UPDATE_REMOTE
    if [[ $UPDATE_REMOTE =~ ^[Yy]$ ]]; then
        git remote set-url origin "$REPO_URL"
        echo "✓ Remote updated"
    fi
else
    echo "→ Adding remote origin..."
    git remote add origin "$REPO_URL"
    echo "✓ Remote added"
fi

echo ""
echo "========================================="
echo "NEXT STEPS:"
echo "========================================="
echo ""
echo "1. Create the repository on GitHub:"
echo "   → Go to: https://github.com/new"
echo "   → Name: ${REPO_NAME}"
echo "   → Visibility: Public or Private"
echo "   → DON'T initialize with README/license/gitignore"
echo "   → Click 'Create repository'"
echo ""
echo "2. Then run these commands to push:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "Or use GitHub CLI:"
echo "   gh repo create ${REPO_NAME} --public --source=. --remote=origin --push"
echo ""
echo "Repository URL: ${REPO_URL}"
echo ""
