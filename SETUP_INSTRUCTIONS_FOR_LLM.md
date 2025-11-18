# Automated Setup Instructions for LLM Assistants

This document provides step-by-step instructions for an LLM assistant (like Claude) to automatically set up the gpt-oss local instance with all customizations.

## Prerequisites Check

Before starting, verify:
1. OS: Linux (preferably ArchLinux, but adaptable)
2. GPU: NVIDIA with 16GB+ VRAM
3. Docker installed and running
4. Ollama installed
5. Python 3.12+
6. User has API keys ready (Google Custom Search)

## Step-by-Step Automation

### Step 1: Install System Dependencies

```bash
# For ArchLinux
sudo pacman -S docker chromium python git

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
# Note: User needs to log out and back in for this to take effect

# Install Ollama if not installed
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Set Up Working Directory

```bash
# Create base directory
mkdir -p ~/Hyperforge
cd ~/Hyperforge

# Verify setup folder exists
if [ ! -d "gpt-oss-local-setup" ]; then
    echo "ERROR: gpt-oss-local-setup folder not found"
    echo "Please ensure you're in the correct directory"
    exit 1
fi
```

### Step 3: Clone and Set Up gpt-oss

```bash
# Clone official gpt-oss repository
git clone https://github.com/openai/gpt-oss.git
cd gpt-oss

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate

# Install base dependencies
pip install gpt-oss openai-harmony pytest

# Install additional dependencies for web search
pip install selenium wordfreq nltk quart quart-cors hypercorn
pip install requests  # For chat client
```

### Step 4: Download Model with Ollama

```bash
# Pull the gpt-oss-20b model
ollama pull gpt-oss:20b

# Verify it's downloaded
ollama list | grep gpt-oss
```

### Step 5: Apply Custom Modifications

```bash
cd ~/Hyperforge/gpt-oss-local-setup

# Copy Google Custom Search backend
cp custom_files/google_backend.py ../gpt-oss/gpt_oss/tools/simple_browser/

# Apply Docker networking fix
# Read the original file
DOCKER_TOOL="../gpt-oss/gpt_oss/tools/python_docker/docker_tool.py"

# Create backup
cp "$DOCKER_TOOL" "$DOCKER_TOOL.bak"

# Apply the fix: Add network_mode="host" to line ~66
# Find the line with: container = _docker_client.containers.create(
# And add network_mode="host" parameter
sed -i 's/detach=True$/detach=True, network_mode="host"/' "$DOCKER_TOOL"

# Verify the change
grep "network_mode" "$DOCKER_TOOL" && echo "Docker fix applied successfully"
```

### Step 6: Modify API Server to Support Google Backend

```bash
API_SERVER="../gpt-oss/gpt_oss/responses_api/api_server.py"

# Create backup
cp "$API_SERVER" "$API_SERVER.bak"

# Add import for GoogleBackend
# Find the line: from gpt_oss.tools.simple_browser.backend import YouComBackend, ExaBackend
# Add: from gpt_oss.tools.simple_browser.google_backend import GoogleBackend

# Find this pattern and add the import
sed -i '/from gpt_oss.tools.simple_browser.backend import YouComBackend, ExaBackend/a from gpt_oss.tools.simple_browser.google_backend import GoogleBackend' "$API_SERVER"

# Add Google backend option to the backend selection logic
# This is more complex - need to add elif clause

# Manual instruction for LLM:
# In api_server.py around line 1150-1159, modify the backend selection:
# After:
#   elif tool_backend == "exa":
#       backend = ExaBackend(source="web")
# Add:
#   elif tool_backend == "google":
#       backend = GoogleBackend(source="web")
```

**Note for LLM**: The API server modification is complex. Use the Edit tool to:
1. Read the file at line ~1150
2. Find the backend selection code block
3. Add the `elif tool_backend == "google":` clause with `GoogleBackend(source="web")`

### Step 7: Configure Credentials

```bash
cd ~/Hyperforge/gpt-oss-local-setup

