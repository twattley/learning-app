"""
Math problem generation and computation service.

Uses scipy for accurate calculations and LLM for creative word problem generation.
"""
import random
from dataclasses import dataclass
from typing import Any, Callable

from scipy import stats


@dataclass
class MathTemplate:
    """Definition of a math problem type."""
    type_id: str
    topic: str
    concept: str
    param_ranges: dict[str, tuple[float, float]]
    asks_for: str
    example: str
    compute: Callable[[dict[str, float]], float]
    hint: str = ""  # Formula hint to help the user
    tolerance: float = 0.01  # For grading — how close the answer needs to be


# ── Computation Functions ──

def _poisson_pmf(params: dict) -> float:
    """P(X = k) for Poisson distribution."""
    return stats.poisson.pmf(params["k"], params["lambda"])


def _poisson_cdf(params: dict) -> float:
    """P(X <= k) for Poisson distribution."""
    return stats.poisson.cdf(params["k"], params["lambda"])


def _poisson_survival(params: dict) -> float:
    """P(X > k) for Poisson distribution."""
    return stats.poisson.sf(params["k"], params["lambda"])


def _binomial_pmf(params: dict) -> float:
    """P(X = k) for Binomial distribution."""
    return stats.binom.pmf(params["k"], params["n"], params["p"])


def _binomial_cdf(params: dict) -> float:
    """P(X <= k) for Binomial distribution."""
    return stats.binom.cdf(params["k"], params["n"], params["p"])


def _normal_cdf(params: dict) -> float:
    """P(X <= x) for Normal distribution."""
    return stats.norm.cdf(params["x"], params["mu"], params["sigma"])


def _normal_zscore(params: dict) -> float:
    """Z-score calculation."""
    return (params["x"] - params["mu"]) / params["sigma"]


def _exponential_cdf(params: dict) -> float:
    """P(X <= x) for Exponential distribution."""
    # scipy uses scale = 1/lambda
    return stats.expon.cdf(params["x"], scale=1/params["lambda"])


def _exponential_survival(params: dict) -> float:
    """P(X > x) for Exponential distribution."""
    return stats.expon.sf(params["x"], scale=1/params["lambda"])


def _present_value(params: dict) -> float:
    """Present Value = FV / (1 + r)^n"""
    return params["fv"] / ((1 + params["r"]) ** params["n"])


def _future_value(params: dict) -> float:
    """Future Value = PV * (1 + r)^n"""
    return params["pv"] * ((1 + params["r"]) ** params["n"])


def _compound_interest(params: dict) -> float:
    """A = P * (1 + r/n)^(n*t)"""
    return params["principal"] * ((1 + params["rate"]/params["compounds_per_year"]) ** (params["compounds_per_year"] * params["years"]))


# ── Template Registry ──

