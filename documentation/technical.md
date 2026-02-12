# Recall — Technical Documentation

> Technical architecture, codebase structure, and implementation details.

## Architecture Overview

```
┌──────────────┐    ┌──────────────┐    ┌────────────────┐
│  Web (React) │    │ Mobile (Expo)│    │   Ollama       │
│  :5175       │    │  Expo Go     │    │   (local LLM)  │
└──────┬───────┘    └──────┬───────┘    └───────┬────────┘
       │   /api proxy      │ Tailscale          │ :11434
       └───────────┬───────┘                    │
                   │                            │
            ┌──────▼──────┐                     │
            │   FastAPI   │◄────────────────────┘
            │   :8002     │
            └──────┬──────┘──────────► Gemini API (cloud)
                   │
            ┌──────▼──────┐
            │  PostgreSQL │
            │   :5432     │
            └─────────────┘
```

All services run on a Mac Mini ("server"). The mobile app connects via Tailscale VPN.

## Project Structure

```
learning_app/
├── documentation/           # Product and technical docs (this file)
│   ├── product.md          # Product-level overview
│   └── technical.md        # Technical architecture (this file)
├── backend/                 # FastAPI application
│   ├── pyproject.toml      # Python deps and project config
│   ├── learning_api_schema.sql  # Full DB schema dump
│   ├── backup_schema.sh    # Schema backup script
│   └── app/
│       ├── main.py         # FastAPI app, CORS, router registration
│       ├── config.py       # pydantic-settings config (env vars)
│       ├── database.py     # asyncpg connection pool
│       ├── schemas.py      # Pydantic request/response models
│       ├── routers/
│       │   ├── questions.py   # CRUD + Gemini refinement endpoint
│       │   ├── learn.py       # Unified learning endpoint (interleaving, SR, grading)
│       │   └── math.py        # Math-specific endpoints (templates, generation)
│       └── services/
│           ├── llm.py             # LLM client management, all prompts
│           ├── math_problems.py   # Math templates, scipy computations, grading
│           └── spaced_repetition.py  # SM-2 algorithm
├── web/                     # React + Vite web frontend
│   ├── vite.config.ts      # Dev server config, API proxy
│   ├── package.json        # Dependencies
│   └── src/
│       ├── App.tsx          # Root layout, sidebar nav
│       ├── main.tsx         # Entry point, router setup
│       ├── index.css        # All styles (dark theme, calculator)
│       ├── lib/
│       │   └── api.ts       # API client functions, TypeScript interfaces
│       ├── components/
│       │   └── Calculator.tsx  # mathjs-powered expression calculator
│       └── pages/
│           ├── Learn.tsx       # Main learning screen
│           ├── Questions.tsx   # Question list/management
│           └── QuestionForm.tsx  # Create/edit with Gemini refinement
└── mobile/                  # React Native + Expo
    ├── app.json            # Expo config
    ├── package.json        # Dependencies
    ├── app/
    │   ├── _layout.tsx     # Root layout
    │   ├── question-form.tsx  # Question creation
    │   └── (tabs)/
    │       ├── _layout.tsx    # Tab navigation
    │       ├── index.tsx      # Learn screen
    │       ├── questions.tsx  # Question list
    │       └── settings.tsx   # API URL configuration
    └── lib/
        ├── api.ts          # API client (configurable base URL)
        └── storage.ts      # AsyncStorage helpers
```

## Backend

### Stack

- **Python 3.11+**
- **FastAPI** — async web framework
- **asyncpg** — async PostgreSQL driver (raw SQL, no ORM)
- **pydantic** / **pydantic-settings** — validation, config
- **scipy** — probability/statistics computations
- **openai** — OpenAI-compatible client (used for Gemini and Ollama)

### Configuration (`app/config.py`)

All config via environment variables with `RECALL_` prefix:

