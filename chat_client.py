#!/usr/bin/env python3
"""
Simple interactive chat client for gpt-oss Responses API

Usage:
  python chat_client.py                           # Interactive mode
  python chat_client.py "Your question here"      # Single question
  python chat_client.py --web "Search question"   # With web search
  python chat_client.py --python "Code question"  # With Python execution

Note: Requires 'requests' package. Install with: pip install requests
Or run from gpt-oss virtual environment: source ../gpt-oss/.venv/bin/activate
"""

import requests
import json
import sys

API_URL = "http://127.0.0.1:8000/v1/responses"

def chat(message, use_web_search=False, use_python=False, reasoning_effort="low"):
    """Send a message to gpt-oss and get a response."""

    # Build tools list
    tools = []
    if use_web_search:
        tools.append({"type": "web_search"})
    if use_python:
        tools.append({"type": "code_interpreter"})

    payload = {
        "input": message,
        "reasoning": {"effort": reasoning_effort},
        "stream": False
    }

    if tools:
        payload["tools"] = tools

    print(f"\n🤖 Thinking...\n")

    try:
        response = requests.post(API_URL, json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()

        # Extract and display the response
        output = data.get("output", [])

        # Show reasoning (optional - uncomment to see chain of thought)
        # for item in output:
        #     if item.get("type") == "reasoning":
        #         for content in item.get("content", []):
        #             print(f"💭 Reasoning: {content.get('text', '')}")

        # Show web searches
        for item in output:
            if item.get("type") == "web_search_call":
                action = item.get("action", {})
                if action.get("type") == "search":
                    print(f"🔍 Searched: {action.get('query')}")
                elif action.get("type") == "open_page":
                    print(f"📄 Opened: {action.get('url')}")

        # Show code execution
        for item in output:
            if item.get("type") == "code_interpreter_call":
                code = item.get("code", "")
                if code:
                    print(f"\n💻 Executed Python:\n{code}\n")
                outputs = item.get("outputs", [])
                for out in outputs:
                    if out.get("type") == "logs":
                        print(f"Output: {out.get('logs')}")

        # Show final response
        for item in output:
            if item.get("type") == "message" and item.get("role") == "assistant":
                content = item.get("content", [])
                for c in content:
                    if c.get("type") == "output_text":
                        print(f"\n✨ Response:\n{c.get('text')}\n")

                        # Show citations
                        annotations = c.get("annotations", [])
                        if annotations:
                            print("\n📚 Sources:")
                            for ann in annotations:
                                if ann.get("type") == "url_citation":
                                    print(f"  - {ann.get('title')}: {ann.get('url')}")

        # Show token usage
        usage = data.get("usage", {})
        if usage:
            print(f"\n📊 Tokens: {usage.get('input_tokens')} in / {usage.get('output_tokens')} out")

        return data

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return None


def interactive_mode():
    """Run interactive chat mode."""
    print("=" * 60)
    print("🚀 gpt-oss Interactive Chat")
    print("=" * 60)
    print("\nCommands:")
    print("  /web     - Enable web search for next message")
    print("  /python  - Enable Python code execution for next message")
    print("  /both    - Enable both web search and Python")
    print("  /high    - Set reasoning effort to high")
    print("  /medium  - Set reasoning effort to medium")
    print("  /low     - Set reasoning effort to low (default)")
    print("  /quit    - Exit")
    print("\n" + "=" * 60 + "\n")

    use_web = False
    use_py = False
    effort = "low"

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                cmd = user_input.lower()
                if cmd == "/quit":
                    print("👋 Goodbye!")
                    break
                elif cmd == "/web":
                    use_web = True
                    print("🔍 Web search enabled for next message")
                    continue
                elif cmd == "/python":
                    use_py = True
                    print("💻 Python execution enabled for next message")
                    continue
                elif cmd == "/both":
                    use_web = True
                    use_py = True
                    print("🔍💻 Web search and Python enabled for next message")
                    continue
                elif cmd == "/high":
                    effort = "high"
                    print("🧠 Reasoning effort set to HIGH")
                    continue
                elif cmd == "/medium":
                    effort = "medium"
                    print("🧠 Reasoning effort set to MEDIUM")
                    continue
                elif cmd == "/low":
                    effort = "low"
                    print("🧠 Reasoning effort set to LOW")
                    continue
                else:
                    print(f"❓ Unknown command: {user_input}")
                    continue

            # Send message
            chat(user_input, use_web_search=use_web, use_python=use_py, reasoning_effort=effort)

            # Reset tool flags after use
            use_web = False
            use_py = False

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Command line mode
        message = " ".join(sys.argv[1:])

        # Check for flags
        use_web = "--web" in sys.argv
        use_py = "--python" in sys.argv

        # Remove flags from message
        message = message.replace("--web", "").replace("--python", "").strip()

        chat(message, use_web_search=use_web, use_python=use_py)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
