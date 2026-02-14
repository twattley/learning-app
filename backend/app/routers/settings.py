from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings, get_llm_provider, set_llm_provider

router = APIRouter(prefix="/settings", tags=["settings"])


class LLMMode(BaseModel):
    mode: str  # "local" or "web"
    provider: str  # "ollama" or "gemini"
    model: str


class SetLLMMode(BaseModel):
    mode: str  # "local" or "web"


def _provider_for_mode(mode: str) -> str:
    return "ollama" if mode == "local" else "gemini"


def _mode_for_provider(provider: str) -> str:
    return "local" if provider == "ollama" else "web"


@router.get("/llm-mode")
async def get_llm_mode() -> LLMMode:
    """Get the current LLM mode."""
    provider = get_llm_provider()
    mode = _mode_for_provider(provider)
    model = settings.ollama_model if provider == "ollama" else settings.gemini_model
    return LLMMode(mode=mode, provider=provider, model=model)


@router.put("/llm-mode")
async def update_llm_mode(body: SetLLMMode) -> LLMMode:
    """Switch between local (Ollama) and web (Gemini) LLM mode."""
    provider = _provider_for_mode(body.mode)
    set_llm_provider(provider)
    model = settings.ollama_model if provider == "ollama" else settings.gemini_model
    print(f"[Settings] LLM mode switched to: {body.mode} ({provider}, {model})")
    return LLMMode(mode=body.mode, provider=provider, model=model)
