"""
Backward-compatible re-exports.

All Pydantic models have moved to their respective feature packages.
Import from here only if you have an existing dependency on app.schemas;
prefer the canonical locations for new code.
"""

from app.features.questions.models import Question, QuestionCreate, QuestionUpdate
from app.features.learn.models import SubmitUnifiedAnswer, UnifiedReviewResponse
from app.features.math.models import MathQuestion, MathReview, MathTemplateInfo, SubmitMathAnswer

# SubmitAnswer and Review were defined in schemas.py but are only referenced
# internally; keep them here for any external consumers that import them.
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class SubmitAnswer(BaseModel):
    question_id: uuid.UUID
    user_answer: str


class LLMFeedback(BaseModel):
    score: int = Field(ge=1, le=5)
    verdict: str
    missing: str
    tip: str


class Review(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    user_answer: str
    llm_feedback: str
    score: int | None = None
    created_at: datetime


__all__ = [
    "Question",
    "QuestionCreate",
    "QuestionUpdate",
    "SubmitAnswer",
    "SubmitUnifiedAnswer",
    "UnifiedReviewResponse",
    "LLMFeedback",
    "Review",
    "MathTemplateInfo",
    "MathQuestion",
    "SubmitMathAnswer",
    "MathReview",
]
