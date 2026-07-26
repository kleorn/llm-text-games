from app.cli import run
from app.config import Settings
from app.llm import ToolResult
from openai import OpenAIError


class FakeLLM:
    def __init__(self, *_args):
        pass

    def respond(self, messages, tools):
        return ToolResult("Свободен.", released=True)


def test_cli_returns_success_on_release(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _prompt: next(iter(["1", "Я невиновен"])))
    settings = Settings(OPENAI_API_KEY="key", OPENAI_BASE_URL="https://example.test/v1", OPENAI_MODEL="model")
    assert run(settings, FakeLLM) == 0
    output = capsys.readouterr().out
    assert "Стражник:" in output
    assert "Поздравляем" in output


class ProviderError(OpenAIError):
    pass


def test_cli_hides_provider_error(monkeypatch, capsys):
    values = iter(["1", "Попытка"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(values))

    class FailingLLM:
        def __init__(self, *_args):
            pass

        def respond(self, messages, tools):
            raise ProviderError("access denied")

    settings = Settings(OPENAI_API_KEY="key", OPENAI_BASE_URL="https://example.test/v1", OPENAI_MODEL="model")
    assert run(settings, FailingLLM) == 1
    output = capsys.readouterr().out
    assert "Ошибка игры" in output
    assert "Traceback" not in output
