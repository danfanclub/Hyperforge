#!/usr/bin/env python3
"""
GPT-OSS Terminal Chat Client

A terminal-based chat interface for gpt-oss with Ollama backend.
Automatically enables file editing and web search capabilities.

Usage:
    python gpt-oss-chat.py [options]

Prerequisites:
    1. Start Ollama: ollama run gpt-oss:20b
    2. Start Responses API server:
       cd gpt-oss
       source .venv/bin/activate
       python -m gpt_oss.responses_api.serve --inference-backend ollama --port 8000
    3. Set API keys for web search (optional):
       export EXA_API_KEY=your_key  # or YDC_API_KEY
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

import requests


class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


def print_colored(text: str, color: str = "", bold: bool = False, dim: bool = False):
    """Print colored text to terminal"""
    prefix = ""
    if bold:
        prefix += Colors.BOLD
    if dim:
        prefix += Colors.DIM
    prefix += color
    print(f"{prefix}{text}{Colors.RESET}")


def print_separator(char: str = "─", width: int = 80):
    """Print a separator line"""
    print_colored(char * width, Colors.DIM)


def print_header(text: str):
    """Print a section header"""
    print()
    print_colored(f"╭{'─' * (len(text) + 2)}╮", Colors.CYAN)
    print_colored(f"│ {text} │", Colors.CYAN, bold=True)
    print_colored(f"╰{'─' * (len(text) + 2)}╯", Colors.CYAN)


class ChatClient:
    """Terminal chat client for gpt-oss Responses API"""

    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        enable_file_editing: bool = True,
        enable_web_search: bool = True,
        max_tokens: int = 4096,
        instructions: str = None,
    ):
        self.api_url = api_url.rstrip('/')
        self.enable_file_editing = enable_file_editing
        self.enable_web_search = enable_web_search
        self.max_tokens = max_tokens
        self.custom_instructions = instructions
        self.conversation_history: List[Dict[str, Any]] = []

    def build_tools_list(self) -> List[Dict[str, str]]:
        """Build the list of enabled tools"""
        tools = []

        if self.enable_web_search:
            tools.append({"type": "web_search"})

        if self.enable_file_editing:
            tools.append({"type": "file_editing"})

        return tools

    def build_instructions(self) -> str:
        """Build system instructions"""
        instructions = []

        if self.custom_instructions:
            instructions.append(self.custom_instructions)

        cwd = os.getcwd()
        instructions.append(f"You are working in directory: {cwd}")

        capabilities = []
        if self.enable_file_editing:
            capabilities.append("edit files")
        if self.enable_web_search:
            capabilities.append("search the web")

        if capabilities:
            cap_str = " and ".join(capabilities)
            instructions.append(f"You can {cap_str} to help the user.")

        return "\n".join(instructions)

    def send_message(self, user_message: str) -> Dict[str, Any]:
        """Send a message to the API and get response"""

        # Build conversation input
        conversation_input = self.conversation_history.copy()

        # Add user message
        conversation_input.append({
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": user_message}]
        })

        # Build request payload
        payload = {
            "input": conversation_input,
            "instructions": self.build_instructions(),
            "tools": self.build_tools_list(),
            "max_output_tokens": self.max_tokens,
            "stream": False,
            "store": False,
        }

        # Send request
        try:
            response = requests.post(
                f"{self.api_url}/v1/responses",
                json=payload,
                timeout=300  # 5 minute timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            print_colored("✗ Error: Cannot connect to Responses API server", Colors.RED, bold=True)
            print_colored(f"  Make sure the server is running at {self.api_url}", Colors.YELLOW)
            print_colored("  Start it with:", Colors.YELLOW)
            print_colored("    cd gpt-oss && source .venv/bin/activate", Colors.DIM)
            print_colored("    python -m gpt_oss.responses_api.serve --inference-backend ollama", Colors.DIM)
            return None
        except requests.exceptions.Timeout:
            print_colored("✗ Error: Request timed out", Colors.RED, bold=True)
            print_colored("  The model is taking too long to respond", Colors.YELLOW)
            return None
        except requests.exceptions.HTTPError as e:
            print_colored(f"✗ Error: HTTP {response.status_code}", Colors.RED, bold=True)
            print_colored(f"  {response.text}", Colors.YELLOW)
            return None
        except Exception as e:
            print_colored(f"✗ Unexpected error: {e}", Colors.RED, bold=True)
            return None

    def display_response(self, response: Dict[str, Any]):
        """Display the API response in a nice format"""

        if not response:
            return

        output = response.get("output", [])

        for item in output:
            item_type = item.get("type")

            if item_type == "message":
                # Regular assistant message
                content = item.get("content", [])
                for content_item in content:
                    if content_item.get("type") == "output_text":
                        text = content_item.get("text", "")
                        print_colored(text, Colors.WHITE)

                        # Show citations if present
                        annotations = content_item.get("annotations", [])
                        if annotations:
                            print()
                            print_colored("Sources:", Colors.CYAN, bold=True)
                            for i, annotation in enumerate(annotations, 1):
                                url = annotation.get("url", "")
                                title = annotation.get("title", url)
                                print_colored(f"  [{i}] {title}", Colors.BLUE)
                                print_colored(f"      {url}", Colors.DIM)

            elif item_type == "reasoning":
                # Reasoning/thinking content
                content = item.get("content", [])
                if content:
                    print_colored("\n[Reasoning]", Colors.MAGENTA, dim=True)
                    for content_item in content:
                        if content_item.get("type") == "reasoning_text":
                            text = content_item.get("text", "")
                            # Show abbreviated reasoning
                            lines = text.split('\n')
                            preview = lines[0][:100]
                            if len(lines) > 1 or len(lines[0]) > 100:
                                preview += "..."
                            print_colored(f"  {preview}", Colors.MAGENTA, dim=True)

            elif item_type == "web_search_call":
                # Web search action
                action = item.get("action", {})
                action_type = action.get("type")

                if action_type == "search":
                    query = action.get("query", "")
                    print_colored(f"\n🔍 Searching: {query}", Colors.CYAN, bold=True)
                elif action_type == "open_page":
                    url = action.get("url", "")
                    print_colored(f"\n🌐 Opening: {url}", Colors.CYAN, bold=True)
                elif action_type == "find":
                    pattern = action.get("pattern", "")
                    url = action.get("url", "")
                    print_colored(f"\n🔎 Finding '{pattern}' in {url}", Colors.CYAN, bold=True)

            elif item_type == "code_interpreter_call":
                # Python code execution
                code = item.get("code", "")
                outputs = item.get("outputs", [])

                if code:
                    print_colored("\n🐍 Executing Python:", Colors.GREEN, bold=True)
                    print_colored(code, Colors.GREEN)

                if outputs:
                    print_colored("\nOutput:", Colors.GREEN, bold=True)
                    for output_item in outputs:
                        if output_item.get("type") == "logs":
                            logs = output_item.get("logs", "")
                            print_colored(logs, Colors.WHITE)

            elif item_type == "function_call":
                # Custom function call (including apply_patch)
                name = item.get("name", "")
                arguments = item.get("arguments", "")

                if name == "apply_patch":
                    print_colored("\n📝 Editing files...", Colors.YELLOW, bold=True)
                    # Try to extract file operations from patch
                    if "Add File:" in arguments:
                        files = [line.split("Add File:")[1].strip()
                                for line in arguments.split('\n')
                                if "Add File:" in line]
                        for f in files:
                            print_colored(f"  + Creating: {f}", Colors.GREEN)
                    if "Update File:" in arguments:
                        files = [line.split("Update File:")[1].strip()
                                for line in arguments.split('\n')
                                if "Update File:" in line]
                        for f in files:
                            print_colored(f"  ~ Updating: {f}", Colors.YELLOW)
                    if "Delete File:" in arguments:
                        files = [line.split("Delete File:")[1].strip()
                                for line in arguments.split('\n')
                                if "Delete File:" in line]
                        for f in files:
                            print_colored(f"  - Deleting: {f}", Colors.RED)
                else:
                    print_colored(f"\n⚡ Calling function: {name}", Colors.MAGENTA, bold=True)

        # Update conversation history with assistant's output
        self.conversation_history.extend(output)

    def run(self):
        """Run the chat loop"""

        # Print welcome message
        print_header("GPT-OSS Terminal Chat")
        print_colored("A local LLM assistant with file editing and web search", Colors.CYAN)
        print()
        print_colored(f"Working directory: {os.getcwd()}", Colors.BLUE)
        print_colored(f"API endpoint: {self.api_url}", Colors.BLUE)

        # Show enabled capabilities
        capabilities = []
        if self.enable_file_editing:
            capabilities.append("📝 File Editing")
        if self.enable_web_search:
            capabilities.append("🔍 Web Search")

        if capabilities:
            print_colored(f"Enabled tools: {', '.join(capabilities)}", Colors.GREEN)

        print()
        print_colored("Commands:", Colors.YELLOW, bold=True)
        print_colored("  /exit or /quit - Exit the chat", Colors.YELLOW)
        print_colored("  /clear - Clear conversation history", Colors.YELLOW)
        print_colored("  /history - Show conversation history", Colors.YELLOW)
        print_colored("  /help - Show this help message", Colors.YELLOW)
        print()
        print_separator()

        # Main chat loop
        while True:
            try:
                # Get user input
                print()
                user_input = input(f"{Colors.GREEN}{Colors.BOLD}You:{Colors.RESET} ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith('/'):
                    command = user_input.lower()

                    if command in ['/exit', '/quit']:
                        print_colored("\nGoodbye! 👋", Colors.CYAN, bold=True)
                        break

                    elif command == '/clear':
                        self.conversation_history.clear()
                        print_colored("\n✓ Conversation history cleared", Colors.GREEN)
                        continue

                    elif command == '/history':
                        print_header("Conversation History")
                        if not self.conversation_history:
                            print_colored("(empty)", Colors.DIM)
                        else:
                            print_colored(json.dumps(self.conversation_history, indent=2), Colors.DIM)
                        continue

                    elif command == '/help':
                        print_colored("\nCommands:", Colors.YELLOW, bold=True)
                        print_colored("  /exit, /quit - Exit the chat", Colors.YELLOW)
                        print_colored("  /clear - Clear conversation history", Colors.YELLOW)
                        print_colored("  /history - Show conversation history", Colors.YELLOW)
                        print_colored("  /help - Show this help", Colors.YELLOW)
                        continue

                    else:
                        print_colored(f"Unknown command: {user_input}", Colors.RED)
                        print_colored("Type /help for available commands", Colors.YELLOW)
                        continue

                # Add user message to history
                self.conversation_history.append({
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": user_input}]
                })

                # Send message and get response
                print()
                print_colored("Assistant:", Colors.BLUE, bold=True)
                print()

                response = self.send_message(user_input)

                if response:
                    self.display_response(response)
                else:
                    # Remove the user message from history if request failed
                    self.conversation_history.pop()

                print()
                print_separator()

            except KeyboardInterrupt:
                print()
                print_colored("\nInterrupted. Type /exit to quit or continue chatting.", Colors.YELLOW)
                continue
            except EOFError:
                print()
                print_colored("\nGoodbye! 👋", Colors.CYAN, bold=True)
                break


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="GPT-OSS Terminal Chat Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gpt-oss-chat.py
  python gpt-oss-chat.py --api-url http://localhost:8000
  python gpt-oss-chat.py --no-web-search
  python gpt-oss-chat.py --no-file-editing
        """
    )

    parser.add_argument(
        '--api-url',
        default='http://localhost:8000',
        help='URL of the Responses API server (default: http://localhost:8000)'
    )

    parser.add_argument(
        '--no-file-editing',
        action='store_true',
        help='Disable file editing capability'
    )

    parser.add_argument(
        '--no-web-search',
        action='store_true',
        help='Disable web search capability'
    )

    parser.add_argument(
        '--max-tokens',
        type=int,
        default=4096,
        help='Maximum output tokens (default: 4096)'
    )

    parser.add_argument(
        '--instructions',
        type=str,
        help='Custom system instructions'
    )

    args = parser.parse_args()

    # Create and run chat client
    client = ChatClient(
        api_url=args.api_url,
        enable_file_editing=not args.no_file_editing,
        enable_web_search=not args.no_web_search,
        max_tokens=args.max_tokens,
        instructions=args.instructions,
    )

    client.run()


if __name__ == "__main__":
    main()
