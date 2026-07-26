from typing import Any, Protocol

from app.llm import ToolResult


class LLMResponder(Protocol):
    def respond(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> ToolResult: ...
