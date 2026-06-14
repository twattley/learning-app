import uuid


async def create_question(
    pool,
    question_text: str,
    answer_text: str | None,
    topic: str,
    tags: list[str],
) -> dict:
    row = await pool.fetchrow(
        """
        INSERT INTO questions (question_text, answer_text, topic, tags)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        """,
        question_text,
        answer_text,
        topic,
        tags,
    )
    return dict(row)


async def list_questions(
    pool,
    topic: str | None = None,
    work_only: bool = False,
) -> list[dict]:
    if topic and work_only:
        rows = await pool.fetch(
            """
            SELECT *
            FROM questions
            WHERE topic = $1
              AND 'work' = ANY(tags)
            ORDER BY created_at DESC
            """,
            topic,
        )
    elif topic:
        rows = await pool.fetch(
            "SELECT * FROM questions WHERE topic = $1 ORDER BY created_at DESC",
            topic,
        )
    elif work_only:
        rows = await pool.fetch(
            """
            SELECT *
            FROM questions
            WHERE 'work' = ANY(tags)
            ORDER BY created_at DESC
            """
        )
    else:
        rows = await pool.fetch("SELECT * FROM questions ORDER BY created_at DESC")

    return [dict(r) for r in rows]


async def get_question(pool, question_id: uuid.UUID) -> dict | None:
    row = await pool.fetchrow("SELECT * FROM questions WHERE id = $1", question_id)
    return dict(row) if row else None


async def update_question(
    pool,
    question_id: uuid.UUID,
    question_text: str | None = None,
    answer_text: str | None = None,
    topic: str | None = None,
    tags: list[str] | None = None,
) -> dict | None:
    row = await pool.fetchrow(
        """
        UPDATE questions
        SET question_text = COALESCE($2, question_text),
            answer_text   = COALESCE($3, answer_text),
            topic         = COALESCE($4, topic),
            tags          = COALESCE($5, tags),
            updated_at    = now()
        WHERE id = $1
        RETURNING *
        """,
        question_id,
        question_text,
        answer_text,
        topic,
        tags,
    )
    return dict(row) if row else None


async def delete_question(pool, question_id: uuid.UUID) -> bool:
    """Returns True if a row was deleted, False if the id was not found."""
    result = await pool.execute("DELETE FROM questions WHERE id = $1", question_id)
    return result != "DELETE 0"
