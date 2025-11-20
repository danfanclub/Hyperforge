# File Editing (apply_patch) Tool Integration

This document describes the changes needed to add file editing capabilities to gpt-oss via the apply_patch tool.

## Summary

The apply_patch tool enables the model to create, update, and delete files in the local filesystem using a structured patch format. This integration adds three main components:

1. **ApplyPatchTool class** - Tool implementation for the Responses API
2. **Type definitions** - Request validation for file_editing tool type
3. **API server integration** - Tool detection and execution logic

## Files Added

### 1. apply_patch_tool.py

**Location**: `gpt_oss/tools/apply_patch_tool.py`

**Source**: `custom_files/apply_patch_tool.py`

**Purpose**: Wraps the existing `apply_patch` module to integrate with the Responses API.

**Copy command**:
```bash
cp custom_files/apply_patch_tool.py gpt-oss/gpt_oss/tools/
```

## Files Modified

### 2. types.py - Add FileEditingToolConfig

**File**: `gpt_oss/responses_api/types.py`

**Change 1** - Add new tool config class (after CodeInterpreterToolConfig, around line 150):

```python
class FileEditingToolConfig(BaseModel):
    type: Literal["file_editing"] | Literal["apply_patch"]
```

**Change 2** - Add to Union type (around line 178):

```python
# Before:
tools: Optional[
    list[
        Union[FunctionToolDefinition, BrowserToolConfig, CodeInterpreterToolConfig]
    ]
] = []

# After:
tools: Optional[
    list[
        Union[FunctionToolDefinition, BrowserToolConfig, CodeInterpreterToolConfig, FileEditingToolConfig]
    ]
] = []
```

### 3. api_server.py - Integrate apply_patch tool

**File**: `gpt_oss/responses_api/api_server.py`

**Change 1** - Add import (around line 28):

```python
from gpt_oss.tools.apply_patch_tool import ApplyPatchTool
```

**Change 2** - Update is_not_builtin_tool function (around line 90):

```python
def is_not_builtin_tool(
    recipient: str,
    treat_functions_python_as_builtin: bool = False,
    treat_functions_apply_patch_as_builtin: bool = False
) -> bool:
    if treat_functions_python_as_builtin and recipient == "functions.python":
        return False
    if treat_functions_apply_patch_as_builtin and recipient == "functions.apply_patch":
        return False
    return (
        not recipient.startswith("browser.")
        and recipient != "python"
        and recipient != "apply_patch"
        and recipient != "assistant"
    )
```

**Change 3** - Update generate_response signature (around line 125):

Add these parameters:
```python
apply_patch_tool: Optional[ApplyPatchTool] = None,
treat_functions_apply_patch_as_builtin: bool = False,
```

**Change 4** - Update is_not_builtin_tool calls (around line 176):

```python
if len(recipient) > 0 and is_not_builtin_tool(
    recipient, treat_functions_python_as_builtin, treat_functions_apply_patch_as_builtin
):
```

**Change 5** - Update StreamResponsesEvents.__init__ (around line 416):

Add these parameters:
```python
apply_patch_tool: Optional[ApplyPatchTool] = None,
functions_apply_patch_as_builtin: bool = False,
```

And in the body:
```python
self.apply_patch_tool = apply_patch_tool
self.use_apply_patch = apply_patch_tool is not None
self.functions_apply_patch_as_builtin = functions_apply_patch_as_builtin
```

**Change 6** - Add tool execution in run() method (after python tool execution, around line 1112):

```python
elif (
    self.use_apply_patch
    and last_message.recipient is not None
    and (
        last_message.recipient.startswith("apply_patch")
        or (
            self.functions_apply_patch_as_builtin
            and last_message.recipient == "functions.apply_patch"
        )
    )
):
    # Handle apply_patch tool
    async def run_apply_patch_tool():
        results = []
        async for msg in self.apply_patch_tool.process(last_message):
            results.append(msg)
        return results

    result = await run_apply_patch_tool()
    print(result)

    # Feed the results back into the conversation
    new_tokens = encoding.render_conversation_for_completion(
        Conversation.from_messages(result), Role.ASSISTANT
    )

    print(encoding.decode_utf8(new_tokens))
    self.output_tokens.append(next_tok)
    self.tokens.append(
        encoding.encode("<|end|>", allowed_special="all")[0]
    )

    for token in new_tokens:
        self.parser.process(token)
        self.output_tokens.append(token)
        self.tokens.append(token)

    current_output_index += 1
    self.new_request = True

    continue
```

