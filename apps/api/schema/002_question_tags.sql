-- Add tags array and is_work flag to questions
-- Idempotent: safe to run multiple times.

BEGIN;

ALTER TABLE questions
ADD COLUMN IF NOT EXISTS tags text[] NOT NULL DEFAULT '{}'::text[];

ALTER TABLE questions
ADD COLUMN IF NOT EXISTS is_work boolean NOT NULL DEFAULT false;

CREATE INDEX IF NOT EXISTS idx_questions_tags_gin ON questions USING gin (tags);

COMMIT;
