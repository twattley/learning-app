# apps/web — React Web App

Browser-based learning interface built with React 19 + Vite.

## Stack

| Component | Technology |
|---|---|
| Framework | React 19 |
| Build tool | Vite 6 |
| Styling | Tailwind CSS + custom CSS (dark theme) |
| Server state | TanStack Query v5 |
| Routing | React Router v7 |
| Markdown | react-markdown + react-syntax-highlighter |
| Calculator | mathjs |
| Package manager | npm (workspace: @recall/web) |

## Source layout

```
src/
  api/
    config.ts      — API_BASE constant
    http.ts        — apiFetch, apiPost, apiPut, apiDelete
    queryClient.ts — singleton QueryClient
    ApiProvider.tsx — QueryClientProvider wrapper
    hooks.ts       — all TanStack Query hooks
  features/
    learn/
      LearnPage.tsx  — main review flow (phase state machine)
    questions/
      QuestionsPage.tsx    — question list with filters
      QuestionFormPage.tsx — create/edit form with Gemini refinement
  components/
    Calculator.tsx  — mathjs-powered in-app calculator
  App.tsx   — sidebar navigation, LLM mode toggle
  main.tsx  — entry point, router + ApiProvider
  index.css — Tailwind directives + custom dark theme
```

## Commands

```bash
# From repo root:
make web          # Dev server on :5176

# Direct:
cd apps/web
npm run dev       # Dev server (proxies /api → :8003)
npm run build     # Production build
```

## API hooks

All API interactions go through `src/api/hooks.ts`:

| Hook | Description |
|---|---|
| `useQuestions(topic?, focus?)` | List questions |
| `useQuestion(id)` | Fetch single question |
| `useCreateQuestion()` | Create mutation |
| `useUpdateQuestion()` | Update mutation |
| `useDeleteQuestion()` | Delete mutation |
| `useRefineQuestion()` | Gemini refinement mutation |
| `useSubmitAnswer()` | Submit answer mutation |
| `useLLMMode()` | Get current LLM mode |
| `useSetLLMMode()` | Switch LLM mode mutation |

## Notes

- The dev server proxies `/api/*` to `:8003` (see `vite.config.ts`)
- Tailwind is set up for new components; existing CSS classes use the custom dark theme
- No shared React Context — each feature owns its own queries
