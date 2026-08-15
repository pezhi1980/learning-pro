-- ============================================================
-- Learning Lang Pro — Version-Controlled Supabase DDL Schema
-- File: backend/data/schema.sql
-- ============================================================

-- ── Extensions ─────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Enum Types ─────────────────────────────────────────────
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('user', 'admin');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ── 1. Languages Table ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS languages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    native_name TEXT NOT NULL,
    flag TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    order_index INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 2. Levels Table ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    order_index INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 3. Profiles Table ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    first_name TEXT DEFAULT '',
    last_name TEXT DEFAULT '',
    email TEXT UNIQUE NOT NULL,
    role user_role DEFAULT 'user',
    native_language TEXT DEFAULT 'fa',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 4. Grammar Topics Table ────────────────────────────────
CREATE TABLE IF NOT EXISTS grammar_topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    language_id UUID REFERENCES languages(id) ON DELETE CASCADE,
    level_id UUID REFERENCES levels(id) ON DELETE CASCADE,
    topic_code TEXT NOT NULL,
    title TEXT,
    order_index INT DEFAULT 0,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 5. Grammar Content Table ───────────────────────────────
CREATE TABLE IF NOT EXISTS grammar_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id UUID REFERENCES grammar_topics(id) ON DELETE CASCADE,
    native_language TEXT DEFAULT 'fa',
    title TEXT NOT NULL,
    explanation TEXT NOT NULL,
    comparison TEXT,
    examples_json JSONB DEFAULT '[]'::jsonb,
    tips_json JSONB DEFAULT '[]'::jsonb,
    common_mistakes_json JSONB DEFAULT '[]'::jsonb,
    quality_score FLOAT DEFAULT 1.0,
    generation_model TEXT DEFAULT 'gpt-4o',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 6. Grammar Contrast Table ──────────────────────────────
CREATE TABLE IF NOT EXISTS grammar_contrast (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id UUID REFERENCES grammar_topics(id) ON DELETE CASCADE,
    target_language TEXT DEFAULT 'en',
    native_language TEXT DEFAULT 'fa',
    differences JSONB DEFAULT '[]'::jsonb,
    tips JSONB DEFAULT '[]'::jsonb,
    examples JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 7. Vocabulary Table ────────────────────────────────────
CREATE TABLE IF NOT EXISTS vocabulary (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    language_id UUID REFERENCES languages(id) ON DELETE CASCADE,
    level_id UUID REFERENCES levels(id) ON DELETE CASCADE,
    lexeme TEXT NOT NULL,
    pos TEXT,
    sense_id TEXT,
    guideword TEXT,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 8. Vocabulary Translations Table ───────────────────────
CREATE TABLE IF NOT EXISTS vocabulary_translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vocabulary_id UUID REFERENCES vocabulary(id) ON DELETE CASCADE,
    native_language TEXT DEFAULT 'fa',
    translation TEXT NOT NULL,
    definition TEXT,
    examples_json JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 9. Flashcards Table ────────────────────────────────────
CREATE TABLE IF NOT EXISTS flashcards_with_vocab (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    language_id UUID REFERENCES languages(id) ON DELETE CASCADE,
    level_id UUID REFERENCES levels(id) ON DELETE CASCADE,
    native_language TEXT DEFAULT 'fa',
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    example TEXT,
    is_approved BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 10. Exercises Table ────────────────────────────────────
CREATE TABLE IF NOT EXISTS exercises (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    language_id UUID REFERENCES languages(id) ON DELETE CASCADE,
    level_id UUID REFERENCES levels(id) ON DELETE CASCADE,
    topic_id UUID REFERENCES grammar_topics(id) ON DELETE SET NULL,
    type TEXT NOT NULL DEFAULT 'multiple_choice',
    prompt TEXT NOT NULL,
    options JSONB DEFAULT '[]'::jsonb,
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    native_language TEXT DEFAULT 'fa',
    is_approved BOOLEAN DEFAULT TRUE,
    quality_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 11. User Progress Table ────────────────────────────────
CREATE TABLE IF NOT EXISTS user_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    language_id UUID REFERENCES languages(id) ON DELETE CASCADE,
    level_id UUID REFERENCES levels(id) ON DELETE CASCADE,
    topic_id UUID REFERENCES grammar_topics(id) ON DELETE SET NULL,
    total_attempts INT DEFAULT 0,
    correct_attempts INT DEFAULT 0,
    mastery_score FLOAT DEFAULT 0.0,
    last_attempt_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Indexes for Performance ────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_grammar_topics_lang_level ON grammar_topics(language_id, level_id);
CREATE INDEX IF NOT EXISTS idx_grammar_content_topic_lang ON grammar_content(topic_id, native_language);
CREATE INDEX IF NOT EXISTS idx_exercises_topic_approved ON exercises(topic_id, is_approved);
CREATE INDEX IF NOT EXISTS idx_user_progress_user ON user_progress(user_id, language_id, level_id);

-- ── Stored Procedures & Triggers ───────────────────────────

-- 1. Trigger for New Users
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS trigger AS $$
BEGIN
    INSERT INTO profiles (id, first_name, last_name, email, role, native_language, created_at, updated_at)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'first_name', ''),
        COALESCE(NEW.raw_user_meta_data->>'last_name', ''),
        NEW.email,
        'user'::user_role,
        COALESCE(NEW.raw_user_meta_data->>'native_language', 'fa'),
        NOW(),
        NOW()
    );
    RETURN NEW;
EXCEPTION WHEN OTHERS THEN
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Update User Progress Procedure
CREATE OR REPLACE FUNCTION update_user_progress(
    p_user_id UUID,
    p_language_id UUID,
    p_level_id UUID,
    p_topic_id UUID,
    p_is_correct BOOLEAN
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO user_progress (user_id, language_id, level_id, topic_id, total_attempts, correct_attempts, last_attempt_at, updated_at)
    VALUES (
        p_user_id, p_language_id, p_level_id, p_topic_id, 1, CASE WHEN p_is_correct THEN 1 ELSE 0 END, NOW(), NOW()
    )
    ON CONFLICT (user_id, language_id, level_id, topic_id) DO UPDATE SET
        total_attempts = user_progress.total_attempts + 1,
        correct_attempts = user_progress.correct_attempts + CASE WHEN p_is_correct THEN 1 ELSE 0 END,
        last_attempt_at = NOW(),
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. Get Weak Topics Procedure
CREATE OR REPLACE FUNCTION get_weak_topics(
    p_user_id UUID,
    p_language_id UUID,
    p_level_id UUID,
    p_limit INT DEFAULT 5
)
RETURNS TABLE (
    topic_id UUID,
    title TEXT,
    accuracy FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        gt.id AS topic_id,
        gt.title,
        (up.correct_attempts::FLOAT / NULLIF(up.total_attempts, 0)) AS accuracy
    FROM user_progress up
    JOIN grammar_topics gt ON up.topic_id = gt.id
    WHERE up.user_id = p_user_id
      AND up.language_id = p_language_id
      AND up.level_id = p_level_id
      AND (up.correct_attempts::FLOAT / NULLIF(up.total_attempts, 0)) < 0.70
    ORDER BY accuracy ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
