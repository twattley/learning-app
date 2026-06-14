import uuid

from fastapi import APIRouter, HTTPException, Query

from app.database import get_pool
from app.features.questions.models import (
    Question,
    QuestionCreate,
    QuestionUpdate,
    RefineRequest,
    RefineResponse,
)
from app.features.questions import repository
from app.services.llm import refine_qa

router = APIRouter(prefix="/questions", tags=["questions"])


def _resolve_tags(tags: list[str] | None, is_work: bool | None) -> list[str] | None:
    if tags is None:
        if is_work is None:
            return None
        return ["work"] if is_work else []

    resolved = list(tags)
    if is_work is True and "work" not in resolved:
        resolved.insert(0, "work")
    elif is_work is False:
        resolved = [tag for tag in resolved if tag != "work"]

    return resolved


@router.post("/refine", response_model=RefineResponse)
async def refine_question(body: RefineRequest):
    """Use Gemini to polish and improve a question/answer pair."""
    result = await refine_qa(
        topic=body.topic,
        question=body.question,
        answer=body.answer,
    )
    return RefineResponse(question=result["question"], answer=result["answer"])


@router.post("", response_model=Question, status_code=201)
async def create_question(body: QuestionCreate):
    pool = await get_pool()
    tags = _resolve_tags(body.tags, body.is_work) or []
    row = await repository.create_question(
        pool,
        question_text=body.question_text,
        answer_text=body.answer_text,
        topic=body.topic,
        tags=tags,
    )
    return row


@router.get("", response_model=list[Question])
async def list_questions(topic: str | None = Query(None), focus: str | None = Query(None)):
    pool = await get_pool()
    work_only = (focus or "").strip().lower() == "work"
    rows = await repository.list_questions(pool, topic=topic, work_only=work_only)
    return rows


@router.get("/{question_id}", response_model=Question)
async def get_question(question_id: uuid.UUID):
    pool = await get_pool()
    row = await repository.get_question(pool, question_id)
    if not row:
        raise HTTPException(404, "Question not found")
    return row


@router.put("/{question_id}", response_model=Question)
async def update_question(question_id: uuid.UUID, body: QuestionUpdate):
    pool = await get_pool()

    existing = await repository.get_question(pool, question_id)
    if not existing:
        raise HTTPException(404, "Question not found")

    tags = _resolve_tags(body.tags, body.is_work)

    row = await repository.update_question(
        pool,
        question_id=question_id,
        question_text=body.question_text,
        answer_text=body.answer_text,
        topic=body.topic,
        tags=tags,
    )
    return row


@router.delete("/{question_id}", status_code=204)
async def delete_question(question_id: uuid.UUID):
    pool = await get_pool()
    deleted = await repository.delete_question(pool, question_id)
    if not deleted:
        raise HTTPException(404, "Question not found")
