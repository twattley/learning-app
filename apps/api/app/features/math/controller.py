"""
Math learning endpoints.

Generates dynamic math problems using templates + LLM word problem generation.
Uses spaced repetition at the template level (since questions are generated fresh).
"""

import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.database import get_pool
from app.features.math.models import MathQuestion, MathReview, MathTemplateInfo, SubmitMathAnswer
from app.features.math import repository
from app.services.llm import generate_math_word_problem, get_math_feedback
from app.services.math_problems import (
    MATH_TEMPLATES,
    compute_answer,
    generate_params,
    get_random_template,
    get_template,
    get_templates_by_topic,
    grade_math_answer,
)
from app.services.spaced_repetition import calculate_math_review

router = APIRouter(prefix="/math", tags=["math"])


@router.get("/templates", response_model=list[MathTemplateInfo])
async def list_templates(topic: str | None = Query(None)):
    """List available math problem templates."""
    if topic:
        templates = [t for t in MATH_TEMPLATES.values() if t.topic == topic]
    else:
        templates = list(MATH_TEMPLATES.values())

    return [
        MathTemplateInfo(
            type_id=t.type_id,
            topic=t.topic,
            concept=t.concept,
            asks_for=t.asks_for,
        )
        for t in templates
    ]


@router.get("/topics")
async def list_topics():
    """List all available math topics."""
    topics = sorted(set(t.topic for t in MATH_TEMPLATES.values()))
    return {"topics": topics}


@router.get("/next", response_model=MathQuestion)
async def next_math_question(
    topic: str | None = Query(None),
    template_type: str | None = Query(None),
):
    """
    Generate a new math question.

    Prioritizes templates that are due for review based on spaced repetition.
    Optionally filter by topic (e.g., "probability", "finance") or
    specific template_type (e.g., "poisson_pmf").
    """
    pool = await get_pool()

    # Get template - either specified, due for review, or random
    if template_type:
        template = get_template(template_type)
        if not template:
            raise HTTPException(404, f"Unknown template type: {template_type}")
    else:
        # Check what templates are due for review
        if topic:
            available_templates = get_templates_by_topic(topic)
            template_ids = [t.type_id for t in available_templates]
        else:
            template_ids = list(MATH_TEMPLATES.keys())

        # Find a template that's due for review
        due_row = await repository.get_due_template(pool, template_ids)

        if due_row:
            template = get_template(due_row["template_type"])
        else:
            # Nothing due - pick random (prioritize templates we haven't tried)
            tried = await repository.get_tried_templates(pool, template_ids)
            untried = [t for t in template_ids if t not in tried]

            if untried:
                template = get_template(untried[0])
            else:
                template = get_random_template(topic)

    # Ensure we have a valid template
    if not template:
        raise HTTPException(500, "Failed to select a math template")

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
    row = await repository.insert_math_question(
        pool,
        template_type=template.type_id,
        topic=template.topic,
        params_json=json.dumps(params),
        correct_answer=correct_answer,
        display_text=display_text,
    )

    return MathQuestion(
        id=row["id"],
        template_type=row["template_type"],
        topic=row["topic"],
        params=json.loads(row["params"]),
        display_text=row["display_text"],
        created_at=row["created_at"],
    )


