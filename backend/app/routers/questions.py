import uuid

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.database import get_pool
from app.schemas import Question, QuestionCreate, QuestionUpdate
from app.services.llm import refine_qa

router = APIRouter(prefix="/questions", tags=["questions"])


class RefineRequest(BaseModel):
    topic: str
    question: str
    answer: str = ""


class RefineResponse(BaseModel):
    question: str
    answer: str


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
    row = await pool.fetchrow(
        """
        INSERT INTO questions (question_text, answer_text, topic)
        VALUES ($1, $2, $3)
        RETURNING *
        """,
        body.question_text,
        body.answer_text,
        body.topic,
    )
    return dict(row)


@router.get("", response_model=list[Question])
async def list_questions(topic: str | None = Query(None)):
    pool = await get_pool()
    if topic:
        rows = await pool.fetch(
            "SELECT * FROM questions WHERE topic = $1 ORDER BY created_at DESC",
            topic,
        )
    else:
        rows = await pool.fetch("SELECT * FROM questions ORDER BY created_at DESC")
    return [dict(r) for r in rows]


@router.get("/{question_id}", response_model=Question)
async def get_question(question_id: uuid.UUID):
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM questions WHERE id = $1", question_id)
    if not row:
        raise HTTPException(404, "Question not found")
    return dict(row)


@router.put("/{question_id}", response_model=Question)
async def update_question(question_id: uuid.UUID, body: QuestionUpdate):
    pool = await get_pool()

    existing = await pool.fetchrow("SELECT * FROM questions WHERE id = $1", question_id)
    if not existing:
        raise HTTPException(404, "Question not found")

    row = await pool.fetchrow(
        """
        UPDATE questions
        SET question_text = COALESCE($2, question_text),
            answer_text   = COALESCE($3, answer_text),
            topic         = COALESCE($4, topic),
            updated_at    = now()
        WHERE id = $1
        RETURNING *
        """,
        question_id,
        body.question_text,
        body.answer_text,
        body.topic,
    )
    return dict(row)


@router.delete("/{question_id}", status_code=204)
async def delete_question(question_id: uuid.UUID):
    pool = await get_pool()
    result = await pool.execute("DELETE FROM questions WHERE id = $1", question_id)
    if result == "DELETE 0":
        raise HTTPException(404, "Question not found")
