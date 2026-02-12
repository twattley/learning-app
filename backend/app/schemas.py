from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── Questions ──


class QuestionCreate(BaseModel):
    question_text: str
    answer_text: str | None = None
    topic: str


class QuestionUpdate(BaseModel):
    question_text: str | None = None
    answer_text: str | None = None
    topic: str | None = None


class Question(BaseModel):
    id: uuid.UUID
    question_text: str
    answer_text: str | None = None
    topic: str
    created_at: datetime
    updated_at: datetime


# ── Reviews ──


class SubmitAnswer(BaseModel):
    question_id: uuid.UUID
    user_answer: str


class SubmitUnifiedAnswer(BaseModel):
    """Unified answer submission for both regular and math questions."""
    question_id: uuid.UUID
    question_type: str  # "regular" or "math"
    user_answer: str  # Text for regular, numeric string for math


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


# ── Math Questions ──


class MathTemplateInfo(BaseModel):
    """Info about an available math template."""
    type_id: str
    topic: str
    concept: str
    asks_for: str


class MathQuestion(BaseModel):
    """A generated math question."""
    id: uuid.UUID
    template_type: str
    topic: str
    params: dict
    display_text: str  # The word problem
    created_at: datetime
    # Note: correct_answer is NOT included — don't leak it to the client!


class SubmitMathAnswer(BaseModel):
    math_question_id: uuid.UUID
    user_answer: float


class MathReview(BaseModel):
    id: uuid.UUID
    math_question_id: uuid.UUID
    user_answer: float
    is_correct: bool
    correct_answer: float  # Revealed after submission
    llm_feedback: str | None = None
    created_at: datetime


class UnifiedReviewResponse(BaseModel):
    """Unified response for both regular and math submissions."""
    id: uuid.UUID
    question_type: str  # "regular" or "math"
    user_answer: str
    llm_feedback: str
    # For regular questions
    score: int | None = None
    # For math questions
    is_correct: bool | None = None
    correct_answer: float | None = None
