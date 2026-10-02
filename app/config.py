import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str | None = None
    openai_research_model: str = "gpt-6-luna"
    openai_strategy_model: str = "gpt-6.1-sol"
    openai_prompt_model: str = "gpt-6-luna"
    openai_critic_model: str = "gpt-6.1-sol"
    openai_repair_model: str = "gpt-6.1-sol"
    youtube_api_key: str | None = None
    gemini_api_key: str | None = None
    brain_access_token: str | None = None
    host: str = "0.0.0.0"
    port: int = 10000
    database_path: str = "data/brain.sqlite3"
    output_dir: str = "data/outputs"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_file(self) -> Path:
        path = Path(self.database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def output_directory(self) -> Path:
        path = Path(self.output_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()

# The Agents SDK resolves the OpenAI credential from OPENAI_API_KEY.
# Feed it from pydantic-settings/.env only on the server; never expose it to the browser.
if settings.openai_api_key:
    os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)
