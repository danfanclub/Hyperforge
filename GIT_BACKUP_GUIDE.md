# Git Backup Guide

This guide explains how to back up your gpt-oss setup to GitHub safely (without exposing secrets or uploading large model files).

## What Gets Backed Up

### ✅ **SAFE to commit** (include in git):

- `gpt-oss-local-setup/` folder (this entire setup directory)
  - `README.md` - Main setup guide
  - `SETUP_INSTRUCTIONS_FOR_LLM.md` - Automated setup instructions
  - `MODIFICATIONS.md` - Documentation of code changes
  - `GIT_BACKUP_GUIDE.md` - This file
  - `credentials.template.sh` - Template with placeholders
  - `start_server.template.sh` - Server startup template
  - `chat_client.py` - Chat client script
  - `custom_files/` - Custom code files
    - `google_backend.py`
    - `DOCKER_FIX.md`
  - `.gitignore` - Protects secrets

### ❌ **NEVER commit** (excluded by .gitignore):

- `credentials.sh` - **CONTAINS YOUR ACTUAL API KEYS!**
- `start_server.sh` - May contain paths specific to your system
- `gpt-oss/` - Entire repository (already on GitHub)
- `llmsearch/` - Entire repository (already on GitHub)
- Model files (*.bin, *.safetensors, etc.)
- Virtual environments (.venv/)
- Any file with actual API keys

## Initial Git Setup

### Option 1: Create New Repository

```bash
cd /home/merlin/Hyperforge

# Initialize git repository
git init

# Add the .gitignore (protects secrets)
git add .gitignore
git add gpt-oss-local-setup/

# Create initial commit
git commit -m "Initial commit: gpt-oss local setup with Google Custom Search"

# Create repository on GitHub (via web interface)
# Then connect it:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Option 2: Add to Existing Repository

```bash
cd /home/merlin/Hyperforge

# If already a git repo
git add .gitignore
git add gpt-oss-local-setup/

git commit -m "Add gpt-oss local setup configuration"
git push
```

## Verify Secrets are Protected

**BEFORE your first push, double-check:**

```bash
cd /home/merlin/Hyperforge

# Check what will be committed
git status

# Verify credentials.sh is NOT listed
git status | grep credentials.sh
# Should output nothing (file is ignored)

# Double-check what's staged
git diff --cached --name-only

# Make ABSOLUTELY sure no secrets are included
grep -r "YOUR_GOOGLE_API_KEY\|ydc-sk-\|AIzaSy" gpt-oss-local-setup/
# Should only find them in .template files with placeholder text
```

## Safe Commit Workflow

```bash
cd /home/merlin/Hyperforge

# 1. Check status
git status

# 2. Add ONLY the setup folder
git add gpt-oss-local-setup/

# 3. Verify what's being committed
git diff --cached

# 4. Make sure credentials.sh is NOT in the list
git status | grep credentials.sh
# Should return nothing

# 5. Commit
git commit -m "Update setup documentation"

# 6. Push
git push
```

## What to Do if You Accidentally Commit Secrets

**If you accidentally committed API keys:**

### IMMEDIATELY:

1. **Revoke the exposed API keys** (Google Console, You.com dashboard, etc.)
2. **Remove from git history** (more complex):

```bash
# Remove the file from history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch credentials.sh" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (WARNING: Rewrites history)
git push origin --force --all

# Clean up
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

3. **Generate new API keys** and update `credentials.sh` locally

### Better: Prevent it

- Always check `git status` before committing
- Use `git diff --cached` to review what's being committed
- The `.gitignore` files are your safety net - don't delete them!

## Recommended Repository Structure

```
your-repo/
├── README.md                          # Main project README
├── .gitignore                         # Protects secrets
└── gpt-oss-local-setup/              # Setup folder (committed)
    ├── README.md
    ├── SETUP_INSTRUCTIONS_FOR_LLM.md
    ├── MODIFICATIONS.md
    ├── GIT_BACKUP_GUIDE.md
    ├── credentials.template.sh        # Template (safe)
    ├── credentials.sh                 # IGNORED (secrets)
    ├── start_server.template.sh       # Template (safe)
    ├── start_server.sh                # IGNORED (may have paths)
    ├── chat_client.py
    ├── .gitignore
    └── custom_files/
        ├── google_backend.py
        └── DOCKER_FIX.md
```

## Cloning Your Repo on Another Machine

When you clone your repository on a new machine:

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# Follow setup instructions
cd gpt-oss-local-setup
cat README.md  # Read the setup guide
cat SETUP_INSTRUCTIONS_FOR_LLM.md  # Detailed automation instructions

# Create your credentials.sh from template
cp credentials.template.sh credentials.sh
nano credentials.sh  # Add your API keys

# Follow the rest of the setup
```

## Regular Backups

After making changes:

```bash
cd /home/merlin/Hyperforge

# Update documentation if you made changes
git add gpt-oss-local-setup/
git commit -m "Update setup: [describe changes]"
git push
```

## Security Best Practices

1. **Never hardcode API keys** in scripts - use environment variables
2. **Use templates** with placeholders for sensitive data
3. **Review before committing** - always check what's staged
4. **Keep .gitignore** up to date
5. **Rotate API keys** periodically
6. **Use private repositories** if unsure

## GitHub Repository Settings

For maximum security:

1. **Make repository private** (unless you're sure all secrets are protected)
2. **Enable branch protection** on main branch
3. **Require reviews** for changes (if working with team)
4. **Enable secret scanning** in repository settings

## Questions?

- What to commit: Template files, documentation, custom code
- What NOT to commit: credentials.sh, model files, cloned repos
- When in doubt: Check `git status` and verify against `.gitignore`

Remember: **It's much easier to prevent exposing secrets than to clean them up after!**
