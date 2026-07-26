from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from app.constants import RELEASE_TOOL_NAME


class LLMResponseError(RuntimeError):
    """Provider returned an unsupported response."""


@dataclass(frozen=True)
class ToolResult:
    text: str
    released: bool = False


class LLMClient:
    def __init__(self, api_key: str, base_url: str, model: str):
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    def respond(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> ToolResult:
        response = self._client.chat.completions.create(model=self._model, messages=messages, tools=tools)
        try:
            choices = response.choices
            if not choices or choices[0].message is None:
                raise LLMResponseError("LLM returned no assistant message")
            message = choices[0].message
        except (IndexError, AttributeError, TypeError) as exc:
            raise LLMResponseError("LLM returned no assistant message") from exc
        released = False
        for call in message.tool_calls or []:
            name = getattr(getattr(call, "function", None), "name", None)
            if name != RELEASE_TOOL_NAME:
                raise LLMResponseError(f"Unknown tool call: {name}")
            released = True
        return ToolResult(text=message.content or "", released=released)
