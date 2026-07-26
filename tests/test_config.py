import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_load_environment(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("OPENAI_MODEL", "model")

    settings = Settings()

    assert settings.openai_api_key == "key"
    assert settings.openai_base_url == "https://example.test/v1"
    assert settings.service_port == 8000


def test_settings_require_llm_values(monkeypatch):
    for name in ("OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL"):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_reject_empty_llm_values():
    with pytest.raises(ValidationError):
        Settings(OPENAI_API_KEY="", OPENAI_BASE_URL="", OPENAI_MODEL="")
