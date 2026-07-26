from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = Field(min_length=1, validation_alias="OPENAI_API_KEY")
    openai_base_url: str = Field(min_length=1, validation_alias="OPENAI_BASE_URL")
    openai_model: str = Field(min_length=1, validation_alias="OPENAI_MODEL")
    service_port: int = Field(default=8000, validation_alias="SERVICE_PORT")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def load_settings() -> Settings:
    return Settings()
