-- saved_offers: persists user job offers across devices
-- Run this in Supabase SQL Editor after creating your project.

CREATE TABLE IF NOT EXISTS public.saved_offers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  client_id TEXT NOT NULL,
  company TEXT NOT NULL,
  position TEXT NOT NULL,
  location TEXT NOT NULL,
  base_salary NUMERIC NOT NULL,
  equity NUMERIC DEFAULT 0,
  bonus NUMERIC DEFAULT 0,
  signing_bonus NUMERIC DEFAULT 0,
  total_compensation NUMERIC,
  years_experience INTEGER,
  vesting_years INTEGER DEFAULT 4,
  level TEXT,
  benefits_grade TEXT,
  wlb_grade TEXT,
  growth_grade TEXT,
  wlb_score NUMERIC,
  growth_score NUMERIC,
  work_type TEXT,
  employment_type TEXT,
  domain TEXT,
  job_description TEXT,
  other_perks TEXT,
  relocation_support BOOLEAN,
  currency TEXT DEFAULT 'USD',
  country TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_saved_offers_user_id ON public.saved_offers(user_id);
CREATE UNIQUE INDEX idx_saved_offers_user_client ON public.saved_offers(user_id, client_id);

-- Auto-update updated_at on row changes
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_saved_offers_updated_at
  BEFORE UPDATE ON public.saved_offers
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

ALTER TABLE public.saved_offers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own offers"
  ON public.saved_offers FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own offers"
  ON public.saved_offers FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own offers"
  ON public.saved_offers FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own offers"
  ON public.saved_offers FOR DELETE
  USING (auth.uid() = user_id);

COMMENT ON TABLE public.saved_offers IS 'Persists user job offers for cross-device access.';
COMMENT ON COLUMN public.saved_offers.client_id IS 'Frontend-generated ID (Date.now string) for upsert matching.';
