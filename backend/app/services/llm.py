from openai import AsyncOpenAI

from app.config import settings

_client: AsyncOpenAI | None = None
_gemini_client: AsyncOpenAI | None = None  # Dedicated Gemini client for math problems


def _get_client() -> AsyncOpenAI:
    """Return an OpenAI-compatible client for Gemini, OpenAI, or Ollama."""
    global _client
    if _client is None:
        print(f"[LLM] Initializing client with provider: {settings.llm_provider}")
        if settings.llm_provider == "gemini":
            print(f"[LLM] Using Gemini at generativelanguage.googleapis.com, model: {settings.gemini_model}")
            _client = AsyncOpenAI(
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=settings.gemini_api_key,
            )
        elif settings.llm_provider == "ollama":
            print(f"[LLM] Using Ollama at {settings.ollama_base_url}, model: {settings.ollama_model}")
            _client = AsyncOpenAI(
                base_url=settings.ollama_base_url,
                api_key="ollama",
            )
        else:
            print(f"[LLM] Using OpenAI, model: {settings.openai_model}")
            _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


def _get_model() -> str:
    if settings.llm_provider == "gemini":
        return settings.gemini_model
    if settings.llm_provider == "ollama":
        return settings.ollama_model
    return settings.openai_model


def _get_gemini_client() -> AsyncOpenAI:
    """Return a dedicated Gemini client for math problems (always uses Gemini)."""
    global _gemini_client
    if _gemini_client is None:
        print(f"[LLM] Initializing Gemini client for math problems, model: {settings.gemini_model}")
        _gemini_client = AsyncOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=settings.gemini_api_key,
        )
    return _gemini_client


FEEDBACK_SYSTEM_PROMPT = """\
You are a concise tutor. Compare the user's answer to the question.
{reference_block}
Respond in this exact format:

SCORE: [1-5]
VERDICT: [one sentence summary]
MISSING: [bullet list of key points the user missed, or "Nothing — great answer!" if complete]
TIP: [one actionable suggestion to improve their understanding]

Be encouraging but honest. Don't waffle."""

REPHRASE_SYSTEM_PROMPT = """\
Rephrase the following question. Keep the exact same meaning and scope.
Do NOT add hints or change what is being asked. Just word it differently.
Return only the rephrased question, nothing else."""


async def get_feedback(
    question_text: str,
    user_answer: str,
    answer_text: str | None = None,
) -> dict:
    """Call the LLM to grade the user's answer. Returns parsed feedback."""
    if answer_text:
        reference_block = f"The reference answer is:\n{answer_text}\n"
    else:
        reference_block = "There is no reference answer. Use your own knowledge to evaluate."

    system = FEEDBACK_SYSTEM_PROMPT.format(reference_block=reference_block)

    user_content = f"QUESTION:\n{question_text}\n\nUSER'S ANSWER:\n{user_answer}"

    response = await _get_client().chat.completions.create(
        model=_get_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
        max_tokens=500,
    )

    raw = response.choices[0].message.content or ""
    return _parse_feedback(raw)


async def rephrase_question(question_text: str) -> str:
    """Ask the LLM to rephrase a question while preserving meaning."""
    response = await _get_client().chat.completions.create(
        model=_get_model(),
        messages=[
            {"role": "system", "content": REPHRASE_SYSTEM_PROMPT},
            {"role": "user", "content": question_text},
        ],
        temperature=0.7,
        max_tokens=200,
    )
    return (response.choices[0].message.content or question_text).strip()


def _parse_feedback(raw: str) -> dict:
    """Best-effort parse of the structured LLM response."""
    result = {"score": None, "verdict": "", "missing": "", "tip": "", "raw": raw}

    for line in raw.split("\n"):
        upper = line.strip().upper()
        if upper.startswith("SCORE:"):
            try:
                result["score"] = int("".join(c for c in line.split(":", 1)[1] if c.isdigit())[:1])
            except (ValueError, IndexError):
                pass
        elif upper.startswith("VERDICT:"):
            result["verdict"] = line.split(":", 1)[1].strip()
        elif upper.startswith("MISSING:"):
            result["missing"] = line.split(":", 1)[1].strip()
        elif upper.startswith("TIP:"):
            result["tip"] = line.split(":", 1)[1].strip()

    return result


# ── Math Word Problem Generation (always uses Gemini) ──

