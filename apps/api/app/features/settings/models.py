from pydantic import BaseModel


class LLMMode(BaseModel):
    mode: str  # "local" or "web"
    provider: str  # "ollama" or "gemini"
    model: str


class SetLLMMode(BaseModel):
    mode: str  # "local" or "web"
