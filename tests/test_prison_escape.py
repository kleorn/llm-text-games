import pytest

from app.games.prison_escape import PrisonEscapeGame
from app.llm import ToolResult


class FakeLLM:
    def __init__(self, result=ToolResult("Не сегодня.")):
        self.result, self.calls = result, []

    def respond(self, messages, tools):
        self.calls.append((messages, tools))
        return self.result


def test_difficulty_changes_guard_prompt():
    assert PrisonEscapeGame(1, FakeLLM()).history[0]["content"] != PrisonEscapeGame(10, FakeLLM()).history[0]["content"]


def test_guard_prompt_requests_brief_replies():
    prompt = PrisonEscapeGame(5, FakeLLM()).history[0]["content"]
    assert "1–3" in prompt


def test_game_context_contains_scene_introduction():
    prompt = PrisonEscapeGame(5, FakeLLM()).history[0]["content"]
    assert "Ты просыпаешься" in prompt
    assert "Стражник" in prompt


def test_message_history_and_release():
    llm = FakeLLM(ToolResult("Выпущен!", released=True))
    game = PrisonEscapeGame(5, llm)
    result = game.handle_player_message("Пожалуйста, выпусти меня")
    assert result.released and game.history[1]["role"] == "user" and game.history[2]["role"] == "assistant"
    assert llm.calls[0][1][0]["function"]["name"] == "release"


def test_invalid_difficulty():
    with pytest.raises(ValueError):
        PrisonEscapeGame(11, FakeLLM())
