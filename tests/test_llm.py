import pytest

from app.llm import LLMClient, LLMResponseError


class FakeCompletions:
    def create(self, **kwargs):
        return type("Response", (), {"choices": None})()


class FakeClient:
    def __init__(self):
        self.chat = type("Chat", (), {"completions": FakeCompletions()})()


def test_llm_rejects_missing_choices(monkeypatch):
    monkeypatch.setattr("app.llm.OpenAI", lambda **kwargs: FakeClient())
    client = LLMClient("key", "https://example.test/v1", "model")

    with pytest.raises(LLMResponseError, match="no assistant message"):
        client.respond([], [])