MATH_TEMPLATES: dict[str, MathTemplate] = {
    "poisson_pmf": MathTemplate(
        type_id="poisson_pmf",
        topic="probability",
        concept="Poisson distribution - probability of exactly k events occurring",
        param_ranges={"lambda": (2, 20), "k": (0, 15)},
        asks_for="P(X = k), the probability of exactly k events",
        example="A busy coffee shop serves an average of 12 customers per hour. What's the probability of serving exactly 8 customers in the next hour?",
        compute=_poisson_pmf,
        hint="**Poisson PMF:** P(X = k) = e^(-λ) × λ^k / k!\n\nWhere λ (lambda) is the average rate and k is the exact count you want.",
    ),
    "poisson_cdf": MathTemplate(
        type_id="poisson_cdf",
        topic="probability",
        concept="Poisson distribution - probability of k or fewer events",
        param_ranges={"lambda": (3, 20), "k": (1, 12)},
        asks_for="P(X ≤ k), the probability of at most k events",
        example="A website receives an average of 15 visitors per minute. What's the probability of receiving 10 or fewer visitors in the next minute?",
        compute=_poisson_cdf,
        hint="**Poisson CDF:** P(X ≤ k) = Σ P(X = i) for i = 0 to k\n\nSum the PMF from 0 to k: Σ e^(-λ) × λ^i / i!",
    ),
    "poisson_survival": MathTemplate(
        type_id="poisson_survival",
        topic="probability",
        concept="Poisson distribution - probability of more than k events",
        param_ranges={"lambda": (5, 25), "k": (3, 15)},
        asks_for="P(X > k), the probability of more than k events",
        example="A call center receives an average of 18 calls per hour. What's the probability of receiving more than 20 calls in the next hour?",
        compute=_poisson_survival,
        hint="**Poisson Survival:** P(X > k) = 1 - P(X ≤ k)\n\nCalculate P(X ≤ k) first, then subtract from 1.",
    ),
    "binomial_pmf": MathTemplate(
        type_id="binomial_pmf",
        topic="probability",
        concept="Binomial distribution - probability of exactly k successes in n trials",
        param_ranges={"n": (5, 20), "p": (0.2, 0.8), "k": (1, 15)},
        asks_for="P(X = k), the probability of exactly k successes",
        example="A basketball player has a 70% free throw success rate. If she takes 10 free throws, what's the probability she makes exactly 7?",
        compute=_binomial_pmf,
        hint="**Binomial PMF:** P(X = k) = C(n,k) × p^k × (1-p)^(n-k)\n\nWhere C(n,k) = n! / (k! × (n-k)!)",
    ),
    "binomial_cdf": MathTemplate(
        type_id="binomial_cdf",
        topic="probability",
        concept="Binomial distribution - probability of k or fewer successes",
        param_ranges={"n": (8, 25), "p": (0.3, 0.7), "k": (2, 18)},
        asks_for="P(X ≤ k), the probability of at most k successes",
        example="A multiple choice test has 15 questions with 4 options each. If a student guesses randomly, what's the probability they get 5 or fewer correct?",
        compute=_binomial_cdf,
        hint="**Binomial CDF:** P(X ≤ k) = Σ P(X = i) for i = 0 to k\n\nSum the binomial PMF from 0 to k.",
    ),
    "normal_cdf": MathTemplate(
        type_id="normal_cdf",
        topic="probability",
        concept="Normal distribution - probability of a value being less than or equal to x",
        param_ranges={"mu": (50, 150), "sigma": (5, 25), "x": (30, 180)},
        asks_for="P(X ≤ x), the probability of a value being at most x",
        example="Adult male heights are normally distributed with mean 175cm and standard deviation 10cm. What's the probability a randomly selected man is 180cm or shorter?",
        compute=_normal_cdf,
        hint="**Normal CDF:** First calculate z = (x - μ) / σ\n\nThen look up Φ(z) in a z-table, or use: Φ(z) ≈ 0.5 × (1 + erf(z/√2))",
    ),
    "normal_zscore": MathTemplate(
        type_id="normal_zscore",
        topic="probability",
        concept="Z-score calculation - how many standard deviations from the mean",
        param_ranges={"mu": (40, 100), "sigma": (5, 20), "x": (20, 130)},
        asks_for="The z-score (number of standard deviations from mean)",
        example="Exam scores have a mean of 72 and standard deviation of 8. What is the z-score for a student who scored 84?",
        compute=_normal_zscore,
        hint="**Z-score:** z = (x - μ) / σ\n\nSubtract the mean from the value, then divide by standard deviation.",
        tolerance=0.1,
    ),
    "exponential_cdf": MathTemplate(
        type_id="exponential_cdf",
        topic="probability",
        concept="Exponential distribution - probability of event occurring within time x",
        param_ranges={"lambda": (0.5, 5), "x": (0.5, 4)},
        asks_for="P(X ≤ x), the probability of the event occurring within time x",
        example="Light bulbs fail at a rate of 2 per year on average. What's the probability a bulb fails within the first 6 months?",
        compute=_exponential_cdf,
        hint="**Exponential CDF:** P(X ≤ x) = 1 - e^(-λx)\n\nWhere λ is the rate parameter (events per unit time).",
    ),
    "exponential_survival": MathTemplate(
        type_id="exponential_survival",
        topic="probability",
        concept="Exponential distribution - probability of surviving beyond time x",
        param_ranges={"lambda": (0.2, 3), "x": (0.5, 5)},
        asks_for="P(X > x), the probability of lasting longer than time x",
        example="A machine breaks down on average once every 4 hours. What's the probability it runs for more than 5 hours without breaking?",
        compute=_exponential_survival,
        hint="**Exponential Survival:** P(X > x) = e^(-λx)\n\nWhere λ is the rate (events per unit time). Note: if given mean time between events, λ = 1/mean.",
    ),
    "present_value": MathTemplate(
        type_id="present_value",
        topic="finance",
        concept="Present Value - what a future sum is worth today given a discount rate",
        param_ranges={"fv": (1000, 100000), "r": (0.03, 0.12), "n": (1, 20)},
        asks_for="The present value (PV = FV / (1 + r)^n)",
        example="You will receive £50,000 in 10 years. If the discount rate is 6% per year, what is that payment worth today?",
        compute=_present_value,
        hint="**Present Value:** PV = FV / (1 + r)^n\n\nDivide the future value by (1 + interest rate) raised to the number of periods.",
        tolerance=1.0,  # Within £1 for money
    ),
    "future_value": MathTemplate(
        type_id="future_value",
        topic="finance",
        concept="Future Value - what an investment today will be worth in the future",
        param_ranges={"pv": (500, 50000), "r": (0.02, 0.10), "n": (2, 25)},
        asks_for="The future value (FV = PV * (1 + r)^n)",
        example="You invest £10,000 today at 5% annual interest. What will it be worth in 15 years?",
        compute=_future_value,
        hint="**Future Value:** FV = PV × (1 + r)^n\n\nMultiply the present value by (1 + interest rate) raised to the number of periods.",
        tolerance=1.0,
    ),
    "compound_interest": MathTemplate(
        type_id="compound_interest",
        topic="finance",
        concept="Compound Interest - final amount with periodic compounding",
        param_ranges={"principal": (1000, 50000), "rate": (0.03, 0.10), "compounds_per_year": (1, 12), "years": (1, 15)},
        asks_for="The final amount A = P(1 + r/n)^(nt)",
        example="You deposit £5,000 in a savings account with 4% annual interest, compounded monthly. How much will you have after 8 years?",
        compute=_compound_interest,
        hint="**Compound Interest:** A = P × (1 + r/n)^(n×t)\n\nWhere P = principal, r = annual rate, n = compounds per year, t = years.",
        tolerance=1.0,
    ),
}