| Variable                    | Default                              | Description                                                       |
| --------------------------- | ------------------------------------ | ----------------------------------------------------------------- |
| `RECALL_DATABASE_URL`       | `postgresql://localhost:5432/recall` | PostgreSQL connection string                                      |
| `RECALL_REPHRASE_QUESTIONS` | `false`                              | Rephrase questions each time they're shown                        |
| `RECALL_LLM_PROVIDER`       | `gemini`                             | Provider for regular Q&A grading: `gemini`, `openai`, or `ollama` |
| `RECALL_GEMINI_API_KEY`     |                                      | Google AI API key (always needed for math + refinement)           |
| `RECALL_GEMINI_MODEL`       | `gemini-2.0-flash`                   | Gemini model name                                                 |
| `RECALL_OLLAMA_BASE_URL`    | `http://localhost:11434/v1`          | Ollama API endpoint                                               |
| `RECALL_OLLAMA_MODEL`       | `llama3`                             | Ollama model (currently using `gemma3:12b`)                       |

Loaded from `.env` file in `backend/` directory.

### API Routes

All routes prefixed with `/api/v1`.

#### Questions (`/api/v1/questions`)

| Method   | Path                | Description                   |
| -------- | ------------------- | ----------------------------- |
| `POST`   | `/questions`        | Create a question             |
| `GET`    | `/questions`        | List all (optional `?topic=`) |
| `GET`    | `/questions/{id}`   | Get single question           |
| `PUT`    | `/questions/{id}`   | Update question               |
| `DELETE` | `/questions/{id}`   | Delete question               |
| `POST`   | `/questions/refine` | Refine Q&A pair via Gemini    |

#### Learn (`/api/v1/learn`)

| Method | Path            | Description                                       |
| ------ | --------------- | ------------------------------------------------- |
| `GET`  | `/learn/next`   | Get next question (interleaved, SR-prioritised)   |
| `POST` | `/learn/submit` | Submit answer (routes to regular or math grading) |
| `GET`  | `/learn/stats`  | Spaced repetition statistics                      |

#### Math (`/api/v1/math`)

| Method | Path              | Description                           |
| ------ | ----------------- | ------------------------------------- |
| `GET`  | `/math/templates` | List available math templates         |
| `GET`  | `/math/topics`    | List math topics                      |
| `GET`  | `/math/next`      | Generate a math question (standalone) |
| `POST` | `/math/submit`    | Submit math answer (standalone)       |

### LLM Architecture (`app/services/llm.py`)

Two separate LLM clients:

1. **Primary client** (`_get_client()`) — configurable via `RECALL_LLM_PROVIDER`
   - Used for: regular Q&A grading, question rephrasing
   - Can be Gemini, OpenAI, or Ollama

2. **Gemini client** (`_get_gemini_client()`) — always Gemini
   - Used for: math word problem generation, math feedback, Q&A refinement
   - These tasks need higher quality and aren't on the hot path

All clients use the OpenAI-compatible API format (Gemini and Ollama both support this).

#### Prompts

| Prompt                     | Purpose                                                 | Client  |
| -------------------------- | ------------------------------------------------------- | ------- |
| `FEEDBACK_SYSTEM_PROMPT`   | Grade regular Q&A (score 1-5, verdict, missing, tip)    | Primary |
| `REPHRASE_SYSTEM_PROMPT`   | Rephrase question keeping same meaning                  | Primary |
| `MATH_WORD_PROBLEM_PROMPT` | Generate creative word problem from template params     | Gemini  |
| `MATH_FEEDBACK_PROMPT`     | Brief feedback on math answer                           | Gemini  |
| `REFINE_QA_PROMPT`         | Transform rough notes into comprehensive study material | Gemini  |

### Math Problem Service (`app/services/math_problems.py`)

Template-based system — each template defines:

- **Parameter ranges** (e.g., λ between 2-20 for Poisson)
- **Computation function** (uses scipy for exact answers)
- **Tolerance** for grading (e.g., 0.01 for probabilities, 1.0 for money)
- **Formula hint** shown to user on request

Current templates (12 total):

| Template               | Topic       | Computation               |
| ---------------------- | ----------- | ------------------------- |
| `poisson_pmf`          | probability | `scipy.stats.poisson.pmf` |
| `poisson_cdf`          | probability | `scipy.stats.poisson.cdf` |
| `poisson_survival`     | probability | `scipy.stats.poisson.sf`  |
| `binomial_pmf`         | probability | `scipy.stats.binom.pmf`   |
| `binomial_cdf`         | probability | `scipy.stats.binom.cdf`   |
| `normal_cdf`           | probability | `scipy.stats.norm.cdf`    |
| `normal_zscore`        | probability | `(x - μ) / σ`             |
| `exponential_cdf`      | probability | `scipy.stats.expon.cdf`   |
| `exponential_survival` | probability | `scipy.stats.expon.sf`    |
| `present_value`        | finance     | `FV / (1 + r)^n`          |
| `future_value`         | finance     | `PV × (1 + r)^n`          |
| `compound_interest`    | finance     | `P × (1 + r/n)^(nt)`      |