@router.post("/submit", response_model=MathReview)
async def submit_math_answer(body: SubmitMathAnswer):
    """Submit an answer to a math question, get feedback, update spaced repetition."""
    pool = await get_pool()

    # Fetch the question
    row = await repository.get_math_question(pool, body.math_question_id)
    if not row:
        raise HTTPException(404, "Math question not found")

    template = get_template(row["template_type"])
    if not template:
        raise HTTPException(500, f"Unknown template type: {row['template_type']}")

    # Grade the answer
    grade = grade_math_answer(
        user_answer=body.user_answer,
        correct_answer=row["correct_answer"],
        tolerance=template.tolerance,
    )

    # Get LLM feedback
    feedback = await get_math_feedback(
        question=row["display_text"],
        concept=template.concept,
        correct_answer=row["correct_answer"],
        user_answer=body.user_answer,
        is_correct=grade["is_correct"],
    )

    # Get or compute spaced repetition result
    progress = await repository.get_math_template_progress(pool, row["template_type"])

    if progress:
        sr_result = calculate_math_review(
            is_correct=grade["is_correct"],
            current_ease=progress["ease_factor"],
            current_interval=progress["interval_days"],
            total_attempts=progress["total_attempts"],
        )
        await repository.update_math_template_progress(
            pool,
            template_type=row["template_type"],
            ease_factor=sr_result.ease_factor,
            interval_days=sr_result.interval_days,
            next_review_at=sr_result.next_review_at,
            is_correct=grade["is_correct"],
        )
    else:
        sr_result = calculate_math_review(
            is_correct=grade["is_correct"],
            current_ease=2.5,
            current_interval=0,
            total_attempts=0,
        )
        await repository.insert_math_template_progress(
            pool,
            template_type=row["template_type"],
            ease_factor=sr_result.ease_factor,
            interval_days=sr_result.interval_days,
            next_review_at=sr_result.next_review_at,
            is_correct=grade["is_correct"],
        )

    # Store the review
    review_row = await repository.insert_math_review(
        pool,
        math_question_id=body.math_question_id,
        user_answer=body.user_answer,
        is_correct=grade["is_correct"],
        feedback=feedback,
    )

    return MathReview(
        id=review_row["id"],
        math_question_id=review_row["math_question_id"],
        user_answer=review_row["user_answer"],
        is_correct=review_row["is_correct"],
        correct_answer=row["correct_answer"],  # Reveal after submission
        llm_feedback=review_row["llm_feedback"],
        created_at=review_row["created_at"],
    )


@router.get("/history")
async def get_math_history(limit: int = Query(20, le=100)):
    """Get recent math question attempts."""
    pool = await get_pool()
    rows = await repository.get_math_history(pool, limit=limit)

    return [
        {
            "id": r["id"],
            "template_type": r["template_type"],
            "topic": r["topic"],
            "question": r["display_text"],
            "user_answer": r["user_answer"],
            "correct_answer": r["correct_answer"],
            "is_correct": r["is_correct"],
            "feedback": r["llm_feedback"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]


@router.get("/stats")
async def get_math_stats(topic: str | None = Query(None)):
    """Get spaced repetition statistics for math templates."""
    pool = await get_pool()

    # Get progress for all templates
    rows = await repository.get_math_template_stats(pool)

    # Also get templates with no attempts
    template_ids = list(MATH_TEMPLATES.keys())
    if topic:
        template_ids = [t.type_id for t in get_templates_by_topic(topic)]

    attempted = {r["template_type"] for r in rows}

    progress_list = []
    for r in rows:
        if topic and r["template_type"] not in template_ids:
            continue
        template = get_template(r["template_type"])
        progress_list.append(
            {
                "template_type": r["template_type"],
                "concept": template.concept if template else "Unknown",
                "topic": template.topic if template else "Unknown",
                "ease_factor": r["ease_factor"],
                "interval_days": r["interval_days"],
                "next_review_at": r["next_review_at"],
                "total_attempts": r["total_attempts"],
                "correct_attempts": r["correct_attempts"],
                "accuracy": (
                    r["correct_attempts"] / r["total_attempts"]
                    if r["total_attempts"] > 0
                    else 0
                ),
                "is_due": (
                    r["next_review_at"] <= datetime.now()
                    if r["next_review_at"]
                    else True
                ),
            }
        )

    # Add templates never attempted
    for tid in template_ids:
        if tid not in attempted:
            template = get_template(tid)
            progress_list.append(
                {
                    "template_type": tid,
                    "concept": template.concept if template else "Unknown",
                    "topic": template.topic if template else "Unknown",
                    "ease_factor": 2.5,
                    "interval_days": 0,
                    "next_review_at": None,
                    "total_attempts": 0,
                    "correct_attempts": 0,
                    "accuracy": 0,
                    "is_due": True,  # Never tried = due
                }
            )

    # Summary stats
    total_attempts = sum(p["total_attempts"] for p in progress_list)
    correct_attempts = sum(p["correct_attempts"] for p in progress_list)
    due_count = sum(1 for p in progress_list if p["is_due"])

    return {
        "templates": progress_list,
        "summary": {
            "total_templates": len(progress_list),
            "templates_due": due_count,
            "total_attempts": total_attempts,
            "overall_accuracy": (
                correct_attempts / total_attempts if total_attempts > 0 else 0
            ),
        },
    }
