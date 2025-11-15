# GitHub Setup Guide

## Quick Start (5 minutes)

### 1. Create GitHub Repository

**Option A: Via GitHub Website**
1. Go to https://github.com/new
2. Repository name: `bedrock-prompts-mcp`
3. Description: `MCP server for AWS Bedrock managed prompts with batch invocation and streaming support`
4. Choose: Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

**Option B: Via GitHub CLI**
```bash
gh repo create bedrock-prompts-mcp --public --source=. --remote=origin
```

### 2. Initialize and Push

From your project directory:

```bash
# Navigate to project directory
cd /path/to/bedrock-prompts-mcp

# Initialize git repository
git init

# Add all files
git add .

# Make first commit
git commit -m "Initial commit: Bedrock Prompts MCP Server v0.2.0

Features:
- List and manage Bedrock prompts
- Invoke prompts with variable substitution
- Batch invocation with parallel execution
- Streaming responses
- Multi-model support (Claude, Titan, Llama, Mistral, Cohere, AI21)
- Claude Desktop integration"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/bedrock-prompts-mcp.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 3. Verify

Visit `https://github.com/YOUR_USERNAME/bedrock-prompts-mcp` to see your repository!

---

## Detailed Steps

### Prerequisites

1. **Git installed**: `git --version`
2. **GitHub account**: https://github.com/signup
3. **GitHub CLI (optional)**: `gh --version` or install from https://cli.github.com/

### Project Structure

Your repository should have:

```
bedrock-prompts-mcp/
├── .gitignore                          # Git ignore rules
├── LICENSE                             # MIT license
├── README.md                           # Main documentation
├── CHANGELOG.md                        # Version history
├── QUICK_REFERENCE.md                  # Usage examples
├── requirements.txt                    # Python dependencies
├── pyproject.toml                      # Package configuration
├── bedrock_prompts_mcp_server.py      # Main server code
├── examples.py                         # Example usage
└── claude_desktop_config.example.json  # Config template
```

### Step-by-Step GitHub Push

#### 1. Set up Git (first time only)
```bash
# Configure your identity
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Optional: Set default branch name
git config --global init.defaultBranch main
```

#### 2. Initialize Repository
```bash
cd /path/to/bedrock-prompts-mcp

# Initialize git
git init

# Check status
git status
```

#### 3. Stage Files
```bash
# Add all files
git add .

# Or add selectively
git add README.md
git add bedrock_prompts_mcp_server.py
git add requirements.txt
# etc.

# Check what will be committed
git status
```

#### 4. Create First Commit
```bash
git commit -m "Initial commit: Bedrock Prompts MCP Server v0.2.0"
```

#### 5. Create GitHub Repository

**Via Web Browser:**
1. Go to https://github.com/new
2. Fill in repository details:
   - **Name**: `bedrock-prompts-mcp`
   - **Description**: `MCP server for AWS Bedrock managed prompts`
   - **Visibility**: Public (recommended for open source) or Private
   - **DON'T** check any initialization options
3. Click "Create repository"
4. Copy the repository URL (e.g., `https://github.com/YOUR_USERNAME/bedrock-prompts-mcp.git`)

**Via GitHub CLI:**
```bash
# Login first (one time)
gh auth login

# Create repo and push
gh repo create bedrock-prompts-mcp \
    --public \
    --source=. \
    --remote=origin \
    --push
```

#### 6. Link and Push

**If you created via web browser:**
```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/bedrock-prompts-mcp.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

**If you used GitHub CLI**, it already pushed for you! Skip to verification.

#### 7. Verify Upload
```bash
# Check remote status
git remote show origin

# View on GitHub
# Visit: https://github.com/YOUR_USERNAME/bedrock-prompts-mcp
```

---

## Making Updates

After initial push, to update your repository:

```bash
# Make changes to files
# ...

# Check what changed
git status
git diff

# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature X" -m "Detailed description of changes"

# Push to GitHub
git push
```

---

## Best Practices

### Commit Messages

**Good commit messages:**
```bash
git commit -m "Add streaming support for Titan models"
git commit -m "Fix: Handle empty variable sets in batch invocation"
git commit -m "Docs: Update README with batch invocation examples"
```

**Message format:**
- First line: Brief summary (50 chars or less)
- Use present tense: "Add feature" not "Added feature"
- Prefix: `Fix:`, `Docs:`, `Feature:`, `Refactor:`, etc.

### Branching (for larger changes)

```bash
# Create feature branch
git checkout -b feature/add-model-support

# Make changes, commit
git add .
git commit -m "Add support for new model type"

# Push branch
git push -u origin feature/add-model-support

# On GitHub: Create Pull Request
# After merge: Switch back to main
git checkout main
git pull
```

### .gitignore

Already included! Prevents committing:
- AWS credentials
- Python cache files
- Virtual environments
- Local config files

**NEVER commit:**
- AWS credentials
- API keys
- Passwords
- Local configuration with secrets

---

## Adding GitHub Badges (Optional)

Add to top of README.md:

```markdown
# Bedrock Prompts MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

---

## Troubleshooting

### "Permission denied (publickey)"

**Solution: Use HTTPS instead of SSH**
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/bedrock-prompts-mcp.git
```

Or **set up SSH keys**: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### "Already exists" error when creating repo

Repository name already taken. Choose different name or delete existing repo.

### "Updates were rejected" when pushing

```bash
# Pull latest changes first
git pull origin main --rebase

# Then push
git push
```

### Large files rejected

GitHub has 100MB file limit. Check what's large:
```bash
git ls-files | xargs ls -lh | sort -k5 -hr | head -10
```

Remove from git:
```bash
git rm --cached large_file.bin
echo "large_file.bin" >> .gitignore
git commit -m "Remove large file"
```

---

## Next Steps

After pushing to GitHub:

1. **Add topics** to make repository discoverable:
   - Go to repository → About (gear icon)
   - Add topics: `mcp`, `bedrock`, `aws`, `claude`, `python`, `ai`

2. **Enable GitHub Actions** (optional):
   - Add automated testing
   - Linting checks
   - Release automation

3. **Create releases**:
   - Tag versions: `git tag v0.2.0`
   - Push tags: `git push --tags`
   - Create release on GitHub with changelog

4. **Add documentation**:
   - GitHub Wiki for detailed docs
   - GitHub Pages for hosted documentation

5. **Community files**:
   - CONTRIBUTING.md
   - CODE_OF_CONDUCT.md
   - Issue templates
   - Pull request templates

---

## Quick Command Reference

```bash
# Check status
git status

# View changes
git diff

# Add files
git add .
git add file.py

# Commit
git commit -m "Message"

# Push
git push

# Pull latest
git pull

# View history
git log --oneline

# Create branch
git checkout -b branch-name

# Switch branch
git checkout main

# View remotes
git remote -v

# Update remote URL
git remote set-url origin NEW_URL
```

---

## Resources

- **Git Documentation**: https://git-scm.com/doc
- **GitHub Docs**: https://docs.github.com
- **GitHub CLI**: https://cli.github.com
- **Learn Git**: https://learngitbranching.js.org/
- **Git Cheat Sheet**: https://education.github.com/git-cheat-sheet-education.pdf