Flow: template → `generate_params()` → `compute_answer()` → LLM generates word problem → store in DB.

### Spaced Repetition (`app/services/spaced_repetition.py`)

SM-2 algorithm variant:

**For regular questions (score 1-5):**

- Score < 3: Reset interval, review in 10 minutes
- First success: 1 day interval
- Second success: 3 day interval
- Subsequent: multiply interval by ease factor
- Ease factor adjusts per SM-2 formula, minimum 1.3
- Maximum interval: 365 days

**For math templates (binary correct/incorrect):**

- Correct maps to score 4, incorrect to score 2
- Same interval progression logic
- Tracked per template type, not per generated question

### Unified Learning Endpoint (`app/routers/learn.py`)

The `/learn/next` endpoint is the core of the learning experience:

1. Collect candidates from both regular questions AND math templates that are due
2. Include untried math templates as always-due candidates
3. If nothing is due, add random candidates from both pools
4. **Randomly select** between candidates — this is the interleaving
5. For regular: fetch question, optionally rephrase, return
6. For math: generate fresh params, compute answer, generate word problem via LLM, store, return

The `/learn/submit` endpoint:

1. Routes based on `question_type` field
2. Regular: LLM grades → parse score → update SR → store review
3. Math: parse numeric answer → scipy grades → LLM feedback → update template SR → store review

## Database

### PostgreSQL (database: `learning-api`)

**Connection:** `postgresql://postgres:test@server:5432/learning-api`

#### Tables

**`questions`** — User-created flashcards
| Column | Type | Description |
|---|---|---|
| `id` | `uuid` (PK) | Auto-generated |
| `question_text` | `text` | The question |
| `answer_text` | `text` (nullable) | Reference answer |
| `topic` | `text` | Topic tag |
| `ease_factor` | `float` (default 2.5) | SM-2 ease factor |
| `interval_days` | `int` (default 0) | Current review interval |
| `next_review_at` | `timestamptz` (default now) | When next due |
| `review_count` | `int` (default 0) | Total review count |
| `created_at` | `timestamptz` | Auto |
| `updated_at` | `timestamptz` | Auto |

**`reviews`** — History of regular question attempts
| Column | Type | Description |
|---|---|---|
| `id` | `uuid` (PK) | |
| `question_id` | `uuid` (FK → questions) | |
| `user_answer` | `text` | What user typed |
| `llm_feedback` | `text` | Raw LLM response |
| `score` | `int` (nullable) | Parsed score 1-5 |
| `created_at` | `timestamptz` | |

**`math_questions`** — Generated math problem instances
| Column | Type | Description |
|---|---|---|
| `id` | `uuid` (PK) | |
| `template_type` | `text` | Which template generated it |
| `topic` | `text` | probability / finance |
| `params` | `jsonb` | Randomised parameter values |
| `correct_answer` | `float` | Computed by scipy |
| `display_text` | `text` | LLM-generated word problem |
| `created_at` | `timestamptz` | |

**`math_reviews`** — History of math attempts
| Column | Type | Description |
|---|---|---|
| `id` | `uuid` (PK) | |
| `math_question_id` | `uuid` (FK → math_questions) | |
| `user_answer` | `float` | |
| `is_correct` | `boolean` | |
| `llm_feedback` | `text` (nullable) | |
| `created_at` | `timestamptz` | |

**`math_template_progress`** — SR state per math template
| Column | Type | Description |
|---|---|---|
| `template_type` | `text` (PK) | e.g. `poisson_pmf` |
| `ease_factor` | `float` (default 2.5) | |
| `interval_days` | `int` (default 0) | |
| `next_review_at` | `timestamptz` | |
| `total_attempts` | `int` | |
| `correct_attempts` | `int` | |

#### Key Indexes

- `idx_questions_topic` — filter by topic
- `idx_questions_next_review` — find due questions
- `idx_math_progress_next_review` — find due templates
- `idx_math_questions_template` / `topic` — filter math questions
- `idx_reviews_question_id` / `idx_math_reviews_question_id` — review history lookups

