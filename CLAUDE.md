# Recall — Agent Entry Point

Read this first. It is the complete orientation for this project.

## What this project is

A personal learning app ("flashcards on steroids") combining spaced repetition, AI-powered
feedback, and dynamic math problems. Single-user, runs on a private Mac Mini home server,
accessible via Tailscale VPN on mobile.

## Monorepo layout

```
apps/
  api/      Python FastAPI — all business logic, spaced repetition, LLM grading
  web/      React 19 + Vite — browser dashboard
  mobile/   Expo 54 + React Native — iOS/Android app
packages/
  domain-types/  TypeScript interfaces mirroring the Python Pydantic models
```

## Quick reference

| Concern | Location |
|---|---|
| Python API source | `apps/api/app/` |
| DB schema (SQL migrations) | `apps/api/schema/` |
| Python config / env vars | `apps/api/.env` |
| Web app source | `apps/web/src/` |
| Mobile app source | `apps/mobile/src/` |
| Shared TypeScript types | `packages/domain-types/src/` |

## Commands (run from repo root)

```bash
make serve      # FastAPI on :8003
make web        # Vite dev server on :5176 (proxies /api → :8003)
make mobile     # Expo (iOS simulator or physical device)
make init-db    # Apply schema/*.sql to Postgres
make install    # uv sync + npm install
```

## Key architectural invariants — never break these

1. **Shared types live in `packages/domain-types/`** — both web and mobile import from
   `@recall/domain-types`. TypeScript interfaces mirror the Python Pydantic models.
2. **No ORM** — the backend uses raw asyncpg SQL. All queries stay in `repository.py` files
   within each feature.
3. **LLM service is shared** — `app/services/llm.py` is the single client for all LLM calls.
   Never instantiate LLM clients outside this module.
4. **SM-2 algorithm is pure** — `app/services/spaced_repetition.py` has no DB dependency.
   It computes the next interval from inputs; `repository.py` owns the write.
5. **API is JSON-only** (no server-rendered HTML). CORS is configured for :5176 and :8081.

## Environment variables (`apps/api/.env`)

```
DATABASE_URL     — PostgreSQL connection string
GEMINI_API_KEY   — Google AI API key (math problems + Q&A refinement)
LLM_PROVIDER     — gemini | openai | ollama (default: gemini)
GEMINI_MODEL     — default: gemini-2.0-flash
OLLAMA_BASE_URL  — default: http://localhost:11434/v1
OLLAMA_MODEL     — default: gemma3:12b
REPHRASE_QUESTIONS — true | false (default: false)
```

## Where to read next

- **`ARCHITECTURE.md`** — data model, design decisions, feature breakdown
- **`apps/api/README.md`** — Python API, CLI, feature structure
- **`apps/web/README.md`** — React app setup and feature structure
- **`apps/mobile/README.md`** — Expo setup and feature structure
- **`packages/domain-types/README.md`** — shared TypeScript contract
