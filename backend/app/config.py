from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings

_env_file = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    database_url: str = "postgresql://localhost:5432/recall"
    rephrase_questions: bool = False

    # LLM provider: "gemini", "openai", or "ollama"
    llm_provider: Literal["gemini", "openai", "ollama"] = "gemini"

    # Gemini (cloud — default)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # Ollama (local)
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "llama3"

    model_config = {"env_prefix": "RECALL_", "env_file": str(_env_file)}


settings = Settings()