## Web Frontend

### Stack

- **React 19** with TypeScript
- **Vite** — dev server with API proxy to `:8002`
- **react-router-dom v7** — client-side routing
- **react-markdown** + **react-syntax-highlighter** — rich feedback display
- **mathjs** — expression evaluator for the calculator

### Pages

| Route                 | Component          | Description                            |
| --------------------- | ------------------ | -------------------------------------- |
| `/`                   | `Learn.tsx`        | Main learning interface                |
| `/questions`          | `Questions.tsx`    | Question list with topic filter        |
| `/questions/new`      | `QuestionForm.tsx` | Create question with Gemini refinement |
| `/questions/:id/edit` | `QuestionForm.tsx` | Edit existing question                 |

### Key Components

**`Calculator.tsx`** — In-app expression evaluator for math questions

- Uses mathjs `evaluate()` for arbitrary expressions
- Symbol buttons: `^`, `√`, `n!`, `e^x`, `ln`, `(`, `)`, `/`, `×`
- History with clickable results (fills answer input)
- Only shown for math questions

**`Learn.tsx`** — Main learning screen

- Detects question type (regular vs math)
- Regular: textarea input, Cmd+Enter to submit
- Math: number input, Enter to submit, calculator + hint button
- Feedback phase: markdown-rendered LLM response with score/result
- For math: shows correct answer on incorrect attempts

**`QuestionForm.tsx`** — Question creation/editing

- Topic, question, and answer text fields with markdown support
- "✨ Refine with Gemini" button to polish Q&A via API
- Tab key inserts spaces in textareas

### API Client (`lib/api.ts`)

All API calls go through a `request()` helper with JSON content type. Key interfaces:

```typescript
interface Question {
  id: string;
  question_text?: string;
  topic: string;
  display_text?: string;
  question_type: "regular" | "math";
  template_type?: string;
  hint?: string;
}

interface Review {
  question_type: "regular" | "math";
  llm_feedback: string;
  score: number | null; // regular
  is_correct?: boolean; // math
  correct_answer?: number; // math
}
```

### Styling

- Single `index.css` file, CSS custom properties
- Dark theme (slate palette: `--bg: #0f172a`, `--surface: #1e293b`)
- No CSS framework — custom classes

## Mobile Frontend

### Stack

- **React Native** with TypeScript
- **Expo** (managed workflow, Expo Go for deployment)
- **expo-router** — file-based routing with tabs
- **@react-native-async-storage/async-storage** — persistent settings

### Key Differences from Web

- API base URL is configurable via Settings tab (stored in AsyncStorage)
- Default API URL: `http://server:8002/api/v1` (Tailscale hostname)
- Settings page has "Test Connection" to verify connectivity
- Mobile Learn screen not yet updated for unified question types (still uses old regular-only format)

## Running the App

### Backend

```bash
cd backend
# Create .env with RECALL_DATABASE_URL, RECALL_GEMINI_API_KEY, RECALL_LLM_PROVIDER, etc.
pip install -e .
uvicorn app.main:app --reload --host 0.0.0.0
```

### Web

```bash
cd web
npm install
npm run dev    # Starts on :5175, proxies /api to :8002
```

### Mobile

```bash
cd mobile
npm install
npx expo start  # Scan QR with Expo Go
```

### Database Setup

```bash
psql -h server -U postgres -d learning-api -f backend/learning_api_schema.sql
```

## Design Decisions

1. **Raw SQL over ORM** — asyncpg with manual queries. Simple, fast, no abstraction layer to fight.
2. **OpenAI-compatible API for all LLMs** — Gemini and Ollama both support this, so one client library works for all.
3. **Separate Gemini client for quality tasks** — math generation and refinement always use Gemini regardless of primary provider setting.
4. **scipy for math answers** — LLMs hallucinate numbers. scipy gives exact answers for probability/finance.
5. **Comprehensive reference answers** — refined by Gemini at creation time so even tiny models can grade by comparison.
6. **Template-based math with LLM word problems** — templates ensure correctness, LLM adds creativity.
7. **Spaced repetition at template level for math** — can't track individual questions since they're regenerated each time.
8. **No auth** — single user on a private Tailscale network.
