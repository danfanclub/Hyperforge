# Code Modifications Documentation

This document describes all modifications made to the official gpt-oss codebase to enable local deployment with Google Custom Search and fix compatibility issues.

## Summary of Changes

1. **Added Google Custom Search Backend** - New browser tool backend
2. **Fixed Docker Networking Issue** - Host network mode for Python execution
3. **Integrated Google Backend** - Modified API server to support Google

## Detailed Modifications

### 1. Google Custom Search Backend

**File Created**: `gpt_oss/tools/simple_browser/google_backend.py`

**Purpose**: Provide web search capability using Google Custom Search API instead of You.com or Exa.

**Key Features**:
- Uses Google Custom Search API (100 free searches/day)
- Returns search results in same format as other backends
- Fetches webpage content for further analysis
- Compatible with existing SimpleBrowserTool interface

**API Requirements**:
- `GOOGLE_KEY` environment variable - Google API key
- `GOOGLE_CX` environment variable - Custom Search Engine ID

**Code Location**: `custom_files/google_backend.py`

---

### 2. Docker Networking Fix

**File Modified**: `gpt_oss/tools/python_docker/docker_tool.py`

**Line**: ~66

**Change**:
```python
# Before:
container = _docker_client.containers.create(
    "python:3.11", command="sleep infinity", detach=True
)

# After:
container = _docker_client.containers.create(
    "python:3.11", command="sleep infinity", detach=True, network_mode="host"
)
```

**Why**:
On some Linux systems (particularly ArchLinux), Docker fails to create bridge networks due to kernel veth interface issues. Using host networking bypasses this problem while maintaining container isolation for code execution.

**Trade-offs**:
- ✅ Works on systems with veth issues
- ✅ Better performance (no NAT)
- ⚠️ Less network isolation (acceptable for local use)

**Detailed Documentation**: `custom_files/DOCKER_FIX.md`

---

### 3. API Server Integration

**File Modified**: `gpt_oss/responses_api/api_server.py`

**Changes**:

#### A. Import GoogleBackend (around line 26)

```python
# Before:
from gpt_oss.tools.simple_browser.backend import YouComBackend, ExaBackend

# After:
from gpt_oss.tools.simple_browser.backend import YouComBackend, ExaBackend
from gpt_oss.tools.simple_browser.google_backend import GoogleBackend
```

#### B. Add Google Backend Option (around line 1156)

```python
# Before:
if use_browser_tool:
    tool_backend = os.getenv("BROWSER_BACKEND", "exa")
    if tool_backend == "youcom":
        backend = YouComBackend(source="web")
    elif tool_backend == "exa":
        backend = ExaBackend(source="web")
    else:
        raise ValueError(f"Invalid tool backend: {tool_backend}")
    browser_tool = SimpleBrowserTool(backend=backend)

# After:
if use_browser_tool:
    tool_backend = os.getenv("BROWSER_BACKEND", "exa")
    if tool_backend == "youcom":
        backend = YouComBackend(source="web")
    elif tool_backend == "exa":
        backend = ExaBackend(source="web")
    elif tool_backend == "google":
        backend = GoogleBackend(source="web")
    else:
        raise ValueError(f"Invalid tool_backend: {tool_backend}")
    browser_tool = SimpleBrowserTool(backend=backend)
```

**Purpose**: Allow selection of Google backend via `BROWSER_BACKEND=google` environment variable.

---

## Environment Variables

The following environment variables control the setup:

| Variable | Purpose | Required | Example |
|----------|---------|----------|---------|
| `BROWSER_BACKEND` | Select web search backend | Yes | `google`, `youcom`, or `exa` |
| `GOOGLE_KEY` | Google API key | If using Google | `AIzaSy...` |
| `GOOGLE_CX` | Google Custom Search Engine ID | If using Google | `d5a6b0d48...` |
| `YDC_API_KEY` | You.com API key | If using You.com | `ydc-sk-...` |
| `EXA_API_KEY` | Exa API key | If using Exa | `exa-...` |

