-- Initial schema: all core tables
-- Idempotent: safe to run multiple times.

CREATE TABLE IF NOT EXISTS questions (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    question_text text NOT NULL,
    answer_text text,
    topic text NOT NULL,
    ease_factor double precision DEFAULT 2.5,
    interval_days integer DEFAULT 0,
    next_review_at timestamp with time zone DEFAULT now(),
    review_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    question_id uuid NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    user_answer text NOT NULL,
    llm_feedback text NOT NULL,
    score integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS math_questions (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    template_type text NOT NULL,
    topic text NOT NULL,
    params jsonb NOT NULL,
    correct_answer double precision NOT NULL,
    display_text text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS math_reviews (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    math_question_id uuid NOT NULL REFERENCES math_questions(id) ON DELETE CASCADE,
    user_answer double precision NOT NULL,
    is_correct boolean NOT NULL,
    llm_feedback text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);

CREATE TABLE IF NOT EXISTS math_template_progress (
    template_type text NOT NULL PRIMARY KEY,
    ease_factor double precision DEFAULT 2.5,
    interval_days integer DEFAULT 0,
    next_review_at timestamp with time zone DEFAULT now(),
    total_attempts integer DEFAULT 0,
    correct_attempts integer DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions USING btree (topic);
CREATE INDEX IF NOT EXISTS idx_questions_next_review ON questions USING btree (next_review_at);
CREATE INDEX IF NOT EXISTS idx_reviews_question_id ON reviews USING btree (question_id);
CREATE INDEX IF NOT EXISTS idx_math_questions_template ON math_questions USING btree (template_type);
CREATE INDEX IF NOT EXISTS idx_math_questions_topic ON math_questions USING btree (topic);
CREATE INDEX IF NOT EXISTS idx_math_reviews_question_id ON math_reviews USING btree (math_question_id);
CREATE INDEX IF NOT EXISTS idx_math_progress_next_review ON math_template_progress USING btree (next_review_at);
