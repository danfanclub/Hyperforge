# GPT-OSS Local Setup with Ollama Backend

This folder contains everything needed to set up a local gpt-oss-20b instance with:
- Ollama backend for inference
- Google Custom Search for web browsing
- Python code execution in Docker
- Interactive chat client

## System Requirements

- **Hardware**: NVIDIA GPU with 16GB+ VRAM (tested on 4080 Super)
- **OS**: Linux (tested on ArchLinux)
- **Software**:
  - Docker (for Python code execution)
  - Ollama (for model inference)
  - Python 3.12+
  - Chromium/Chrome (for web scraping)

## Quick Setup Guide

### 1. Install Dependencies

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull gpt-oss-20b model
ollama pull gpt-oss:20b

# Install system packages (ArchLinux)
sudo pacman -S docker chromium python

# Start Docker
sudo systemctl start docker
sudo usermod -aG docker $USER  # Add yourself to docker group
```

### 2. Clone gpt-oss Repository

```bash
cd /home/merlin/Hyperforge
git clone https://github.com/openai/gpt-oss.git
cd gpt-oss

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install gpt-oss openai-harmony pytest
pip install selenium wordfreq nltk quart quart-cors hypercorn
```

### 3. Apply Custom Modifications

Copy the custom files from this setup folder:

```bash
# Copy custom Google backend
cp custom_files/google_backend.py gpt-oss/gpt_oss/tools/simple_browser/

# Copy modified Docker tool (with host networking fix)
cp custom_files/docker_tool_patch.py gpt-oss/gpt_oss/tools/python_docker/docker_tool.py

# Copy API server modifications
# (or manually apply the changes described in MODIFICATIONS.md)
```

### 4. Configure API Keys

Copy and edit the credentials template:

```bash
cp credentials.template.sh credentials.sh
nano credentials.sh  # Edit with your actual API keys
```

Fill in:
- `GOOGLE_KEY` - Your Google Custom Search API key
- `GOOGLE_CX` - Your Custom Search Engine ID

**DO NOT commit credentials.sh to git!**

### 5. Start the Server

```bash
# Make scripts executable
chmod +x start_server.sh

# Start the server
./start_server.sh
```

### 6. Use the Chat Client

In a new terminal:

```bash
cd /home/merlin/Hyperforge/gpt-oss-local-setup
./chat_client.py
```

## Getting API Keys

### Google Custom Search API (Free Tier: 100 searches/day)

1. **Google API Key**:
   - Go to https://console.cloud.google.com/
   - Create/select a project
   - Enable "Custom Search API"
   - Create credentials → API Key
   - Copy the key

2. **Custom Search Engine ID (CX)**:
   - Go to https://programmablesearchengine.google.com/
   - Create new search engine
   - Set "Sites to search" to `*` (whole web)
   - Get your Search Engine ID from settings

## Files in This Setup

- **`README.md`** - This file
- **`SETUP_INSTRUCTIONS_FOR_LLM.md`** - Detailed instructions for automated setup by an LLM
- **`credentials.template.sh`** - Template for API keys (edit and rename to credentials.sh)
- **`start_server.template.sh`** - Template for server startup script
- **`chat_client.py`** - Interactive chat client
- **`custom_files/`** - Custom code modifications
  - `google_backend.py` - Google Custom Search integration
  - `docker_tool_patch.py` - Docker networking fix
- **`MODIFICATIONS.md`** - Documentation of all code changes made

## Security Notes

**Never commit these files to git:**
- `credentials.sh`
- Any file containing API keys
- `.env` files

**The .gitignore in parent directory should exclude:**
- `credentials.sh`
- `*.key`
- `.env`

## Troubleshooting

See `TROUBLESHOOTING.md` for common issues and solutions.

## What Gets Backed Up to Git

**Include in git:**
- This setup folder (gpt-oss-local-setup/)
- Template files
- Custom code files
- Documentation

**Exclude from git:**
- credentials.sh (actual API keys)
- gpt-oss/ directory (already on GitHub)
- Model files
- Virtual environments

## License

This setup uses:
- gpt-oss (Apache 2.0) - https://github.com/openai/gpt-oss
- Custom modifications (your choice of license)
