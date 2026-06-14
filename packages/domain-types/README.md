# packages/domain-types — Shared TypeScript Types

TypeScript interfaces mirroring the Python Pydantic models in `apps/api`.
Both `apps/web` and `apps/mobile` import from this package.

## Usage

```typescript
import type { Question, Review, LLMMode } from '@recall/domain-types'
```

## Exported types

| Type | Description |
|---|---|
| `Question` | A flashcard question with SM-2 state |
| `CreateQuestionInput` | Body for POST /questions |
| `UpdateQuestionInput` | Body for PUT /questions/:id |
| `RefineInput` | Body for POST /questions/refine |
| `RefineResult` | Response from /questions/refine |
| `Review` | LLM feedback after answer submission |
| `SubmitAnswerInput` | Body for POST /learn/submit |
| `LLMMode` | Current LLM provider/model state |

## Sync rule

These types are hand-written mirrors of the Pydantic models in `apps/api/app/features/*/models.py`.
When the Python models change, update this package too.

**Source of truth:** Python Pydantic models.
**Mirror:** TypeScript interfaces here.
