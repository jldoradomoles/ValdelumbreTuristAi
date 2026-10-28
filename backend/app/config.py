from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    LLM_PROVIDER: str = "fallback"
    DATA_PATH: Path = Path(__file__).resolve().parent.parent.parent / "references" / "datos" / "pois.json"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:4200"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