**Change 7** - Update both generate_response calls to include apply_patch params:

First call (around line 522):
```python
apply_patch_tool=self.apply_patch_tool,
treat_functions_apply_patch_as_builtin=self.functions_apply_patch_as_builtin,
```

Second call (around line 1180):
```python
apply_patch_tool=self.apply_patch_tool,
treat_functions_apply_patch_as_builtin=self.functions_apply_patch_as_builtin,
```

**Change 8** - Detect and initialize tool in /v1/responses endpoint (around line 1228):

```python
use_apply_patch = any(
    getattr(tool, "type", None) in ("file_editing", "apply_patch")
    for tool in (body.tools or [])
)

if use_apply_patch:
    apply_patch_tool = ApplyPatchTool()
else:
    apply_patch_tool = None

# ... (after python_function_name_conflict check)

apply_patch_function_name_conflict = any(
    getattr(tool, "type", None) == "function"
    and getattr(tool, "name", None) == "apply_patch"
    for tool in (body.tools or [])
)
functions_apply_patch_as_builtin = use_apply_patch and not (
    apply_patch_function_name_conflict
)
```

**Change 9** - Add instructions and tool config (around line 1316):

```python
# Build instructions with apply_patch if enabled
instructions = body.instructions or ""
if use_apply_patch:
    if instructions:
        instructions += "\n"
    instructions += apply_patch_tool.instruction

developer_message_content = DeveloperContent.new().with_instructions(
    instructions
)

# ... (in tools list building)

# Add apply_patch tool if enabled
if use_apply_patch:
    tools.append(apply_patch_tool.tool_config)
```

**Change 10** - Pass to StreamResponsesEvents (around line 1432):

```python
apply_patch_tool=apply_patch_tool,
functions_apply_patch_as_builtin=functions_apply_patch_as_builtin,
```

## Usage

Once integrated, enable file editing in API requests:

```python
{
    "input": "Create a hello.py file",
    "tools": [{"type": "file_editing"}],  # or "apply_patch"
    "max_output_tokens": 4096
}
```

The model will use the patch format to create/edit/delete files:

```
*** Begin Patch
*** Add File: hello.py
+print("Hello, World!")
*** End Patch
```

## Testing

Test the integration:

```bash
cd gpt-oss
source .venv/bin/activate

# Start server with Ollama backend
python -m gpt_oss.responses_api.serve \
    --inference-backend ollama \
    --checkpoint gpt-oss:20b \
    --port 8000

# Test with API call
curl -X POST http://localhost:8000/v1/responses \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Create a test.txt file with hello world",
    "tools": [{"type": "file_editing"}],
    "max_output_tokens": 2048,
    "stream": false
  }'
```

## Compatibility

- **gpt-oss version**: Works with main branch (tested Nov 2024)
- **Python**: 3.12+
- **Dependencies**: Uses existing `apply_patch` module, no additional deps

## Security Considerations

The apply_patch tool can modify any file the server process has write access to. For production use:

1. Run the server with limited filesystem permissions
2. Use a dedicated user account with restricted access
3. Consider sandboxing or containerization
4. Monitor file operations
5. Implement file path allowlisting if needed

## Patch Format Reference

See `gpt_oss/tools/apply_patch.md` for full patch format specification.

Quick reference:
- `*** Add File: <path>` - Create new file (all lines prefixed with +)
- `*** Update File: <path>` - Modify existing file with hunks
- `*** Delete File: <path>` - Remove file
- `*** Move to: <new_path>` - Rename file (after Update)