# Prompt user for API keys
echo "=== API Key Configuration ==="
echo ""
echo "You need the following API keys:"
echo "1. Google Custom Search API Key"
echo "   Get from: https://console.cloud.google.com/"
echo ""
echo "2. Google Custom Search Engine ID (CX)"
echo "   Get from: https://programmablesearchengine.google.com/"
echo ""

# Create credentials.sh from template
cp credentials.template.sh credentials.sh

# Prompt for keys
read -p "Enter your Google API Key: " GOOGLE_KEY
read -p "Enter your Google CX: " GOOGLE_CX

# Update credentials.sh
sed -i "s/YOUR_GOOGLE_API_KEY_HERE/$GOOGLE_KEY/" credentials.sh
sed -i "s/YOUR_SEARCH_ENGINE_ID_HERE/$GOOGLE_CX/" credentials.sh

echo "Credentials configured!"
```

### Step 8: Create Start Script

```bash
# Create start script from template
cp start_server.template.sh start_server.sh
chmod +x start_server.sh

# Make chat client executable
chmod +x chat_client.py

echo "Scripts created and made executable"
```

### Step 9: Test Installation

```bash
# Test 1: Check Ollama
ollama ps
if [ $? -ne 0 ]; then
    echo "WARNING: Ollama might not be running"
fi

# Test 2: Check Docker
docker ps
if [ $? -ne 0 ]; then
    echo "ERROR: Docker not accessible. Run: sudo usermod -aG docker $USER"
    echo "Then log out and back in"
fi

# Test 3: Check virtual environment
source ../gpt-oss/.venv/bin/activate
python -c "import gpt_oss; import openai_harmony; print('Dependencies OK')"

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "To start the server:"
echo "  cd ~/Hyperforge/gpt-oss-local-setup"
echo "  ./start_server.sh"
echo ""
echo "To use the chat client (in a new terminal):"
echo "  cd ~/Hyperforge/gpt-oss-local-setup"
echo "  python chat_client.py"
echo ""
```

## Verification Checklist

After setup, verify:
- [ ] Ollama is installed: `ollama --version`
- [ ] Model is downloaded: `ollama list | grep gpt-oss`
- [ ] Docker is accessible: `docker ps` (without sudo)
- [ ] Virtual environment exists: `ls ~/Hyperforge/gpt-oss/.venv`
- [ ] Custom files copied: `ls ~/Hyperforge/gpt-oss/gpt_oss/tools/simple_browser/google_backend.py`
- [ ] Credentials configured: `grep -v "YOUR_" ~/Hyperforge/gpt-oss-local-setup/credentials.sh`
- [ ] Scripts are executable: `ls -l ~/Hyperforge/gpt-oss-local-setup/*.sh`

## Common Issues During Setup

### Issue 1: Docker Permission Denied
```bash
sudo usermod -aG docker $USER
# Then log out and back in
```

### Issue 2: Ollama Not Found
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Issue 3: Python Version Too Old
```bash
python --version  # Should be 3.12+
# If not, install Python 3.12 or later
```

### Issue 4: Virtual Environment Activation Fails
```bash
cd ~/Hyperforge/gpt-oss
python -m venv .venv --clear  # Recreate if corrupted
```

## Testing After Setup

Run these tests to ensure everything works:

```bash
# Terminal 1: Start server
cd ~/Hyperforge/gpt-oss-local-setup
./start_server.sh

# Terminal 2: Test with chat client
cd ~/Hyperforge/gpt-oss-local-setup

# Test 1: Basic question
python chat_client.py "What is 2+2?"

# Test 2: Web search
python chat_client.py --web "Who won the 2024 Nobel Prize in Physics?"

# Test 3: Python execution
python chat_client.py --python "Calculate the first 10 prime numbers"
```

## Cleanup After Failed Setup

If setup fails and you need to start over:

```bash
cd ~/Hyperforge
rm -rf gpt-oss  # Remove cloned repo
# Keep gpt-oss-local-setup folder
# Re-run setup from Step 3
```

## Notes for LLM Assistants

- Always create backups before modifying files
- Use `sed` carefully - verify changes with `grep` or `diff`
- Ask user for API keys - never hardcode them
- Check each step's exit code before proceeding
- Provide clear error messages with solutions
- Test modifications incrementally
