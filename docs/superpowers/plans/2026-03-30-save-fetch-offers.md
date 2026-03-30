# Save & Fetch Offers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist user offers to Supabase so they survive across devices/browsers and can be loaded during comparison.

**Architecture:** New `saved_offers` table in Supabase with RLS. Backend gets CRUD endpoints (`GET/POST/DELETE /api/offers`) authenticated via existing `verify_jwt` dependency (no rate limit needed for offer CRUD). Frontend auto-syncs on login and debounce-saves on change, with localStorage as offline fallback.

**Tech Stack:** Supabase (Postgres + RLS), FastAPI (Python), Next.js/React (TypeScript), Axios

---

## File Structure

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `supabase/migrations/002_saved_offers.sql` | DB schema + RLS + updated_at trigger |
| Create | `utils/offers_db.py` | CRUD operations for offers in Supabase |
| Modify | `api_server.py` | New REST endpoints for offer persistence |
| Create | `frontend/lib/offers-api.ts` | Frontend API client (reuses `@/lib/api`) |
| Modify | `frontend/app/page.tsx` | Cloud sync logic on login/change + status badge |
| Create | `tests/test_offers_db.py` | Backend unit tests |

---

### Task 1: Database Migration

**Files:**
- Create: `supabase/migrations/002_saved_offers.sql`

- [ ] **Step 1: Write the migration SQL**

```sql
-- saved_offers: persists user job offers across devices
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
COMMENT ON COLUMN public.saved_offers.client_id IS 'Frontend-generated ID (Date.now string) for upsert matching. NOT NULL.';
```

Notes:
- `client_id NOT NULL` prevents duplicates from NULL uniqueness behavior.
- `years_experience` included for full parity with backend `Offer` model.
- `set_updated_at()` trigger auto-maintains `updated_at` on every UPDATE.
- RLS policies are per-operation. Backend uses `SUPABASE_SERVICE_ROLE_KEY` (bypasses RLS); policies protect direct Supabase client access.

- [ ] **Step 2: Apply migration to Supabase**

Run in Supabase SQL Editor or via CLI:
```bash
# If using Supabase CLI:
supabase db push
# Otherwise: paste the SQL into Supabase Dashboard > SQL Editor > Run
```

- [ ] **Step 3: Commit**

```bash
git add supabase/migrations/002_saved_offers.sql
git commit -m "feat(db): add saved_offers table with RLS and updated_at trigger"
```

---

### Task 2: Backend CRUD Module

**Files:**
- Create: `utils/offers_db.py`
- Test: `tests/test_offers_db.py`

- [ ] **Step 1: Write failing tests for offers_db**

Create `tests/test_offers_db.py`:

```python
"""Tests for utils/offers_db.py CRUD operations."""
import pytest
from unittest.mock import MagicMock, patch

SAMPLE_OFFER = {
    "client_id": "1711700000000",
    "company": "Acme Corp",
    "position": "Senior Engineer",
    "location": "San Francisco, CA",
    "base_salary": 200000,
    "equity": 50000,
    "bonus": 20000,
    "currency": "USD",
}


@patch("utils.offers_db._get_supabase")
def test_list_offers_returns_list(mock_sb):
    from utils.offers_db import list_offers
    mock_sb.return_value.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = [SAMPLE_OFFER]
    result = list_offers("user-uuid-123")
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["company"] == "Acme Corp"


@patch("utils.offers_db._get_supabase")
def test_upsert_offers_calls_upsert(mock_sb):
    from utils.offers_db import upsert_offers
    mock_sb.return_value.table.return_value.upsert.return_value.execute.return_value.data = [SAMPLE_OFFER]
    result = upsert_offers("user-uuid-123", [SAMPLE_OFFER])
    assert isinstance(result, list)
    mock_sb.return_value.table.return_value.upsert.assert_called_once()


@patch("utils.offers_db._get_supabase")
def test_delete_offer_by_id(mock_sb):
    from utils.offers_db import delete_offer
    mock_sb.return_value.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock()
    delete_offer("user-uuid-123", "some-uuid")
    mock_sb.return_value.table.return_value.delete.assert_called_once()


@patch("utils.offers_db._get_supabase")
def test_delete_offer_by_client_id(mock_sb):
    from utils.offers_db import delete_offer_by_client_id
    mock_sb.return_value.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock()
    delete_offer_by_client_id("user-uuid-123", "1711700000000")
    mock_sb.return_value.table.return_value.delete.assert_called_once()


@patch("utils.offers_db._get_supabase")
def test_upsert_filters_to_known_columns(mock_sb):
    from utils.offers_db import upsert_offers
    offer_with_extras = {**SAMPLE_OFFER, "unknown_field": "should_be_dropped"}
    mock_sb.return_value.table.return_value.upsert.return_value.execute.return_value.data = [SAMPLE_OFFER]
    upsert_offers("user-uuid-123", [offer_with_extras])
    call_args = mock_sb.return_value.table.return_value.upsert.call_args[0][0]
    assert "unknown_field" not in call_args[0]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_offers_db.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'utils.offers_db'`

