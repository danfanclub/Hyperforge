# GPT-OSS Local Setup with Ollama Backend

This folder contains everything needed to set up a local gpt-oss-20b instance with:
- **Ollama backend** for inference
- **Web search** (Google Custom Search, Exa, or You.com)
- **Python code execution** in Docker
- **File editing** (create, update, delete files)
- **Interactive chat client** with automatic tool enablement

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
# Navigate to this setup folder
cd /home/merlin/Hyperforge/gpt-oss-local-setup

# Copy custom Google backend
cp custom_files/google_backend.py ../gpt-oss/gpt_oss/tools/simple_browser/

# Copy file editing tool
cp custom_files/apply_patch_tool.py ../gpt-oss/gpt_oss/tools/

# Apply API server modifications
# See MODIFICATIONS.md and custom_files/FILE_EDITING_INTEGRATION.md for details
# You'll need to manually apply changes to:
# - gpt_oss/responses_api/api_server.py
# - gpt_oss/responses_api/types.py
# - gpt_oss/tools/python_docker/docker_tool.py (host networking fix)
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

Make sure Ollama is running (it usually runs as a service automatically):

```bash
# Check if Ollama is running
ollama ps

# If not running, start it
ollama serve
```

Then start the Responses API server:

```bash
cd /home/merlin/Hyperforge/gpt-oss
source .venv/bin/activate

# Start with Ollama backend (IMPORTANT: specify model name)
python -m gpt_oss.responses_api.serve \
    --inference-backend ollama \
    --checkpoint gpt-oss:20b \
    --port 8000
```

### 6. Use the Enhanced Chat Client

In a new terminal, navigate to your working directory and start the chat:

```bash
# Navigate to where you want to work (model can edit files here)
cd ~/Documents/my-project

# Start the chat client (from anywhere)
python /home/merlin/Hyperforge/gpt-oss-local-setup/gpt-oss-chat.py

# Or if you've set up the wrapper script:
gpt-oss-chat
```

**Features**:
- 🔍 **Automatic web search** - Model can search the web for information
- 📝 **Automatic file editing** - Model can create/update/delete files in current directory
- 💬 **Conversation history** - Maintains context across the chat
- 🎨 **Color-coded output** - Easy-to-read terminal UI
- ⚡ **Commands**: `/exit`, `/clear`, `/history`, `/help`

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
- **`gpt-oss-chat.py`** - **NEW** Enhanced interactive chat client with file editing and web search
- **`chat_client.py`** - Original basic chat client (deprecated)
- **`custom_files/`** - Custom code modifications
  - `apply_patch_tool.py` - **NEW** File editing tool implementation
  - `FILE_EDITING_INTEGRATION.md` - **NEW** Documentation for file editing setup
  - `google_backend.py` - Google Custom Search integration
  - `DOCKER_FIX.md` - Docker networking fix documentation
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