MATH_WORD_PROBLEM_PROMPT = """\
Create a fun, realistic word problem for this math concept.

Concept: {concept}
Parameters: {params}
The student should calculate: {asks_for}

Style example (use a DIFFERENT scenario, be creative!): {example}

Rules:
- Make it feel like a real-world situation
- Use the exact parameter values provided
- Be clear about what the student needs to calculate
- Keep it concise (2-3 sentences max)
- Don't reveal the answer or formula

Return only the word problem, nothing else."""

MATH_FEEDBACK_PROMPT = """\
The student solved this math problem:

PROBLEM: {question}

CONCEPT: {concept}
CORRECT ANSWER: {correct_answer:.6g}
STUDENT'S ANSWER: {user_answer:.6g}
RESULT: {result}

Give brief, helpful feedback (2-3 sentences). If wrong, hint at where they might have gone wrong without giving the full solution. If correct, give a quick "well done" with an optional insight about the concept."""


async def generate_math_word_problem(
    concept: str,
    params: dict,
    asks_for: str,
    example: str,
) -> str:
    """Generate a creative word problem for a math concept using Gemini."""
    # Format params nicely
    params_str = ", ".join(f"{k} = {v}" for k, v in params.items())
    
    prompt = MATH_WORD_PROBLEM_PROMPT.format(
        concept=concept,
        params=params_str,
        asks_for=asks_for,
        example=example,
    )
    
    print(f"[LLM] Generating math word problem via Gemini for: {concept}")
    
    response = await _get_gemini_client().chat.completions.create(
        model=settings.gemini_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,  # Higher temp for creativity
        max_tokens=300,
    )
    
    return (response.choices[0].message.content or "").strip()


async def get_math_feedback(
    question: str,
    concept: str,
    correct_answer: float,
    user_answer: float,
    is_correct: bool,
) -> str:
    """Generate feedback for a math answer using Gemini."""
    result = "CORRECT ✓" if is_correct else "INCORRECT ✗"
    
    prompt = MATH_FEEDBACK_PROMPT.format(
        question=question,
        concept=concept,
        correct_answer=correct_answer,
        user_answer=user_answer,
        result=result,
    )
    
    response = await _get_gemini_client().chat.completions.create(
        model=settings.gemini_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=200,
    )
    
    return (response.choices[0].message.content or "").strip()


# ── Q&A Refinement (uses Gemini for quality) ──

REFINE_QA_PROMPT = """\
You are creating comprehensive study material for a flashcard learning app.

TOPIC: {topic}

USER'S ROUGH QUESTION:
{question}

USER'S ROUGH ANSWER:
{answer}

Your task is to transform this into HIGH-QUALITY study material:

FOR THE QUESTION:
- Make it clear, precise, and unambiguous
- Keep the original intent but improve the wording

FOR THE ANSWER:
- Create a COMPREHENSIVE reference answer (this will be used to grade recall attempts)
- Include ALL key concepts, definitions, and important details
- Structure it clearly with bullet points or numbered lists where helpful
- Add relevant examples if they aid understanding
- Include any common misconceptions or gotchas
- Use proper technical terminology
- Make it SELF-CONTAINED — assume the grader has no external knowledge
- Aim for thorough coverage, not brevity — this is reference material

The answer should contain everything someone would need to know to fully understand this topic.
A simple model should be able to grade a user's recall attempt just by comparing against this reference.

Return in this exact format:
QUESTION:
[your improved question]

ANSWER:
[your comprehensive, self-contained reference answer]"""


async def refine_qa(topic: str, question: str, answer: str) -> dict:
    """Refine and polish a question/answer pair using Gemini."""
    prompt = REFINE_QA_PROMPT.format(
        topic=topic,
        question=question,
        answer=answer if answer else "(no answer provided — generate a good reference answer)",
    )
    
    print(f"[LLM] Refining Q&A via Gemini for topic: {topic}")
    
    response = await _get_gemini_client().chat.completions.create(
        model=settings.gemini_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=1000,
    )
    
    raw = (response.choices[0].message.content or "").strip()
    return _parse_refined_qa(raw, question, answer)


def _parse_refined_qa(raw: str, original_question: str, original_answer: str) -> dict:
    """Parse the refined Q&A response."""
    result = {
        "question": original_question,
        "answer": original_answer,
        "raw": raw,
    }
    
    # Split by QUESTION: and ANSWER: markers
    if "QUESTION:" in raw and "ANSWER:" in raw:
        parts = raw.split("ANSWER:", 1)
        question_part = parts[0].replace("QUESTION:", "").strip()
        answer_part = parts[1].strip() if len(parts) > 1 else ""
        
        if question_part:
            result["question"] = question_part
        if answer_part:
            result["answer"] = answer_part
    
    return result
