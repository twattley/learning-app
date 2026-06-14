from __future__ import annotations

import uuid

from pydantic import BaseModel


class SubmitUnifiedAnswer(BaseModel):
    """Unified answer submission for both regular and math questions."""

    question_id: uuid.UUID
    question_type: str  # "regular" or "math"
    user_answer: str  # Text for regular, numeric string for math


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