def get_template(type_id: str) -> MathTemplate | None:
    """Get a specific template by ID."""
    return MATH_TEMPLATES.get(type_id)


def get_all_templates() -> list[MathTemplate]:
    """Get all available templates."""
    return list(MATH_TEMPLATES.values())


def get_templates_by_topic(topic: str) -> list[MathTemplate]:
    """Get templates for a specific topic."""
    return [t for t in MATH_TEMPLATES.values() if t.topic == topic]


def get_random_template(topic: str | None = None) -> MathTemplate:
    """Get a random template, optionally filtered by topic."""
    if topic:
        templates = get_templates_by_topic(topic)
    else:
        templates = list(MATH_TEMPLATES.values())
    return random.choice(templates)


def generate_params(template: MathTemplate) -> dict[str, float]:
    """Generate random parameters within the template's ranges."""
    params = {}
    for param_name, (min_val, max_val) in template.param_ranges.items():
        if param_name in ("n", "k", "compounds_per_year"):
            # Integer params
            params[param_name] = random.randint(int(min_val), int(max_val))
        elif param_name == "p":
            # Probability - round to 2 decimal places
            params[param_name] = round(random.uniform(min_val, max_val), 2)
        elif param_name in ("fv", "pv", "principal"):
            # Money - round to nice numbers
            params[param_name] = round(random.uniform(min_val, max_val), -2)  # Round to nearest 100
        elif param_name == "rate":
            # Interest rate - round to nice percentage
            params[param_name] = round(random.uniform(min_val, max_val), 2)
        else:
            # General numeric
            params[param_name] = round(random.uniform(min_val, max_val), 1)
    
    # For binomial, ensure k <= n
    if "k" in params and "n" in params:
        params["k"] = min(params["k"], params["n"])
    
    return params


def compute_answer(template: MathTemplate, params: dict[str, float]) -> float:
    """Compute the correct answer using scipy."""
    return template.compute(params)


def grade_math_answer(user_answer: float, correct_answer: float, tolerance: float) -> dict:
    """Grade a math answer with tolerance for floating point."""
    # Handle percentage difference for very small/large numbers
    if abs(correct_answer) < 0.0001:
        is_correct = abs(user_answer - correct_answer) < tolerance
    else:
        relative_error = abs(user_answer - correct_answer) / abs(correct_answer)
        is_correct = relative_error < tolerance or abs(user_answer - correct_answer) < tolerance
    
    return {
        "is_correct": is_correct,
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "difference": abs(user_answer - correct_answer),
    }
