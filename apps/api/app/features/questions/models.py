from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, computed_field, field_validator


def _normalize_tags(tags: list[str] | None) -> list[str]:
    if not tags:
        return []

    normalized: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        cleaned = tag.strip().lower()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        normalized.append(cleaned)

    if len(normalized) > 2:
        raise ValueError("A maximum of 2 tags is allowed")

    return normalized


class QuestionCreate(BaseModel):
    question_text: str
    answer_text: str | None = None
    topic: str
    tags: list[str] = Field(default_factory=list)
    is_work: bool = False

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        return _normalize_tags(value)


class QuestionUpdate(BaseModel):
    question_text: str | None = None
    answer_text: str | None = None
    topic: str | None = None
    tags: list[str] | None = None
    is_work: bool | None = None

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        return _normalize_tags(value)


class Question(BaseModel):
    id: uuid.UUID
    question_text: str
    answer_text: str | None = None
    topic: str
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags_from_db(cls, value: list[str] | None) -> list[str]:
        return _normalize_tags(value)

    @computed_field(return_type=bool)
    @property
    def is_work(self) -> bool:
        return "work" in self.tags


class RefineRequest(BaseModel):
    topic: str
    question: str
    answer: str = ""


class RefineResponse(BaseModel):
    question: str
    answer: str
