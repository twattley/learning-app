from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

_env_file = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    database_url: str = Field(
        validation_alias=AliasChoices("DATABASE_URL", "RECALL_DATABASE_URL")
    )
    api_port: int = Field(default=8003, validation_alias=AliasChoices("API_PORT", "RECALL_API_PORT"))
    rephrase_questions: bool = Field(
        default=False,
        validation_alias=AliasChoices("REPHRASE_QUESTIONS", "RECALL_REPHRASE_QUESTIONS"),
    )

    # LLM provider: "gemini", "openai", or "ollama"
    llm_provider: Literal["gemini", "openai", "ollama"] = Field(
        default="gemini",
        validation_alias=AliasChoices("LLM_PROVIDER", "RECALL_LLM_PROVIDER"),
    )

    # Gemini (cloud — default)
    gemini_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GEMINI_API_KEY", "RECALL_GEMINI_API_KEY"),
    )
    gemini_model: str = Field(
        default="gemini-2.0-flash",
        validation_alias=AliasChoices("GEMINI_MODEL", "RECALL_GEMINI_MODEL"),
    )

    # Ollama (local)
    ollama_base_url: str = Field(
        default="http://localhost:11434/v1",
        validation_alias=AliasChoices("OLLAMA_BASE_URL", "RECALL_OLLAMA_BASE_URL"),
    )
    ollama_model: str = Field(
        default="gemma3:12b",
        validation_alias=AliasChoices("OLLAMA_MODEL", "RECALL_OLLAMA_MODEL"),
    )

    model_config = SettingsConfigDict(env_file=str(_env_file), extra="ignore")


settings = Settings()


# Runtime override for LLM provider (allows switching without restart)
_runtime_llm_provider: str | None = None


def get_llm_provider() -> str:
    """Return the active LLM provider, respecting runtime overrides."""
    if _runtime_llm_provider is not None:
        return _runtime_llm_provider
    return settings.llm_provider


def set_llm_provider(provider: str) -> None:
    """Set the LLM provider at runtime (does not persist across restarts)."""
    global _runtime_llm_provider
    _runtime_llm_provider = provider
