"""
Supabase JWT verification and per-user rate limiting (2 comparisons per day).
Used by FastAPI to protect /api/analyze and /api/analyze/quick.
"""

from __future__ import annotations

import os
from datetime import date, datetime, timezone
from typing import Optional

import jwt
from fastapi import HTTPException, Header
from supabase import create_client, Client

# Lazy-init Supabase client (requires env at runtime)
_supabase: Optional[Client] = None

DAILY_LIMIT = 2


def _get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise HTTPException(
                status_code=503,
                detail="Auth not configured (SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY missing)",
            )
        _supabase = create_client(url, key)
    return _supabase


def _get_jwt_secret() -> str:
    secret = os.environ.get("SUPABASE_JWT_SECRET")
    if not secret:
        raise HTTPException(
            status_code=503,
            detail="Auth not configured (SUPABASE_JWT_SECRET missing)",
        )
    return secret


def verify_jwt(authorization: Optional[str] = Header(None)) -> str:
    """Verify Supabase JWT and return user_id (UUID). Raises 401 if invalid/missing."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "").strip()
    secret = _get_jwt_secret()
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience="authenticated",
            options={"verify_exp": True},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from e
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return user_id


def check_and_consume_rate_limit(user_id: str) -> None:
    """
    Check per-user daily limit (2 comparisons). If under limit, increment and return.
    Raises 429 if limit reached. Uses Supabase user_usage table.
    """
    supabase = _get_supabase()
    today = date.today().isoformat()

    # Fetch current row
    row = supabase.table("user_usage").select("*").eq("user_id", user_id).execute()

    if not row.data or len(row.data) == 0:
        # First-time user: insert with daily_count = 1
        supabase.table("user_usage").insert({
            "user_id": user_id,
            "daily_count": 1,
            "last_used_date": today,
            "total_analyses": 1,
        }).execute()
        return

    data = row.data[0]
    last_date = data.get("last_used_date")
    daily_count = int(data.get("daily_count", 0))
    total = int(data.get("total_analyses", 0))

    now_iso = datetime.now(timezone.utc).isoformat()
    if last_date != today:
        # New day: reset daily count to 1
        supabase.table("user_usage").update({
            "daily_count": 1,
            "last_used_date": today,
            "total_analyses": total + 1,
            "updated_at": now_iso,
        }).eq("user_id", user_id).execute()
        return

    if daily_count >= DAILY_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Daily limit of {DAILY_LIMIT} comparisons reached. Resets at midnight.",
        )

    # Same day, under limit: increment
    supabase.table("user_usage").update({
        "daily_count": daily_count + 1,
        "total_analyses": total + 1,
        "updated_at": now_iso,
    }).eq("user_id", user_id).execute()


def get_usage(user_id: str) -> dict:
    """Return current user's usage for GET /api/usage (daily_count, limit, remaining)."""
    supabase = _get_supabase()
    today = date.today().isoformat()

    row = supabase.table("user_usage").select("*").eq("user_id", user_id).execute()

    if not row.data or len(row.data) == 0:
        return {"daily_count": 0, "daily_limit": DAILY_LIMIT, "remaining": DAILY_LIMIT}

    data = row.data[0]
    last_date = data.get("last_used_date")
    daily_count = int(data.get("daily_count", 0))

    if last_date != today:
        daily_count = 0

    remaining = max(0, DAILY_LIMIT - daily_count)
    return {
        "daily_count": daily_count,
        "daily_limit": DAILY_LIMIT,
        "remaining": remaining,
    }
