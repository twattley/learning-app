# apps/api — Python FastAPI Backend

The only source of truth for business logic, spaced repetition, and LLM grading.

## Stack

| Component | Technology |
|---|---|
| API framework | FastAPI 0.115+ |
| ASGI server | Uvicorn |
| Database driver | asyncpg (raw SQL, no ORM) |
| Validation | Pydantic v2 |
| LLM client | OpenAI-compatible (Gemini/Ollama) |
| Math | scipy |
| Package manager | uv |

## Source layout

```
app/
  features/
    questions/   — CRUD + LLM refinement (controller, repository, models)
    learn/       — next question selection, answer submission (controller, repository, models)
    math/        — template listing, problem generation (controller, repository, models)
    settings/    — LLM mode toggle (controller, models)
  services/
    llm.py              — single LLM client (never instantiate outside this module)
    spaced_repetition.py — pure SM-2 algorithm (no DB dependency)
  main.py          — FastAPI app, CORS, router registration
  config.py        — Pydantic Settings (RECALL_* env vars)
  database.py      — asyncpg pool, apply_migrations()
  cli.py           — `recall serve` and `recall init-db` entry points
schema/
  001_init.sql          — base schema (all tables)
  002_question_tags.sql — tags[] + is_work flag
```

## Commands

```bash
# From repo root:
make serve        # FastAPI on :8003 (reloads on change)
make init-db      # Apply schema/*.sql migrations

# Direct:
cd apps/api
uv run recall serve
uv run recall init-db
uv run pytest
```

## API routes

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/questions` | List questions (filter by topic, focus=work) |
| POST | `/api/v1/questions` | Create question |
| GET | `/api/v1/questions/{id}` | Get question |
| PUT | `/api/v1/questions/{id}` | Update question |
| DELETE | `/api/v1/questions/{id}` | Delete question |
| POST | `/api/v1/questions/refine` | Polish Q&A with Gemini |
| GET | `/api/v1/learn/next` | Next due question (regular or math) |
| POST | `/api/v1/learn/submit` | Submit answer, get LLM feedback |
| GET | `/api/v1/learn/stats` | Spaced repetition stats |
| GET | `/api/v1/math/templates` | List math templates |
| GET | `/api/v1/math/topics` | List math topics |
| GET | `/api/v1/settings/llm-mode` | Get current LLM mode |
| PUT | `/api/v1/settings/llm-mode` | Switch LLM mode |
| GET | `/health` | Health check |

## Environment variables

```
DATABASE_URL         — PostgreSQL connection string (required)
GEMINI_API_KEY       — Google AI API key (required)
LLM_PROVIDER         — gemini | openai | ollama (default: gemini)
GEMINI_MODEL         — default: gemini-2.0-flash
OLLAMA_BASE_URL      — default: http://localhost:11434/v1
OLLAMA_MODEL         — default: gemma3:12b
REPHRASE_QUESTIONS   — true | false (default: false)
```

Copy `.env.example` to `.env` and fill in values. The older `RECALL_...` names still work, but plain names are preferred.
