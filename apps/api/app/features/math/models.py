from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


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
