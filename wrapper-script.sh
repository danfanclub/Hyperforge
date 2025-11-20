#!/usr/bin/env bash
# Wrapper script to run gpt-oss-chat from anywhere using the correct Python environment
#
# Installation:
#   cp wrapper-script.sh ~/.local/bin/gpt-oss-chat
#   chmod +x ~/.local/bin/gpt-oss-chat
#
# Usage:
#   cd ~/your-project
#   gpt-oss-chat

# Use the Python from gpt-oss virtual environment
VENV_PYTHON="/home/merlin/Hyperforge/gpt-oss/.venv/bin/python"
SCRIPT_PATH="/home/merlin/Hyperforge/gpt-oss-local-setup/gpt-oss-chat.py"

if [ -f "$VENV_PYTHON" ]; then
    exec "$VENV_PYTHON" "$SCRIPT_PATH" "$@"
else
    echo "Error: gpt-oss virtual environment not found at $VENV_PYTHON"
    echo "Please ensure the virtual environment is set up correctly."
    exit 1
fi