- [ ] **Step 3: Implement `utils/offers_db.py`**

```python
"""CRUD operations for saved_offers in Supabase."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from utils.auth import _get_supabase

logger = logging.getLogger(__name__)

TABLE = "saved_offers"

OFFER_COLUMNS = frozenset([
    "id", "client_id", "company", "position", "location",
    "base_salary", "equity", "bonus", "signing_bonus",
    "total_compensation", "years_experience", "vesting_years", "level",
    "benefits_grade", "wlb_grade", "growth_grade",
    "wlb_score", "growth_score", "work_type", "employment_type",
    "domain", "job_description", "other_perks",
    "relocation_support", "currency", "country",
])


def list_offers(user_id: str) -> List[Dict[str, Any]]:
    sb = _get_supabase()
    resp = sb.table(TABLE).select("*").eq("user_id", user_id).order("created_at").execute()
    return resp.data or []


def upsert_offers(user_id: str, offers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sb = _get_supabase()
    rows = []
    for o in offers:
        row: Dict[str, Any] = {"user_id": user_id}
        for col in OFFER_COLUMNS:
            if col in o and o[col] is not None:
                row[col] = o[col]
        if "client_id" not in row or not row["client_id"]:
            logger.warning("Skipping offer without client_id: %s", o.get("company"))
            continue
        rows.append(row)
    if not rows:
        return []
    resp = sb.table(TABLE).upsert(rows, on_conflict="user_id,client_id").execute()
    return resp.data or []


def delete_offer(user_id: str, offer_id: str) -> None:
    sb = _get_supabase()
    sb.table(TABLE).delete().eq("user_id", user_id).eq("id", offer_id).execute()


def delete_offer_by_client_id(user_id: str, client_id: str) -> None:
    sb = _get_supabase()
    sb.table(TABLE).delete().eq("user_id", user_id).eq("client_id", client_id).execute()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_offers_db.py -v
```
Expected: 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add utils/offers_db.py tests/test_offers_db.py
git commit -m "feat(offers-db): add CRUD module for saved_offers"
```

---

### Task 3: Backend API Endpoints

**Files:**
- Modify: `api_server.py` (add endpoints after existing routes)

- [ ] **Step 1: Add imports and Pydantic models**

At the top of `api_server.py`, add to existing imports:

```python
from utils.offers_db import list_offers, upsert_offers, delete_offer, delete_offer_by_client_id
```

After the `AnalyzeResponse` class, add:

```python
class SaveOffersRequest(BaseModel):
    offers: List[Offer] = Field(default_factory=list)


class SavedOfferResponse(BaseModel):
    id: str
    client_id: Optional[str] = None
    company: str
    position: str
    location: str
    base_salary: float
    equity: float = 0
    bonus: float = 0
    signing_bonus: Optional[float] = 0
    total_compensation: Optional[float] = None
    years_experience: Optional[int] = None
    vesting_years: Optional[int] = 4
    level: Optional[str] = None
    benefits_grade: Optional[str] = None
    wlb_grade: Optional[str] = None
    growth_grade: Optional[str] = None
    wlb_score: Optional[float] = None
    growth_score: Optional[float] = None
    work_type: Optional[str] = None
    employment_type: Optional[str] = None
    domain: Optional[str] = None
    job_description: Optional[str] = None
    other_perks: Optional[str] = None
    relocation_support: Optional[bool] = None
    currency: Optional[str] = None
    country: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
```

- [ ] **Step 2: Add GET /api/offers endpoint**

Uses `verify_jwt` directly as a FastAPI dependency (it already takes `authorization: Optional[str] = Header(None)` and returns `user_id`). No rate limiting needed for offer CRUD.

```python
@app.get("/api/offers", response_model=List[SavedOfferResponse])
async def get_offers(user_id: str = Depends(verify_jwt)):
    """Fetch all saved offers for the authenticated user."""
    return list_offers(user_id)
