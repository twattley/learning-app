# Architecture

This document explains the _why_ behind every significant decision.
Read `CLAUDE.md` first for a quick orientation, then come back here for depth.

---

## Product in one sentence

Create flashcard-style questions → have an LLM grade your answers with feedback →
spaced repetition schedules the next review → dynamic math problems add variety.

---

## Monorepo shape

```
apps/api      Python FastAPI — all business logic lives here
apps/web      React 19 SPA — browser interface
apps/mobile   Expo 54 — iOS/Android app
packages/     Shared artefacts (TypeScript types only, for now)
```

**Why a monorepo?** Web and mobile share the same API contract and domain vocabulary.
Keeping them together prevents the contract from diverging silently.

**Rule:** Code promoted to `packages/` only when two or more apps need it.

**Package managers:** Python uses `uv` (workspace root at repo root, member at `apps/api`).
Node uses npm workspaces (root `package.json`). The two toolchains are independent.

---

## Data model

Five Postgres tables:

```sql
questions (
  id          UUID PRIMARY KEY,
  question_text TEXT NOT NULL,
  answer_text   TEXT,
  topic         TEXT NOT NULL,
  tags          TEXT[],
  is_work       BOOLEAN DEFAULT false,
  -- SM-2 state
  ease_factor   NUMERIC DEFAULT 2.5,
  interval      INT DEFAULT 0,
  repetitions   INT DEFAULT 0,
  next_review_at TIMESTAMPTZ DEFAULT now(),
  created_at    TIMESTAMPTZ DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now()
)

reviews (
  id            UUID PRIMARY KEY,
  question_id   UUID REFERENCES questions(id),
  user_answer   TEXT NOT NULL,
  llm_feedback  TEXT NOT NULL,
  score         INT,            -- 0-5 for regular, null for math
  created_at    TIMESTAMPTZ DEFAULT now()
)

math_questions (
  id            UUID PRIMARY KEY,
  template_type TEXT NOT NULL,
  params        JSONB NOT NULL,
  correct_answer NUMERIC NOT NULL,
  display_text  TEXT NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT now()
)

math_reviews (
  id              UUID PRIMARY KEY,
  math_question_id UUID REFERENCES math_questions(id),
  user_answer     NUMERIC,
  is_correct      BOOLEAN NOT NULL,
  created_at      TIMESTAMPTZ DEFAULT now()
)

math_template_progress (
  template_type TEXT PRIMARY KEY,
  ease_factor   NUMERIC DEFAULT 2.5,
  interval      INT DEFAULT 0,
  repetitions   INT DEFAULT 0,
  next_review_at TIMESTAMPTZ DEFAULT now()
)
```

---

## Feature layout (backend)

Each feature owns its slice of the API:

```
app/features/
  questions/   — CRUD + LLM refinement
  learn/       — next question selection, answer submission
  math/        — template listing, problem generation
  settings/    — LLM mode toggle
```

Each feature directory follows the Controller-Service-Repository pattern:
- `controller.py` — FastAPI router (routes only, no business logic)
- `service.py` — business logic (optional, only when needed)
- `repository.py` — all SQL queries (no business logic)
- `models.py` — Pydantic request/response models (the API contract)

Shared services that span multiple features live in `app/services/`:
- `llm.py` — single LLM client; never instantiate outside this module
- `spaced_repetition.py` — pure SM-2 algorithm; no DB dependency

---

## LLM strategy

Two clients, both using the OpenAI-compatible interface:

| Client | Provider | Used for |
|---|---|---|
| Primary | Gemini (default), OpenAI, or Ollama | Q&A grading, question rephrasing |
| Gemini | Google AI (always) | Math word problem generation, feedback, Q&A refinement |

`RECALL_LLM_PROVIDER` selects the primary client at startup. The Gemini client is always
initialised regardless of provider because math problem generation requires it.

---

## SM-2 spaced repetition

The SM-2 algorithm lives in `app/services/spaced_repetition.py` (pure function, no DB).
It takes a score (0–5) and current SM-2 state and returns the updated state.

- Score ≥ 3 → answer was correct; interval grows
- Score < 3 → answer was wrong; interval resets to 1 day
- `ease_factor` adjusts based on performance history

Math templates use the same SM-2 loop, but state is tracked per template type in
`math_template_progress` rather than per-question.

---

## Frontend state management

- **TanStack Query** for all server state (no Redux/Zustand)
- No shared React Context for data — each feature owns its own queries
- Query invalidation is the coordination mechanism after mutations
- `packages/domain-types/` is the single source of truth for shared TypeScript types

---

## Mobile navigation

React Navigation with bottom tabs:
- **Learn** — the main review flow
- **Questions** — CRUD list + form
- **Settings** — API URL, LLM mode toggle

Expo Go is used for development; no EAS builds required for personal use.

---

## SQL migrations

Migrations live in `apps/api/schema/` and are numbered sequentially:

```
001_init.sql        — base schema (all tables)
002_question_tags.sql — tags[] column + is_work flag
```

`make init-db` applies all migrations in order (idempotent via `IF NOT EXISTS`).