## Files Not Modified

The following official gpt-oss files remain unchanged:
- All model inference code (`torch/`, `triton/`, `metal/`, `vllm/`)
- Core Harmony format handling
- Other tool implementations (python tool core logic, except networking fix)
- Ollama inference backend
- Test files

## Compatibility

These modifications are compatible with:
- gpt-oss v0.0.8 (latest as of Nov 2024)
- Python 3.12+
- Ollama latest
- Docker latest

## Upgrade Path

When upgrading gpt-oss:

1. **Safe to update**: Model files, inference backends (no modifications made)
2. **Check before updating**:
   - `api_server.py` - May need to reapply Google backend integration
   - `docker_tool.py` - May need to reapply networking fix
3. **Always safe**: `google_backend.py` is a new file, won't be overwritten

## Testing Modifications

After applying modifications, test:

1. **Google Search**:
```bash
curl -X POST http://127.0.0.1:8000/v1/responses \
  -H "Content-Type: application/json" \
  -d '{"input": "Search test", "tools": [{"type": "web_search"}]}'
```

2. **Python Execution**:
```bash
curl -X POST http://127.0.0.1:8000/v1/responses \
  -H "Content-Type: application/json" \
  -d '{"input": "Calculate 2+2", "tools": [{"type": "code_interpreter"}]}'
```

## Rollback Procedure

If modifications cause issues:

```bash
cd gpt-oss

# Restore original files from backups
cp gpt_oss/responses_api/api_server.py.bak gpt_oss/responses_api/api_server.py
cp gpt_oss/tools/python_docker/docker_tool.py.bak gpt_oss/tools/python_docker/docker_tool.py

# Remove Google backend
rm gpt_oss/tools/simple_browser/google_backend.py

# Use original backends (You.com or Exa)
export BROWSER_BACKEND="exa"
```

### 4. File Editing Tool (apply_patch)

**Files Created**:
- `gpt_oss/tools/apply_patch_tool.py`

**Files Modified**:
- `gpt_oss/responses_api/types.py`
- `gpt_oss/responses_api/api_server.py`

**Purpose**: Enable the model to create, update, and delete files using a structured patch format.

**Key Features**:
- Create new files with `*** Add File:`
- Update existing files with hunks (`*** Update File:`)
- Delete files with `*** Delete File:`
- Rename files with `*** Move to:`
- Works through Responses API
- No additional dependencies required

**Usage**:
```python
{
    "input": "Create a README.md file",
    "tools": [{"type": "file_editing"}],  # or "apply_patch"
    "max_output_tokens": 4096
}
```

**Code Location**: `custom_files/apply_patch_tool.py`

**Documentation**: `custom_files/FILE_EDITING_INTEGRATION.md`

**Changes Required**:

1. **types.py** - Add `FileEditingToolConfig` class and include in Union type
2. **api_server.py** - Multiple changes:
   - Import `ApplyPatchTool`
   - Update `is_not_builtin_tool()` function
   - Add tool detection and initialization
   - Add tool execution in streaming loop
   - Add instructions and tool config to developer message

**Installation**:
```bash
cp custom_files/apply_patch_tool.py gpt-oss/gpt_oss/tools/
# Then apply api_server.py and types.py changes per FILE_EDITING_INTEGRATION.md
```

---

## Future Enhancements

Potential improvements to consider:

1. **Caching**: Add request caching to Google backend to reduce API calls
2. **Rate Limiting**: Implement smart rate limiting for Google's 100/day quota
3. **Fallback**: Auto-switch to alternative backend if quota exceeded
4. **Enhanced Scraping**: Use Selenium for JavaScript-heavy sites
5. **Local Model for Query Refinement**: Replace OpenAI dependency in llmsearch with local gpt-oss
6. **File Operation Safety**: Add path validation and sandboxing for apply_patch tool
7. **Interactive Chat Client**: Enhanced terminal UI with better tool visualization
