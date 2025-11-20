"""Apply Patch Tool for Responses API Server

This tool wraps the apply_patch module to enable file editing capabilities
in the Responses API server.
"""

from pathlib import Path
from typing import AsyncIterator

from openai_harmony import (
    Author,
    Content,
    Message,
    Role,
    TextContent,
    ToolDescription,
)

from . import apply_patch
from .tool import Tool


class ApplyPatchTool(Tool):
    """Tool for creating, updating, and deleting files using patch format."""

    def __init__(self, name: str = "apply_patch"):
        self._name = name

    @classmethod
    def get_tool_name(cls) -> str:
        return "apply_patch"

    @property
    def name(self) -> str:
        return self._name

    @property
    def instruction(self) -> str:
        """Return the instruction text from apply_patch.md"""
        instruction_file = Path(apply_patch.__file__).parent / "apply_patch.md"
        return instruction_file.read_text()

    @property
    def tool_config(self) -> ToolDescription:
        """Return tool configuration for Harmony format"""
        return ToolDescription.new(
            self._name,
            "Patch a file. Use this to create, update, or delete files.",
            parameters={
                "type": "string",
                "description": "Formatted patch code",
                "default": "*** Begin Patch\n*** End Patch\n",
            },
        )

    def _make_response(
        self,
        output: str,
        channel: str | None = None,
    ) -> Message:
        """Create a response message from tool output"""
        content = TextContent(text=output)
        return self.make_response(content=content, channel=channel)

    def make_response(
        self,
        content: Content,
        *,
        channel: str | None = None,
    ) -> Message:
        """Create a properly formatted response message"""
        tool_name = self.get_tool_name()
        author = Author(role=Role.TOOL, name=f"{tool_name}")

        message = Message(
            author=author,
            content=[content],
        ).with_recipient("assistant")

        if channel:
            message = message.with_channel(channel)

        return message

    async def _process(self, message: Message) -> AsyncIterator[Message]:
        """Process the patch from the model and apply it to the filesystem"""
        patch_text = message.content[0].text
        channel = message.channel

        # Handle potential JSON wrapper (similar to chat.py implementation)
        if patch_text.startswith("{"):
            import json
            try:
                some_dict = json.loads(patch_text)
                _, patch_text = some_dict.popitem()
            except Exception as e:
                error_msg = f"Error parsing JSON: {e}"
                yield self._make_response(error_msg, channel=channel)
                return

        # Apply the patch
        try:
            result = apply_patch.apply_patch(patch_text)
            yield self._make_response(result, channel=channel)
        except Exception as e:
            error_msg = f"Error applying patch: {e}"
            yield self._make_response(error_msg, channel=channel)
