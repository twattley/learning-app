"""
Spaced Repetition Algorithm (SM-2 variant).

Based on the SuperMemo SM-2 algorithm with adjustments for our 1-5 scoring system.

The algorithm determines:
1. When to show a card next (interval)
2. How "easy" a card is (ease factor)

Key rules:
- Score 4-5: Easy - increase interval significantly
- Score 3: Good - normal progression
- Score 1-2: Hard/Wrong - reset interval, show again soon
"""

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class ReviewResult:
    """Result of applying the SR algorithm after a review."""

    ease_factor: float
    interval_days: int
    next_review_at: datetime


def calculate_next_review(
    score: int,
    current_ease: float = 2.5,
    current_interval: int = 0,
    review_count: int = 0,
) -> ReviewResult:
    """
    Calculate the next review parameters based on the score.

    Args:
        score: User's score (1-5)
            - 5: Perfect response
            - 4: Correct with hesitation
            - 3: Correct with difficulty
            - 2: Incorrect but close
            - 1: Complete failure
        current_ease: Current ease factor (default 2.5, range 1.3-2.5+)
        current_interval: Current interval in days
        review_count: Number of times this item has been reviewed

    Returns:
        ReviewResult with new ease_factor, interval_days, and next_review_at
    """
    # Clamp score to valid range
    score = max(1, min(5, score))

    # Calculate new ease factor using SM-2 formula
    # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    # where q is the quality of response (0-5, we use 1-5)
    q = score
    new_ease = current_ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))

    # Ease factor should never go below 1.3 (makes cards too hard to escape)
    new_ease = max(1.3, new_ease)

    # Calculate new interval
    if score < 3:
        # Failed - reset to beginning
        new_interval = 0  # Will show again soon (within the day)
    elif review_count == 0 or current_interval == 0:
        # First successful review
        new_interval = 1
    elif current_interval == 1:
        # Second successful review
        new_interval = 3
    else:
        # Subsequent reviews - multiply by ease factor
        new_interval = round(current_interval * new_ease)

    # Cap interval at 365 days (1 year) - don't want cards disappearing forever
    new_interval = min(365, new_interval)

    # Calculate next review time
    if new_interval == 0:
        # Show again in 10 minutes for failed cards
        next_review = datetime.now() + timedelta(minutes=10)
    else:
        next_review = datetime.now() + timedelta(days=new_interval)

    return ReviewResult(
        ease_factor=round(new_ease, 2),
        interval_days=new_interval,
        next_review_at=next_review,
    )


def calculate_math_review(
    is_correct: bool,
    current_ease: float = 2.5,
    current_interval: int = 0,
    total_attempts: int = 0,
) -> ReviewResult:
    """
    Calculate next review for math templates.

    Math uses binary correct/incorrect, so we map:
    - Correct → score 4
    - Incorrect → score 2

    This is slightly forgiving since math has randomized numbers.
    """
    score = 4 if is_correct else 2
    return calculate_next_review(
        score=score,
        current_ease=current_ease,
        current_interval=current_interval,
        review_count=total_attempts,
    )


def get_priority_score(
    next_review_at: datetime | None, ease_factor: float = 2.5
) -> float:
    """
    Calculate a priority score for ordering items in the review queue.

    Lower score = higher priority (show first).

    Factors:
    - How overdue the item is (most important)
    - Ease factor (harder items get slight priority)
    """
    now = datetime.now()

    if next_review_at is None:
        # Never reviewed - high priority
        return -1000.0

    # Hours overdue (negative if not yet due)
    hours_overdue = (now - next_review_at).total_seconds() / 3600

    # Harder items (lower ease) get a small boost
    ease_penalty = (ease_factor - 1.3) * 10  # 0 to ~15 for typical ease range

    # Priority: primarily overdue time, with ease as tiebreaker
    return -hours_overdue + ease_penalty
