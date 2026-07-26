from typing import Any

from app.constants import RELEASE_TOOL, guard_system_prompt
from app.games.base import LLMResponder
from app.llm import ToolResult


class PrisonEscapeGame:
    def __init__(self, difficulty: int, llm: LLMResponder):
        if difficulty not in range(1, 11):
            raise ValueError("difficulty must be between 1 and 10")
        self.history: list[dict[str, Any]] = [{"role": "system", "content": guard_system_prompt(difficulty)}]
        self._llm = llm

    def handle_player_message(self, text: str) -> ToolResult:
        if not text.strip():
            raise ValueError("message cannot be empty")
        self.history.append({"role": "user", "content": text})
        result = self._llm.respond(self.history, [RELEASE_TOOL])
        if result.text:
            self.history.append({"role": "assistant", "content": result.text})
        return result
