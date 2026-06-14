# Schema Migrations

SQL migrations applied in order by `make init-db` (or `recall init-db`).

| File | Description |
|---|---|
| `001_init.sql` | Base schema — all five core tables |
| `002_question_tags.sql` | `tags[]` array + `is_work` flag on questions |

All migrations are idempotent (`IF NOT EXISTS`, `ADD COLUMN IF NOT EXISTS`).
Running `make init-db` on an existing database is safe.
