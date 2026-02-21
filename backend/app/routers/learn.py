import json
import random

from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.database import get_pool
from app.schemas import Review, SubmitAnswer, SubmitUnifiedAnswer, UnifiedReviewResponse
from app.services.llm import (
    get_feedback,
    rephrase_question,
    generate_math_word_problem,
    get_math_feedback,
)
from app.services.spaced_repetition import calculate_next_review, calculate_math_review
from app.services.math_problems import (
    MATH_TEMPLATES,
    compute_answer,
    generate_params,
    get_random_template,
    get_template,
    get_templates_by_topic,
    grade_math_answer,
)

router = APIRouter(prefix="/learn", tags=["learn"])


@router.get("/next")
async def next_question(topic: str | None = Query(None), focus: str | None = Query(None)):
    """
    Get the next question for review — randomly mixes regular Q&A and math problems.

    Uses spaced repetition to prioritize what's due, with true random interleaving
    between question types for optimal learning.
    """
    pool = await get_pool()
    work_only = (focus or "").strip().lower() == "work"
    include_math = not work_only

    # Collect candidates from both regular questions and math templates
    candidates = []

    # Check for due regular questions
    if topic and work_only:
        regular_row = await pool.fetchrow(
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
        regular_row = await pool.fetchrow(
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
        regular_row = await pool.fetchrow(
            """
            SELECT id, 'regular' as question_type, next_review_at, ease_factor
            FROM questions 
            WHERE next_review_at <= now()
            ORDER BY next_review_at ASC, ease_factor ASC
            LIMIT 1
            """
        )

    if regular_row:
        candidates.append(("regular", regular_row["id"], regular_row["next_review_at"]))

    # Check for due math templates
    if include_math:
        math_templates = (
            get_templates_by_topic(topic) if topic else list(MATH_TEMPLATES.values())
        )
        template_ids = [t.type_id for t in math_templates]

        if template_ids:
            math_row = await pool.fetchrow(
                """
                SELECT template_type, next_review_at, ease_factor
                FROM math_template_progress
                WHERE template_type = ANY($1) AND next_review_at <= now()
                ORDER BY next_review_at ASC, ease_factor ASC
                LIMIT 1
                """,
                template_ids,
            )

            if math_row:
                candidates.append(
                    ("math", math_row["template_type"], math_row["next_review_at"])
                )
            else:
                # Check for untried math templates (they're always "due")
                tried = await pool.fetch(
                    "SELECT template_type FROM math_template_progress WHERE template_type = ANY($1)",
                    template_ids,
                )
                tried_set = {r["template_type"] for r in tried}
                untried = [t for t in template_ids if t not in tried_set]
                if untried:
                    candidates.append(("math", random.choice(untried), None))
    else:
        template_ids = []

    # If nothing is due, add random candidates from both pools
    if not candidates:
        # Random regular question
        if topic and work_only:
            random_regular = await pool.fetchrow(
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
            random_regular = await pool.fetchrow(
                "SELECT id FROM questions WHERE topic = $1 ORDER BY random() LIMIT 1",
                topic,
            )
        elif work_only:
            random_regular = await pool.fetchrow(
                """
                SELECT id
                FROM questions
                WHERE 'work' = ANY(tags)
                ORDER BY random()
                LIMIT 1
                """
            )
        else:
            random_regular = await pool.fetchrow(
                "SELECT id FROM questions ORDER BY random() LIMIT 1"
            )

        if random_regular:
            candidates.append(("regular", random_regular["id"], None))

        # Random math template
        if include_math and template_ids:
            candidates.append(("math", random.choice(template_ids), None))

    if not candidates:
        raise HTTPException(404, "No questions found")

    # TRUE RANDOM SELECTION — this is the interleaving magic
    question_type, question_id, _ = random.choice(candidates)

    if question_type == "regular":
        return await _get_regular_question(pool, question_id)
    else:
        return await _generate_math_question(pool, question_id)


async def _get_regular_question(pool, question_id):
    """Fetch and format a regular question."""
    row = await pool.fetchrow("SELECT * FROM questions WHERE id = $1", question_id)

    if not row:
        raise HTTPException(404, "Question not found")

    question = dict(row)

    # Optionally rephrase
    if settings.rephrase_questions:
        question["display_text"] = await rephrase_question(question["question_text"])
    else:
        question["display_text"] = question["question_text"]

    # Don't leak the answer
    question.pop("answer_text", None)

    # Add type indicator for frontend
    question["question_type"] = "regular"

    return question


async def _generate_math_question(pool, template_type: str):
    """Generate a fresh math question from a template."""
    template = get_template(template_type)
    if not template:
        raise HTTPException(500, f"Unknown template: {template_type}")

    # Generate random parameters
    params = generate_params(template)

    # Compute the correct answer
    correct_answer = compute_answer(template, params)

    # Generate creative word problem via Gemini
    display_text = await generate_math_word_problem(
        concept=template.concept,
        params=params,
        asks_for=template.asks_for,
        example=template.example,
    )

    # Store in database
    row = await pool.fetchrow(
        """
        INSERT INTO math_questions (template_type, topic, params, correct_answer, display_text)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, template_type, topic, params, display_text, created_at
        """,
        template.type_id,
        template.topic,
        json.dumps(params),
        correct_answer,
        display_text,
    )

    return {
        "id": row["id"],
        "question_type": "math",
        "template_type": row["template_type"],
        "topic": row["topic"],
        "display_text": row["display_text"],
        "hint": template.hint,
        "created_at": row["created_at"],
        # Don't leak: params, correct_answer
    }


@router.get("/stats")
async def get_review_stats(topic: str | None = Query(None), focus: str | None = Query(None)):
    """Get spaced repetition statistics."""
    pool = await get_pool()
    work_only = (focus or "").strip().lower() == "work"

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


@router.post("/submit", response_model=UnifiedReviewResponse)
async def submit_answer(body: SubmitUnifiedAnswer):
    """
    Submit an answer for either a regular or math question.

    Automatically routes based on question_type, gets LLM feedback,
    updates spaced repetition, and stores the review.
    """
    pool = await get_pool()

    if body.question_type == "math":
        return await _submit_math_answer(pool, body)
    else:
        return await _submit_regular_answer(pool, body)


async def _submit_regular_answer(
    pool, body: SubmitUnifiedAnswer
) -> UnifiedReviewResponse:
    """Handle regular question submission."""
    # Fetch the question
    row = await pool.fetchrow("SELECT * FROM questions WHERE id = $1", body.question_id)
    if not row:
        raise HTTPException(404, "Question not found")

    question = dict(row)

    # Call the LLM for feedback
    feedback = await get_feedback(
        question_text=question["question_text"],
        user_answer=body.user_answer,
        answer_text=question.get("answer_text"),
    )

    # Calculate next review using SM-2 algorithm
    score = feedback.get("score") or 3
    sr_result = calculate_next_review(
        score=score,
        current_ease=question.get("ease_factor") or 2.5,
        current_interval=question.get("interval_days") or 0,
        review_count=question.get("review_count") or 0,
    )

    # Update spaced repetition fields
    await pool.execute(
        """
        UPDATE questions
        SET ease_factor = $2, interval_days = $3, next_review_at = $4, review_count = review_count + 1
        WHERE id = $1
        """,
        body.question_id,
        sr_result.ease_factor,
        sr_result.interval_days,
        sr_result.next_review_at,
    )

    # Store the review
    review_row = await pool.fetchrow(
        """
        INSERT INTO reviews (question_id, user_answer, llm_feedback, score)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        """,
        body.question_id,
        body.user_answer,
        feedback["raw"],
        feedback["score"],
    )

    return UnifiedReviewResponse(
        id=review_row["id"],
        question_type="regular",
        user_answer=body.user_answer,
        llm_feedback=feedback["raw"],
        score=feedback["score"],
    )


async def _submit_math_answer(pool, body: SubmitUnifiedAnswer) -> UnifiedReviewResponse:
    """Handle math question submission."""
    # Parse numeric answer
    try:
        user_answer = float(body.user_answer)
    except ValueError:
        raise HTTPException(400, "Math answers must be numeric")

    # Fetch the question
    row = await pool.fetchrow(
        "SELECT * FROM math_questions WHERE id = $1",
        body.question_id,
    )
    if not row:
        raise HTTPException(404, "Math question not found")

    template = get_template(row["template_type"])
    if not template:
        raise HTTPException(500, f"Unknown template type: {row['template_type']}")

    # Grade the answer
    grade = grade_math_answer(
        user_answer=user_answer,
        correct_answer=row["correct_answer"],
        tolerance=template.tolerance,
    )

    # Get LLM feedback
    feedback = await get_math_feedback(
        question=row["display_text"],
        concept=template.concept,
        correct_answer=row["correct_answer"],
        user_answer=user_answer,
        is_correct=grade["is_correct"],
    )

    # Update template progress for spaced repetition
    progress = await pool.fetchrow(
        "SELECT * FROM math_template_progress WHERE template_type = $1",
        row["template_type"],
    )

    if progress:
        sr_result = calculate_math_review(
            is_correct=grade["is_correct"],
            current_ease=progress["ease_factor"],
            current_interval=progress["interval_days"],
            total_attempts=progress["total_attempts"],
        )
        await pool.execute(
            """
            UPDATE math_template_progress
            SET ease_factor = $2, interval_days = $3, next_review_at = $4,
                total_attempts = total_attempts + 1, correct_attempts = correct_attempts + $5
            WHERE template_type = $1
            """,
            row["template_type"],
            sr_result.ease_factor,
            sr_result.interval_days,
            sr_result.next_review_at,
            1 if grade["is_correct"] else 0,
        )
    else:
        sr_result = calculate_math_review(
            is_correct=grade["is_correct"],
            current_ease=2.5,
            current_interval=0,
            total_attempts=0,
        )
        await pool.execute(
            """
            INSERT INTO math_template_progress 
            (template_type, ease_factor, interval_days, next_review_at, total_attempts, correct_attempts)
            VALUES ($1, $2, $3, $4, 1, $5)
            """,
            row["template_type"],
            sr_result.ease_factor,
            sr_result.interval_days,
            sr_result.next_review_at,
            1 if grade["is_correct"] else 0,
        )

    # Store the review
    review_row = await pool.fetchrow(
        """
        INSERT INTO math_reviews (math_question_id, user_answer, is_correct, llm_feedback)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        """,
        body.question_id,
        user_answer,
        grade["is_correct"],
        feedback,
    )

    return UnifiedReviewResponse(
        id=review_row["id"],
        question_type="math",
        user_answer=body.user_answer,
        llm_feedback=feedback,
        is_correct=grade["is_correct"],
        correct_answer=row["correct_answer"],
    )
