from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests
from ddgs import DDGS
import json

# Load environment variables
load_dotenv()

app = FastAPI()

# Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "GPT-oss:20B") # Default to the model the user is running
WEB_SEARCH_API_KEY = os.getenv("WEB_SEARCH_API_KEY") # Not directly used by googlesearch-python, but good practice for other APIs

class QueryRequest(BaseModel):
    prompt: str
    context: dict = {} # For passing context from client (e.g., file content, tool output)
    history: list = [] # To maintain conversation history

class ToolCall(BaseModel):
    tool: str
    args: dict

class AgentResponse(BaseModel):
    response: str = None
    tool_call: ToolCall = None
    error: str = None
    tool_output_needed: bool = False # Indicates if the server is waiting for tool output from client

# --- Available Tools ---
AVAILABLE_TOOLS = {
    "web_search": {
        "description": "Performs a web search to get up-to-date information. Use this for questions requiring external knowledge or current events.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."}
            },
            "required": ["query"]
        }
    },
    "read_file": {
        "description": "Reads the content of a local file on the client machine. Use this when the user refers to a local file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The absolute or relative path to the file on the client machine."}
            },
            "required": ["path"]
        }
    },
    "write_file": {
        "description": "Writes content to a local file on the client machine. Use this when the user asks to save information to a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The absolute or relative path to the file on the client machine."},
                "content": {"type": "string", "description": "The content to write to the file."}
            },
            "required": ["path", "content"]
        }
    },
    "list_directory": {
        "description": "Lists the contents of a directory on the client machine.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The absolute or relative path to the directory on the client machine. Defaults to the current directory."}
            },
            "required": []
        }
    }
}

# --- Helper Functions ---

async def perform_web_search(query: str) -> str:
    """Performs a web search using DuckDuckGo and returns a summary of results."""
    search_results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                search_results.append(r['body'])
        print(f"--- Web Search Results ---\n{search_results}\n--------------------------")
    except Exception as e:
        print(f"Error during ddgs search: {e}")
        return f"Error performing web search: {e}"

    if not search_results:
        return "No relevant web search results found."

    return "Web Search Results:\n" + "\n".join(search_results)

async def call_ollama(user_prompt: str, system_prompt: str = None, model: str = OLLAMA_MODEL) -> str:
    """Calls the Ollama API to get a response from the configured model using the /api/generate endpoint."""
    url = f"{OLLAMA_HOST}/api/generate" # Use /api/generate
    headers = {"Content-Type": "application/json"}

    # Combine system and user prompts for the /api/generate endpoint
    full_prompt = user_prompt
    if system_prompt:
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

    data = {
        "model": model,
        "prompt": full_prompt, # Use "prompt" instead of "messages"
        "stream": False
    }
    if system_prompt:
        data["system"] = system_prompt

    print(f"Calling Ollama with model: {model}")
    print(f"System Prompt (truncated): {system_prompt[:200]}..." if system_prompt else "(no system prompt)")
    print(f"User Prompt (truncated): {user_prompt[:200]}...")

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    result = response.json()
    return result["response"] # The response key is different for /api/generate

def parse_ollama_response_for_tool_call(llm_output: str) -> tuple[ToolCall | None, str | None]:
    """
    Parses the LLM's output to check for a structured tool call.
    Expected format:
    <tool_code>
    {"tool": "tool_name", "args": {"arg1": "value1"}}
    </tool_code>
    """
    tool_call_start = llm_output.find("<tool_code>")
    tool_call_end = llm_output.find("</tool_code>")

    if tool_call_start != -1 and tool_call_end != -1:
        tool_json_str = llm_output[tool_call_start + len("<tool_code>"):tool_call_end].strip()
        try:
            tool_data = json.loads(tool_json_str)
            tool_call = ToolCall(tool=tool_data["tool"], args=tool_data["args"])
            # The remaining text might be a thought process before the tool call
            remaining_text = llm_output[:tool_call_start].strip() + llm_output[tool_call_end + len("</tool_code>"):].strip()
            return tool_call, remaining_text
        except json.JSONDecodeError:
            print(f"Warning: LLM output contained <tool_code> but JSON was invalid: {tool_json_str}")
            return None, llm_output
    return None, llm_output

# --- Main Agent Logic ---

@app.post("/query", response_model=AgentResponse)
async def query_agent(request: QueryRequest):
    user_prompt = request.prompt
    context = request.context
    
    # Simplified system prompt
    system_prompt = """You are a helpful AI assistant. You have access to the following tools:

- **web_search(query):** Performs a web search.
- **read_file(path):** Reads the content of a local file.
- **write_file(path, content):** Writes content to a local file.
- **list_directory(path):** Lists the contents of a directory. If no path is provided, it lists the contents of the current directory.

To use a tool, respond with a JSON object inside <tool_code> tags. For example:
<tool_code>
{"tool": "list_directory", "args": {"path": "."}}
</tool_code>

If the user asks to summarize a folder, you MUST use the `list_directory` tool to see the contents of the folder. If they do not provide a path, assume they mean the current directory and use `list_directory` with `path` set to `.`

If you can answer without a tool, provide a direct response.
"""

    # Keyword-based tool triggers
    if "summarize" in user_prompt.lower() and ("folder" in user_prompt.lower() or "directory" in user_prompt.lower()):
        return AgentResponse(tool_call=ToolCall(tool="list_directory", args={"path": "."}))
    
    search_keywords = ["weather", "latest", "current", "news", "what is", "who is", "define"]
    if any(keyword in user_prompt.lower() for keyword in search_keywords):
        return AgentResponse(tool_call=ToolCall(tool="web_search", args={"query": user_prompt}))

    # If no keywords, proceed with a direct LLM call after adding context
    if context:
        for key, value in context.items():
            user_prompt += f"\n\n--- Context from Client ({key}) ---\n{value}"
            
    llm_response_content = await call_ollama(user_prompt=user_prompt, system_prompt=system_prompt)
    print(f"--- Raw LLM Response ---\n{llm_response_content}\n--------------------------")
    
    # Parse the response for a tool call
    tool_call, remaining_text = parse_ollama_response_for_tool_call(llm_response_content)

    if tool_call:
        return AgentResponse(tool_call=tool_call)
    else:
        return AgentResponse(response=remaining_text or llm_response_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

