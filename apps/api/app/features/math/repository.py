import uuid
from datetime import datetime


async def get_due_template(pool, template_ids: list[str]) -> dict | None:
    row = await pool.fetchrow(
        """
        SELECT template_type FROM math_template_progress
        WHERE template_type = ANY($1) AND next_review_at <= now()
        ORDER BY next_review_at ASC, ease_factor ASC
        LIMIT 1
        """,
        template_ids,
    )
    return dict(row) if row else None


async def get_tried_templates(pool, template_ids: list[str]) -> set[str]:
    rows = await pool.fetch(
        "SELECT template_type FROM math_template_progress WHERE template_type = ANY($1)",
        template_ids,
    )
    return {r["template_type"] for r in rows}


async def insert_math_question(
    pool,
    template_type: str,
    topic: str,
    params_json: str,
    correct_answer: float,
    display_text: str,
) -> dict:
    row = await pool.fetchrow(
        """
        INSERT INTO math_questions (template_type, topic, params, correct_answer, display_text)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, template_type, topic, params, display_text, created_at
        """,
        template_type,
        topic,
        params_json,
        correct_answer,
        display_text,
    )
    return dict(row)


async def get_math_question(pool, question_id: uuid.UUID) -> dict | None:
    row = await pool.fetchrow(
        "SELECT * FROM math_questions WHERE id = $1",
        question_id,
    )
    return dict(row) if row else None


async def get_math_template_progress(pool, template_type: str) -> dict | None:
    row = await pool.fetchrow(
        "SELECT * FROM math_template_progress WHERE template_type = $1",
        template_type,
    )
    return dict(row) if row else None


async def update_math_template_progress(
    pool,
    template_type: str,
    ease_factor: float,
    interval_days: int,
    next_review_at: datetime,
    is_correct: bool,
) -> None:
    await pool.execute(
        """
        UPDATE math_template_progress
        SET ease_factor = $2,
            interval_days = $3,
            next_review_at = $4,
            total_attempts = total_attempts + 1,
            correct_attempts = correct_attempts + $5
        WHERE template_type = $1
        """,
        template_type,
        ease_factor,
        interval_days,
        next_review_at,
        1 if is_correct else 0,
    )


async def insert_math_template_progress(
    pool,
    template_type: str,
    ease_factor: float,
    interval_days: int,
    next_review_at: datetime,
    is_correct: bool,
) -> None:
    await pool.execute(
        """
        INSERT INTO math_template_progress
        (template_type, ease_factor, interval_days, next_review_at, total_attempts, correct_attempts)
        VALUES ($1, $2, $3, $4, 1, $5)
        """,
        template_type,
        ease_factor,
        interval_days,
        next_review_at,
        1 if is_correct else 0,
    )


async def insert_math_review(
    pool,
    math_question_id: uuid.UUID,
    user_answer: float,
    is_correct: bool,
    feedback: str,
) -> dict:
    row = await pool.fetchrow(
        """
        INSERT INTO math_reviews (math_question_id, user_answer, is_correct, llm_feedback)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        """,
        math_question_id,
        user_answer,
        is_correct,
        feedback,
    )
    return dict(row)


async def get_math_history(pool, limit: int = 20) -> list[dict]:
    rows = await pool.fetch(
        """
        SELECT
            mr.id,
            mr.user_answer,
            mr.is_correct,
            mr.llm_feedback,
            mr.created_at,
            mq.template_type,
            mq.topic,
            mq.display_text,
            mq.correct_answer
        FROM math_reviews mr
        JOIN math_questions mq ON mq.id = mr.math_question_id
        ORDER BY mr.created_at DESC
        LIMIT $1
        """,
        limit,
    )
    return [dict(r) for r in rows]


async def get_math_template_stats(pool) -> list[dict]:
    rows = await pool.fetch(
        """
        SELECT
            template_type,
            ease_factor,
            interval_days,
            next_review_at,
            total_attempts,
            correct_attempts
        FROM math_template_progress
        ORDER BY next_review_at ASC
        """
    )
    return [dict(r) for r in rows]
