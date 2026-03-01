-- BenchMarked: per-user rate limiting (2 comparisons per user per day)
-- Run this in Supabase SQL Editor after creating your project.

CREATE TABLE IF NOT EXISTS public.user_usage (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  daily_count INT DEFAULT 0,
  last_used_date DATE DEFAULT CURRENT_DATE,
  total_analyses INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.user_usage ENABLE ROW LEVEL SECURITY;

-- Users can read their own usage row
CREATE POLICY "Users can read own usage"
  ON public.user_usage FOR SELECT
  USING (auth.uid() = user_id);

-- Backend uses service_role key (bypasses RLS) for INSERT/UPDATE
-- No policy needed for service_role; RLS is bypassed when using service_role key.

COMMENT ON TABLE public.user_usage IS 'Tracks daily comparison count per user for rate limiting (2/day).';
