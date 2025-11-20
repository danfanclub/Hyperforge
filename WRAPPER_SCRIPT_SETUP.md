# Wrapper Script Setup

This document explains how to set up the `gpt-oss-chat` command to work from any directory.

## Quick Setup

Copy the wrapper script to your local bin directory:

```bash
cp wrapper-script.sh ~/.local/bin/gpt-oss-chat
chmod +x ~/.local/bin/gpt-oss-chat
```

Then reload your shell configuration:

```bash
source ~/.bashrc  # or ~/.zshrc if using zsh
```

Now you can run `gpt-oss-chat` from any directory!

## Manual Setup

If you prefer to create the wrapper manually:

1. Create the wrapper script:

```bash
nano ~/.local/bin/gpt-oss-chat
```

2. Add this content:

```bash
#!/usr/bin/env bash
# Wrapper script to run gpt-oss-chat from anywhere using the correct Python environment

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
```

3. Make it executable:

```bash
chmod +x ~/.local/bin/gpt-oss-chat
```

4. Ensure `~/.local/bin` is in your PATH:

```bash
# Add to ~/.bashrc if not already present
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Usage

Once set up, you can use the chat client from any directory:

```bash
cd ~/Documents/my-project
gpt-oss-chat
```

The model will be able to create/edit files in whatever directory you're currently in.

## Customization

You can pass arguments to the chat client through the wrapper:

```bash
gpt-oss-chat --no-web-search        # Disable web search
gpt-oss-chat --no-file-editing      # Disable file editing
gpt-oss-chat --api-url http://localhost:8080  # Use custom API URL
```

See `gpt-oss-chat.py --help` for all available options.

## Troubleshooting

### Command not found

Make sure `~/.local/bin` is in your PATH:

```bash
echo $PATH | grep -q ".local/bin" && echo "PATH OK" || echo "PATH needs configuration"
```

If PATH needs configuration:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### ModuleNotFoundError: No module named 'requests'

This means the wrapper is using the wrong Python. Make sure the `VENV_PYTHON` path in the wrapper script points to your gpt-oss virtual environment:

```bash
# Check if the path exists
ls -la /home/merlin/Hyperforge/gpt-oss/.venv/bin/python
```

### Permission denied

Make sure the wrapper script is executable:

```bash
chmod +x ~/.local/bin/gpt-oss-chat
```
