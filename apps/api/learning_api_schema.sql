CREATE TABLE public.math_questions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    template_type text NOT NULL,
    topic text NOT NULL,
    params jsonb NOT NULL,
    correct_answer double precision NOT NULL,
    display_text text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);
ALTER TABLE public.math_questions OWNER TO postgres;
CREATE TABLE public.math_reviews (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    math_question_id uuid NOT NULL,
    user_answer double precision NOT NULL,
    is_correct boolean NOT NULL,
    llm_feedback text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);
ALTER TABLE public.math_reviews OWNER TO postgres;
CREATE TABLE public.math_template_progress (
    template_type text NOT NULL,
    ease_factor double precision DEFAULT 2.5,
    interval_days integer DEFAULT 0,
    next_review_at timestamp with time zone DEFAULT now(),
    total_attempts integer DEFAULT 0,
    correct_attempts integer DEFAULT 0
);
ALTER TABLE public.math_template_progress OWNER TO postgres;
CREATE TABLE public.questions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    question_text text NOT NULL,
    answer_text text,
    topic text NOT NULL,
    tags text[] DEFAULT '{}'::text[] NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    ease_factor double precision DEFAULT 2.5,
    interval_days integer DEFAULT 0,
    next_review_at timestamp with time zone DEFAULT now(),
    review_count integer DEFAULT 0
);
ALTER TABLE public.questions OWNER TO postgres;
CREATE TABLE public.reviews (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    question_id uuid NOT NULL,
    user_answer text NOT NULL,
    llm_feedback text NOT NULL,
    score integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);
ALTER TABLE public.reviews OWNER TO postgres;
ALTER TABLE ONLY public.math_questions
    ADD CONSTRAINT math_questions_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.math_reviews
    ADD CONSTRAINT math_reviews_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.math_template_progress
    ADD CONSTRAINT math_template_progress_pkey PRIMARY KEY (template_type);
ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (id);
CREATE INDEX idx_math_progress_next_review ON public.math_template_progress USING btree (next_review_at);
CREATE INDEX idx_math_questions_template ON public.math_questions USING btree (template_type);
CREATE INDEX idx_math_questions_topic ON public.math_questions USING btree (topic);
CREATE INDEX idx_math_reviews_question_id ON public.math_reviews USING btree (math_question_id);
CREATE INDEX idx_questions_next_review ON public.questions USING btree (next_review_at);
CREATE INDEX idx_questions_tags_gin ON public.questions USING gin (tags);
CREATE INDEX idx_questions_topic ON public.questions USING btree (topic);
CREATE INDEX idx_reviews_question_id ON public.reviews USING btree (question_id);
ALTER TABLE ONLY public.math_reviews
    ADD CONSTRAINT math_reviews_math_question_id_fkey FOREIGN KEY (math_question_id) REFERENCES public.math_questions(id) ON DELETE CASCADE;
ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(id) ON DELETE CASCADE;

