# Recall

> Flashcards on steroids — a personal learning app with AI-powered feedback, spaced repetition, and dynamic math problems.

See [documentation/product.md](documentation/product.md) for the full product overview and [documentation/technical.md](documentation/technical.md) for architecture details.

---

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **PostgreSQL 17** (running and accessible)
- **Ollama** (optional — for local LLM grading)
- **Google AI API key** (for Gemini — math problems and Q&A refinement)

## 1. Database Setup

Create the database and load the schema:

```bash
createdb -h server -U postgres learning-api
psql -h server -U postgres -d learning-api -f backend/learning_api_schema.sql
```

Replace `server` with your PostgreSQL host (`localhost` if running locally).

## 2. Backend

```bash
cd backend

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Create .env file
cat > .env << 'EOF'
RECALL_DATABASE_URL=postgresql://postgres:test@server:5432/learning-api
RECALL_LLM_PROVIDER=ollama
RECALL_GEMINI_API_KEY=your-gemini-api-key-here
RECALL_GEMINI_MODEL=gemini-2.0-flash
RECALL_OLLAMA_BASE_URL=http://localhost:11434/v1
RECALL_OLLAMA_MODEL=gemma3:12b
RECALL_REPHRASE_QUESTIONS=true
EOF

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

Verify it's running:

```bash
curl http://localhost:8002/health
# {"status":"ok"}
```

### Environment Variables

| Variable                    | Required | Default                     | Description                                               |
| --------------------------- | -------- | --------------------------- | --------------------------------------------------------- |
| `RECALL_DATABASE_URL`       | Yes      | —                           | PostgreSQL connection string                              |
| `RECALL_GEMINI_API_KEY`     | Yes      | —                           | Google AI API key (needed for math + refinement)          |
| `RECALL_LLM_PROVIDER`       | No       | `gemini`                    | Provider for Q&A grading: `gemini`, `openai`, or `ollama` |
| `RECALL_GEMINI_MODEL`       | No       | `gemini-2.0-flash`          | Gemini model                                              |
| `RECALL_OLLAMA_BASE_URL`    | No       | `http://localhost:11434/v1` | Ollama endpoint                                           |
| `RECALL_OLLAMA_MODEL`       | No       | `llama3`                    | Ollama model name                                         |
| `RECALL_REPHRASE_QUESTIONS` | No       | `false`                     | Rephrase questions on each review                         |

## 3. Web Frontend

```bash
cd web

# Install dependencies
npm install

# Start dev server (proxies /api to backend on :8002)
npm run dev
```

Open [http://localhost:5175](http://localhost:5175).

## 4. Mobile App (Optional)

Requires [Expo Go](https://expo.dev/go) on your phone and network access to the backend (e.g. via Tailscale).

```bash
cd mobile

# Install dependencies
npm install

# Start Expo
npx expo start
```

Scan the QR code with Expo Go. On first launch, go to the **Settings** tab to configure the API URL (e.g. `http://server:8002/api/v1`).

## Quick Start Summary

```bash
# Terminal 1 — Backend
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

# Terminal 2 — Web
cd web && npm run dev

# Terminal 3 — Ollama (if using local LLM)
ollama serve
ollama pull gemma3:12b
```

Then open [http://localhost:5175](http://localhost:5175), add some questions, and start learning.

## Work-Focused Learning

Questions support lightweight tags (up to 2), and `work` is a first-class focus signal.

- In **New/Edit Question**, add optional tags and toggle **Mark as work question**.
- In **Learn**, toggle **Work focus only** to pull only work-tagged questions.
- Interleaving remains the default; math interleaving is skipped while work focus is enabled.

Backend-driven API filters:

- `GET /api/v1/questions?focus=work`
- `GET /api/v1/learn/next?focus=work`
- `GET /api/v1/learn/stats?focus=work`

### Backward compatibility and migration

The backend auto-applies this schema change at startup for existing databases, so older data continues to work.

If you prefer an explicit migration step, run:

```bash
psql -h server -U postgres -d learning-api -f backend/migrations/20260216_add_question_tags.sql
```

That migration is idempotent (`IF NOT EXISTS`) and includes optional backfill examples you can uncomment/edit.

## Backing Up the Schema

```bash
./backend/backup_schema.sh
```

This dumps the current schema to `backend/learning_api_schema.sql`.