```

- [ ] **Step 3: Add POST /api/offers endpoint**

```python
@app.post("/api/offers", response_model=List[SavedOfferResponse])
async def save_offers(req: SaveOffersRequest, user_id: str = Depends(verify_jwt)):
    """Upsert (save/update) offers for the authenticated user."""
    if not req.offers:
        raise HTTPException(status_code=400, detail="Offers list cannot be empty")
    offer_dicts = []
    for o in req.offers:
        d = o.model_dump()
        d["client_id"] = d.pop("id", None)
        offer_dicts.append(d)
    return upsert_offers(user_id, offer_dicts)
```

- [ ] **Step 4: Add DELETE /api/offers/{offer_id} endpoint**

Supports both Supabase UUID (`id`) and frontend client ID via query param `by`.

```python
@app.delete("/api/offers/{offer_id}")
async def remove_offer(offer_id: str, by: str = "id", user_id: str = Depends(verify_jwt)):
    """Delete a saved offer by Supabase UUID (default) or by client_id (?by=client_id)."""
    if by == "client_id":
        delete_offer_by_client_id(user_id, offer_id)
    else:
        delete_offer(user_id, offer_id)
    return {"status": "deleted"}
```

- [ ] **Step 5: Restart backend and smoke-test with curl**

```bash
# Restart backend
kill $(lsof -ti:8001) 2>/dev/null; sleep 1
source .venv/bin/activate && python api_server.py &

# Test GET (use a valid JWT from browser dev tools):
TOKEN="<paste-jwt-here>"
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/offers | python3 -m json.tool
# Expected: [] (empty list for new user)
```

- [ ] **Step 6: Commit**

```bash
git add api_server.py
git commit -m "feat(api): add CRUD endpoints for saved offers"
```

---

### Task 4: Frontend API Client

**Files:**
- Create: `frontend/lib/offers-api.ts`

- [ ] **Step 1: Create the API client module**

Reuses `getApiBase` and `authHeaders` from `@/lib/api` to avoid duplication.

```typescript
import axios from 'axios'
import { getApiBase, authHeaders } from '@/lib/api'
import type { Offer } from '@/types'

export interface SavedOffer {
  id: string
  client_id: string | null
  company: string
  position: string
  location: string
  base_salary: number
  equity: number
  bonus: number
  signing_bonus?: number
  total_compensation?: number
  years_experience?: number
  vesting_years?: number
  level?: string
  benefits_grade?: string
  wlb_grade?: string
  growth_grade?: string
  wlb_score?: number
  growth_score?: number
  work_type?: string
  employment_type?: string
  domain?: string
  job_description?: string
  other_perks?: string
  relocation_support?: boolean
  currency?: string
  country?: string
  created_at?: string
  updated_at?: string
}

export async function fetchSavedOffers(token: string): Promise<SavedOffer[]> {
  const res = await axios.get(`${getApiBase()}/api/offers`, {
    headers: authHeaders(token),
  })
  return res.data
}

export async function saveOffersToCloud(
  token: string,
  offers: Offer[]
): Promise<SavedOffer[]> {
  const res = await axios.post(
    `${getApiBase()}/api/offers`,
    { offers },
    { headers: authHeaders(token) }
  )
  return res.data
}

