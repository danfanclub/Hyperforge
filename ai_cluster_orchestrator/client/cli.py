import requests
import argparse
import json
import os

# Configuration for the server
SERVER_URL = "http://127.0.0.1:8000" # Default to localhost, can be changed to Titan's IP

def send_query(prompt: str, context: dict = None, history: list = None):
    """Sends a query to the FastAPI server."""
    url = f"{SERVER_URL}/query"
    payload = {"prompt": prompt}
    if context:
        payload["context"] = context
    if history:
        payload["history"] = history

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to the server at {SERVER_URL}.")
        print("Please ensure the FastAPI server is running.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error during request to server: {e}")
        return None

def process_prompt(current_prompt, tool_output_context, conversation_history):
    while True:
        # Send query with current prompt, any tool output, and history
        response_data = send_query(current_prompt, context=tool_output_context, history=conversation_history)
        tool_output_context = {} # Clear tool output context after sending

        if not response_data:
            print("No response from Orchestrator. Exiting.")
            break

        # Add user's prompt to history
        conversation_history.append({"role": "user", "content": current_prompt})

        if response_data.get("error"):
            print(f"Orchestrator Error: {response_data['error']}")
            break

        if response_data.get("response"):
            print(f"\n--- Orchestrator Response ---")
            print(f"{response_data['response']}")
            conversation_history.append({"role": "assistant", "content": response_data['response']})
            return # Return to the main loop in interactive mode

        if response_data.get("tool_call"):
            tool_call = response_data["tool_call"]
            print(f"\n--- Orchestrator requested tool ---")
            print(f"Tool: {tool_call['tool']} with args: {tool_call['args']}")

            # --- Execute local tool call ---
            tool_output = None
            if tool_call["tool"] == "read_file":
                file_path = tool_call["args"].get("path")
                if file_path:
                    try:
                        abs_path = os.path.expanduser(file_path)
                        with open(abs_path, "r") as f:
                            tool_output = f.read()
                        print(f"Successfully read file: {abs_path}")
                    except FileNotFoundError:
                        tool_output = f"Error: File not found at {abs_path}"
                    except Exception as e:
                        tool_output = f"Error reading file {abs_path}: {e}"
                else:
                    tool_output = "Error: 'path' argument missing for read_file tool."
            elif tool_call["tool"] == "list_directory":
                path = tool_call["args"].get("path", ".")
                try:
                    abs_path = os.path.expanduser(path)
                    files = os.listdir(abs_path)
                    tool_output = f"Directory listing for {abs_path}:\n" + "\n".join(files)
                except FileNotFoundError:
                    tool_output = f"Error: Directory not found at {abs_path}"
                except Exception as e:
                    tool_output = f"Error listing directory {abs_path}: {e}"
            elif tool_call["tool"] == "write_file":
                file_path = tool_call["args"].get("path")
                content = tool_call["args"].get("content")
                if file_path and content is not None:
                    try:
                        abs_path = os.path.expanduser(file_path)
                        with open(abs_path, "w") as f:
                            f.write(content)
                        tool_output = f"Successfully wrote to file: {abs_path}"
                    except Exception as e:
                        tool_output = f"Error writing to file {abs_path}: {e}"
                else:
                    tool_output = "Error: 'path' or 'content' argument missing for write_file tool."
            else:
                tool_output = f"Error: Unknown tool '{tool_call['tool']}' requested."

            print(f"Tool Output:\n{tool_output}")
            
            # Prepare for next turn: send tool output back to server
            current_prompt = f"Tool '{tool_call['tool']}' executed. Output: {tool_output}"
            tool_output_context = {"tool_output": tool_output}
            conversation_history.append({"role": "assistant", "content": f"Tool call: {tool_call['tool']} executed. Output sent to orchestrator."})
            # Loop continues to send this back to the server
        else:
            print("Orchestrator did not provide a response or tool call. Exiting.")
            break

def main():
    parser = argparse.ArgumentParser(description="Interact with the AI Cluster Orchestrator.")
    parser.add_argument("prompt", type=str, nargs='?', default=None, help="The prompt to send to the AI agent.")
    parser.add_argument("--context-file", type=str, help="Path to a file to be passed as context to the agent.")
    args = parser.parse_args()

    conversation_history = []
    tool_output_context = {} # To pass tool output back to the server

    # Read context file if provided
    if args.context_file:
        try:
            with open(args.context_file, 'r') as f:
                tool_output_context['gemini_md_content'] = f.read()
        except FileNotFoundError:
            print(f"Error: Context file not found at {args.context_file}")
            return
        except Exception as e:
            print(f"Error reading context file: {e}")
            return

    if args.prompt:
        # Single-shot mode
        process_prompt(args.prompt, tool_output_context, conversation_history)
    else:
        # Interactive chat mode
        print("Entering interactive chat mode. Type 'exit' or 'quit' to end the session.")
        while True:
            try:
                current_prompt = input("You: ")
                if current_prompt.lower() in ["exit", "quit"]:
                    break
                process_prompt(current_prompt, tool_output_context, conversation_history)
            except KeyboardInterrupt:
                print("\nExiting chat mode.")
                break
            except EOFError:
                print("\nExiting chat mode.")
                break

if __name__ == "__main__":
    main()

