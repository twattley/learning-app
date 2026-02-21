-- Migration: add tags support for question-level focus (e.g. work)
-- Safe to run multiple times.

BEGIN;

ALTER TABLE public.questions
ADD COLUMN IF NOT EXISTS tags text[] NOT NULL DEFAULT '{}'::text[];

UPDATE public.questions
SET tags = '{}'::text[]
WHERE tags IS NULL;

CREATE INDEX IF NOT EXISTS idx_questions_tags_gin
ON public.questions
USING gin (tags);

COMMIT;

-- ------------------------------------------------------------------
-- Optional backfill helpers (run manually after the migration)
-- ------------------------------------------------------------------
-- Example: mark every existing question as work
-- UPDATE public.questions
-- SET tags = ARRAY['work']::text[];

-- Example: mark specific topics as work
-- UPDATE public.questions
-- SET tags = ARRAY['work']::text[]
-- WHERE topic IN ('python', 'sql', 'architecture');

-- Example: add work while preserving existing tags
-- UPDATE public.questions
-- SET tags = CASE
--   WHEN 'work' = ANY(tags) THEN tags
--   ELSE tags || ARRAY['work']::text[]
-- END;