export async function deleteOfferFromCloud(
  token: string,
  clientId: string
): Promise<void> {
  await axios.delete(`${getApiBase()}/api/offers/${clientId}?by=client_id`, {
    headers: authHeaders(token),
  })
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/lib/offers-api.ts
git commit -m "feat(frontend): add offers API client"
```

---

### Task 5: Frontend Cloud Sync

**Files:**
- Modify: `frontend/app/page.tsx`

Sync strategy (simple and reliable):
- On login: fetch cloud offers, add any that are missing locally (by `client_id` match)
- On offer add/edit: debounced save to cloud after 2s of inactivity
- On offer delete: remove from cloud immediately via `deleteOfferFromCloud`
- **Accepted limitation:** "cloud fills in missing offers only" -- no timestamp-based conflict resolution. If the same offer exists locally and in the cloud with different data, local version wins.

- [ ] **Step 1: Add imports and sync state**

At the top of `page.tsx`, add:
```typescript
import { fetchSavedOffers, saveOffersToCloud, deleteOfferFromCloud } from '@/lib/offers-api'
```

Add state and ref inside the component:
```typescript
const [cloudSyncStatus, setCloudSyncStatus] = useState<'idle' | 'syncing' | 'synced' | 'error'>('idle')
const saveTimerRef = useRef<NodeJS.Timeout | null>(null)
```

- [ ] **Step 2: Add cloud fetch on login**

Add a `useEffect` that runs when `user` changes:

```typescript
useEffect(() => {
  if (!user) {
    setCloudSyncStatus('idle')
    return
  }
  let cancelled = false
  const syncFromCloud = async () => {
    try {
      setCloudSyncStatus('syncing')
      const token = await getAccessToken()
      if (!token || cancelled) return
      const cloudOffers = await fetchSavedOffers(token)
      if (cancelled) return

      setOffers(prev => {
        const localIds = new Set(prev.map(o => o.id))
        const newFromCloud = cloudOffers
          .filter(co => !localIds.has(co.client_id || co.id))
          .map(co => ({ ...co, id: co.client_id || co.id } as any))
        if (newFromCloud.length === 0) return prev
        return [...prev, ...newFromCloud]
      })
      setCloudSyncStatus('synced')
    } catch (e) {
      console.error('Cloud sync failed:', e)
      setCloudSyncStatus('error')
    }
  }
  syncFromCloud()
  return () => { cancelled = true }
}, [user])
```

- [ ] **Step 3: Add debounced save-to-cloud on offer changes**

```typescript
useEffect(() => {
  if (!user || offers.length === 0) return
  if (saveTimerRef.current) clearTimeout(saveTimerRef.current)
  saveTimerRef.current = setTimeout(async () => {
    try {
      const token = await getAccessToken()
      if (!token) return
      await saveOffersToCloud(token, offers)
      setCloudSyncStatus('synced')
    } catch (e) {
      console.error('Cloud save failed:', e)
      setCloudSyncStatus('error')
    }
  }, 2000)
  return () => {
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current)
  }
}, [offers, user])
```

- [ ] **Step 4: Wire delete to also remove from cloud**

In the existing `handleRemoveOffer` (or equivalent), after removing from local state:

```typescript
if (user) {
  getAccessToken().then(token => {
    if (token) deleteOfferFromCloud(token, offerId).catch(console.error)
  })
}
```

- [ ] **Step 5: Add sync status indicator in the UI**

Near the "Your Job Offers" heading, add a small badge:

```tsx
{user && cloudSyncStatus !== 'idle' && (
  <span className={`text-xs px-2 py-0.5 rounded-full ${
    cloudSyncStatus === 'syncing' ? 'bg-yellow-500/20 text-yellow-400' :
    cloudSyncStatus === 'synced' ? 'bg-green-500/20 text-green-400' :
    'bg-red-500/20 text-red-400'
  }`}>
    {cloudSyncStatus === 'syncing' ? 'Syncing...' :
     cloudSyncStatus === 'synced' ? 'Saved to cloud' :
     'Sync failed'}
  </span>
)}
```

- [ ] **Step 6: Commit**

```bash
git add frontend/app/page.tsx
git commit -m "feat(frontend): auto-sync offers with cloud on login"
```

---

### Task 6: Integration Testing

- [ ] **Step 1: Test full flow manually**

1. Start backend: `source .venv/bin/activate && python api_server.py`
2. Start frontend: `cd frontend && npm run dev`
3. Sign in with Google
4. Add 2 offers via the form
5. Verify: sync badge shows "Saved to cloud"
6. Open a new incognito window, sign in with same account
7. Verify: offers load from cloud

- [ ] **Step 2: Test edge cases**

1. Add offers while logged out -> works (localStorage only), no cloud badge
2. Log in -> offers sync to cloud, badge shows "Saved to cloud"
3. Delete an offer -> removed from both local and cloud
4. Log out and back in -> offers persist from cloud
5. Clear all data (existing button) while logged in -> localStorage cleared; cloud retains data (accepted limitation, documented above)

- [ ] **Step 3: Run all existing tests to check for regressions**

```bash
pytest tests/ -v
```
Expected: All tests pass (including new `test_offers_db.py`)

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: save and fetch offers from Supabase cloud"
```

---

## Known Limitations & Future Work

1. **No conflict resolution:** If the same offer (by `client_id`) has different content locally vs cloud, local wins. A future enhancement could compare `updated_at` timestamps.
2. **"Clear all" doesn't clear cloud:** The existing "Clear All Data" button only clears localStorage. A future enhancement could add a "Clear cloud data" option.
3. **No offline queue:** If the user modifies offers while offline, changes won't sync until the next page load when online and logged in.
