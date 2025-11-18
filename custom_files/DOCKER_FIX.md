# Docker Networking Fix for Python Tool

## Issue
On some systems, Docker fails to create bridge networks with error:
```
failed to add the host (veth...) <=> sandbox (veth...) pair interfaces: operation not supported
```

## Solution
Add `network_mode="host"` to container creation in `gpt_oss/tools/python_docker/docker_tool.py`

## File to Modify
`gpt-oss/gpt_oss/tools/python_docker/docker_tool.py`

## Change Required

**Find this code (around line 65-67):**
```python
# 2. Start the container
container = _docker_client.containers.create(
    "python:3.11", command="sleep infinity", detach=True
)
```

**Replace with:**
```python
# 2. Start the container
container = _docker_client.containers.create(
    "python:3.11", command="sleep infinity", detach=True, network_mode="host"
)
```

## Automated Application

If using the setup script, this patch is automatically applied.

Manual application:
```bash
cd gpt-oss/gpt_oss/tools/python_docker
# Make backup
cp docker_tool.py docker_tool.py.bak

# Apply the change (one line modification at line 66)
# Add: network_mode="host" as parameter to containers.create()
```

## Why This Works

Host networking bypasses Docker's bridge network creation, which fails on some kernel configurations. The container still runs isolated but shares the host's network stack.

## Trade-offs

- **Pro**: Works on systems where bridge networking fails
- **Pro**: Slightly better performance (no NAT overhead)
- **Con**: Less network isolation (acceptable for local development)
- **Con**: Container can access host network services
