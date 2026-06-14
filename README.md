# Recall

> Flashcards on steroids — a personal learning app with AI-powered feedback, spaced repetition, and dynamic math problems.

Read `CLAUDE.md` for agent orientation. Read `ARCHITECTURE.md` for design decisions.

---

## Monorepo layout

```
apps/
  api/      Python FastAPI — all business logic, LLM grading, spaced repetition
  web/      React 19 + Vite — browser interface
  mobile/   Expo 54 + React Native — iOS/Android app
packages/
  domain-types/  TypeScript interfaces shared by web and mobile
```

## Prerequisites

- **Python 3.11+** and [uv](https://docs.astral.sh/uv/)
- **Node.js 18+** and npm
- **PostgreSQL 17** (running and accessible)
- **Google AI API key** (for Gemini — math problems and Q&A refinement)
- **Ollama** (optional — for local LLM grading)

## Setup

```bash
# Install all dependencies
make install

# Configure backend environment
cp apps/api/.env.example apps/api/.env
# Edit apps/api/.env and fill in RECALL_DATABASE_URL and RECALL_GEMINI_API_KEY

# Bootstrap the database
make init-db
```

## Running

```bash
# Terminal 1 — Backend (FastAPI on :8003)
make serve

# Terminal 2 — Web (Vite dev server on :5176)
make web

# Terminal 3 — Mobile (Expo Go)
make mobile
```

Open [http://localhost:5176](http://localhost:5176) for the web app.

For mobile: install [Expo Go](https://expo.dev/go) on your phone, then scan the QR code.
On first launch, go to the **Settings** tab to configure the API URL (e.g. `http://server:8003/api/v1`).

## Environment variables (`apps/api/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `RECALL_DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `RECALL_GEMINI_API_KEY` | Yes | — | Google AI API key |
| `RECALL_LLM_PROVIDER` | No | `gemini` | `gemini` \| `openai` \| `ollama` |
| `RECALL_GEMINI_MODEL` | No | `gemini-2.0-flash` | Gemini model name |
| `RECALL_OLLAMA_BASE_URL` | No | `http://localhost:11434/v1` | Ollama endpoint |
| `RECALL_OLLAMA_MODEL` | No | `gemma3:12b` | Ollama model name |
| `RECALL_REPHRASE_QUESTIONS` | No | `false` | Rephrase questions on each review |

## Further reading

- [apps/api/README.md](apps/api/README.md) — Python API routes, CLI, feature structure
- [apps/web/README.md](apps/web/README.md) — React app setup and feature structure
- [apps/mobile/README.md](apps/mobile/README.md) — Expo setup and navigation
- [packages/domain-types/README.md](packages/domain-types/README.md) — shared TypeScript contract
- [ARCHITECTURE.md](ARCHITECTURE.md) — design decisions, data model, LLM strategy
