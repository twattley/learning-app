import uuid
from datetime import datetime


async def get_next_regular_question(
    pool,
    topic: str | None = None,
    work_only: bool = False,
) -> dict | None:
    """Return the most overdue regular question, or None if nothing is due."""
    if topic and work_only:
        row = await pool.fetchrow(
            """
            SELECT id, 'regular' as question_type, next_review_at, ease_factor
            FROM questions
            WHERE topic = $1
              AND 'work' = ANY(tags)
              AND next_review_at <= now()
            ORDER BY next_review_at ASC, ease_factor ASC
            LIMIT 1
            """,
            topic,
        )
    elif topic:
        row = await pool.fetchrow(
            """
            SELECT id, 'regular' as question_type, next_review_at, ease_factor
            FROM questions
            WHERE topic = $1 AND next_review_at <= now()
            ORDER BY next_review_at ASC, ease_factor ASC
            LIMIT 1
            """,
            topic,
        )
    else:
        row = await pool.fetchrow(
            """
            SELECT id, 'regular' as question_type, next_review_at, ease_factor
            FROM questions
            WHERE next_review_at <= now()
            ORDER BY next_review_at ASC, ease_factor ASC
            LIMIT 1
            """
        )
    return dict(row) if row else None


async def get_random_regular_question(
    pool,
    topic: str | None = None,
    work_only: bool = False,
) -> dict | None:
    """Return a random regular question regardless of due date."""
    if topic and work_only:
        row = await pool.fetchrow(
            """
            SELECT id
            FROM questions
            WHERE topic = $1
              AND 'work' = ANY(tags)
            ORDER BY random()
            LIMIT 1
            """,
            topic,
        )
    elif topic:
        row = await pool.fetchrow(
            "SELECT id FROM questions WHERE topic = $1 ORDER BY random() LIMIT 1",
            topic,
        )
    elif work_only:
        row = await pool.fetchrow(
            """
            SELECT id
            FROM questions
            WHERE 'work' = ANY(tags)
            ORDER BY random()
            LIMIT 1
            """
        )
    else:
        row = await pool.fetchrow(
            "SELECT id FROM questions ORDER BY random() LIMIT 1"
        )
    return dict(row) if row else None


async def get_question_for_review(pool, question_id: uuid.UUID) -> dict | None:
    """Fetch a full question row by id."""
    row = await pool.fetchrow("SELECT * FROM questions WHERE id = $1", question_id)
    return dict(row) if row else None


async def update_question_sr(
    pool,
    question_id: uuid.UUID,
    ease_factor: float,
    interval_days: int,
    next_review_at: datetime,
) -> None:
    await pool.execute(
        """
        UPDATE questions
        SET ease_factor = $2, interval_days = $3, next_review_at = $4,
            review_count = review_count + 1
        WHERE id = $1
        """,
        question_id,
        ease_factor,
        interval_days,
        next_review_at,
    )


async def insert_review(
    pool,
    question_id: uuid.UUID,
    user_answer: str,
    llm_feedback: str,
    score: int,
) -> dict:
    row = await pool.fetchrow(
        """
        INSERT INTO reviews (question_id, user_answer, llm_feedback, score)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        """,
        question_id,
        user_answer,
        llm_feedback,
        score,
    )
    return dict(row)


async def get_math_template_progress(pool, template_ids: list[str]) -> list[dict]:
    rows = await pool.fetch(
        """
        SELECT template_type, next_review_at, ease_factor
        FROM math_template_progress
        WHERE template_type = ANY($1) AND next_review_at <= now()
        ORDER BY next_review_at ASC, ease_factor ASC
        LIMIT 1
        """,
        template_ids,
    )
    return [dict(r) for r in rows]


async def get_due_math_template(pool, template_ids: list[str]) -> dict | None:
    row = await pool.fetchrow(
        """
        SELECT template_type, next_review_at, ease_factor
        FROM math_template_progress
        WHERE template_type = ANY($1) AND next_review_at <= now()
        ORDER BY next_review_at ASC, ease_factor ASC
        LIMIT 1
        """,
        template_ids,
    )
    return dict(row) if row else None


async def get_tried_math_templates(pool, template_ids: list[str]) -> set[str]:
    rows = await pool.fetch(
        "SELECT template_type FROM math_template_progress WHERE template_type = ANY($1)",
        template_ids,
    )
    return {r["template_type"] for r in rows}


async def get_math_question(pool, question_id: uuid.UUID) -> dict | None:
    row = await pool.fetchrow(
        "SELECT * FROM math_questions WHERE id = $1",
        question_id,
    )
    return dict(row) if row else None


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


async def upsert_math_template_progress(
    pool,
    template_type: str,
    ease_factor: float,
    interval_days: int,
    next_review_at: datetime,
    is_correct: bool,
) -> None:
    existing = await pool.fetchrow(
        "SELECT * FROM math_template_progress WHERE template_type = $1",
        template_type,
    )
    if existing:
        await pool.execute(
            """
            UPDATE math_template_progress
            SET ease_factor = $2, interval_days = $3, next_review_at = $4,
                total_attempts = total_attempts + 1, correct_attempts = correct_attempts + $5
            WHERE template_type = $1
            """,
            template_type,
            ease_factor,
            interval_days,
            next_review_at,
            1 if is_correct else 0,
        )
    else:
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


async def get_review_stats(
    pool,
    topic: str | None = None,
    work_only: bool = False,
) -> dict:
    if topic and work_only:
        stats = await pool.fetchrow(
            """
            SELECT
                COUNT(*) as total_questions,
                COUNT(*) FILTER (WHERE next_review_at <= now()) as due_now,
                COUNT(*) FILTER (WHERE next_review_at > now() AND next_review_at <= now() + interval '1 day') as due_today,
                COUNT(*) FILTER (WHERE review_count = 0) as never_reviewed,
                AVG(ease_factor) as avg_ease_factor
            FROM questions
            WHERE topic = $1
              AND 'work' = ANY(tags)
            """,
            topic,
        )
    elif topic:
        stats = await pool.fetchrow(
            """
            SELECT
                COUNT(*) as total_questions,
                COUNT(*) FILTER (WHERE next_review_at <= now()) as due_now,
                COUNT(*) FILTER (WHERE next_review_at > now() AND next_review_at <= now() + interval '1 day') as due_today,
                COUNT(*) FILTER (WHERE review_count = 0) as never_reviewed,
                AVG(ease_factor) as avg_ease_factor
            FROM questions
            WHERE topic = $1
            """,
            topic,
        )
    elif work_only:
        stats = await pool.fetchrow(
            """
            SELECT
                COUNT(*) as total_questions,
                COUNT(*) FILTER (WHERE next_review_at <= now()) as due_now,
                COUNT(*) FILTER (WHERE next_review_at > now() AND next_review_at <= now() + interval '1 day') as due_today,
                COUNT(*) FILTER (WHERE review_count = 0) as never_reviewed,
                AVG(ease_factor) as avg_ease_factor
            FROM questions
            WHERE 'work' = ANY(tags)
            """
        )
    else:
        stats = await pool.fetchrow(
            """
            SELECT
                COUNT(*) as total_questions,
                COUNT(*) FILTER (WHERE next_review_at <= now()) as due_now,
                COUNT(*) FILTER (WHERE next_review_at > now() AND next_review_at <= now() + interval '1 day') as due_today,
                COUNT(*) FILTER (WHERE review_count = 0) as never_reviewed,
                AVG(ease_factor) as avg_ease_factor
            FROM questions
            """
        )
    return dict(stats)
