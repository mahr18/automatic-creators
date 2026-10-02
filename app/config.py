from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-luna"
    openai_strategy_model: str = "gpt-5.6-terra"
    openai_critic_model: str = "gpt-5.6-luna"
    youtube_api_key: str | None = None
    gemini_api_key: str | None = None
    host: str = "0.0.0.0"
    port: int = 8000
    database_path: str = "data/brain.sqlite3"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_file(self) -> Path:
        path = Path(self.database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
