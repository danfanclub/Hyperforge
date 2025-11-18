#!/bin/bash
# GPT-OSS Server Startup Script Template
#
# INSTRUCTIONS:
# 1. Copy this file: cp start_server.template.sh start_server.sh
# 2. Make it executable: chmod +x start_server.sh
# 3. Edit paths if your setup is different
# 4. Run: ./start_server.sh

# Load API credentials
# Make sure you've created credentials.sh from credentials.template.sh!
if [ -f "credentials.sh" ]; then
    source credentials.sh
else
    echo "ERROR: credentials.sh not found!"
    echo "Please create it from credentials.template.sh and add your API keys."
    exit 1
fi

# Set browser backend (options: google, youcom, exa)
export BROWSER_BACKEND="google"

# Navigate to gpt-oss directory
# Adjust this path if your setup is different
cd ../gpt-oss || {
    echo "ERROR: gpt-oss directory not found at ../gpt-oss"
    echo "Please adjust the path in this script"
    exit 1
}

# Activate virtual environment
source .venv/bin/activate

# Start the Responses API server
echo "Starting gpt-oss Responses API server..."
echo "Backend: Ollama"
echo "Model: gpt-oss:20b"
echo "Browser: $BROWSER_BACKEND"
echo "Server will run on http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python -m gpt_oss.responses_api.serve --inference-backend ollama --checkpoint "gpt-oss:20b"
