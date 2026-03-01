"""
Supabase JWT verification and per-user rate limiting (2 comparisons per day).
Used by FastAPI to protect /api/analyze and /api/analyze/quick.
"""

from __future__ import annotations

import os
from datetime import date, datetime, timezone
from typing import Optional

import requests
from fastapi import HTTPException, Header
from jose import jwt
from jose.exceptions import JWTError
from supabase import create_client, Client

# Lazy-init Supabase client (requires env at runtime)
_supabase: Optional[Client] = None
_jwks_cache: Optional[dict] = None
_jwks_cached_at: Optional[datetime] = None

DAILY_LIMIT = 2
SUPPORTED_JWKS_ALGS = {"ES256", "RS256"}
JWKS_CACHE_SECONDS = 300


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


def _get_supabase_url() -> str:
    url = os.environ.get("SUPABASE_URL")
    if not url:
        raise HTTPException(
            status_code=503,
            detail="Auth not configured (SUPABASE_URL missing)",
        )
    return url.rstrip("/")


def _should_refresh_jwks(now: datetime) -> bool:
    if _jwks_cache is None or _jwks_cached_at is None:
        return True
    age = (now - _jwks_cached_at).total_seconds()
    return age >= JWKS_CACHE_SECONDS


def _fetch_jwks(force_refresh: bool = False) -> dict:
    global _jwks_cache, _jwks_cached_at

    now = datetime.now(timezone.utc)
    if not force_refresh and not _should_refresh_jwks(now):
        return _jwks_cache

    supabase_url = _get_supabase_url()
    jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"

    try:
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        jwks = response.json()
    except requests.RequestException as exc:
        if _jwks_cache is not None:
            return _jwks_cache
        raise HTTPException(status_code=503, detail="Unable to fetch Supabase JWKS") from exc

    keys = jwks.get("keys") if isinstance(jwks, dict) else None
    if not isinstance(keys, list) or not keys:
        if _jwks_cache is not None:
            return _jwks_cache
        raise HTTPException(status_code=503, detail="Supabase JWKS is invalid or empty")

    _jwks_cache = jwks
    _jwks_cached_at = now
    return jwks


def _find_signing_key(token: str) -> dict:
    try:
        headers = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token header") from exc

    kid = headers.get("kid")
    if not kid:
        raise HTTPException(status_code=401, detail="Token missing key id (kid)")

    for force_refresh in (False, True):
        jwks = _fetch_jwks(force_refresh=force_refresh)
        key = next((item for item in jwks["keys"] if item.get("kid") == kid), None)
        if key:
            alg = key.get("alg")
            if alg and alg not in SUPPORTED_JWKS_ALGS:
                raise HTTPException(status_code=401, detail="Unsupported token signing algorithm")
            return key

    raise HTTPException(status_code=401, detail="Signing key not found for token")


def verify_jwt(authorization: Optional[str] = Header(None)) -> str:
    """Verify Supabase JWT and return user_id (UUID). Raises 401 if invalid/missing."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.replace("Bearer ", "").strip()
    supabase_url = _get_supabase_url()

    try:
        token_headers = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token header") from exc

    token_alg = token_headers.get("alg")
    if token_alg not in SUPPORTED_JWKS_ALGS:
        raise HTTPException(status_code=401, detail="Unsupported token signing algorithm")

    key = _find_signing_key(token)
    decode_algorithms = list(SUPPORTED_JWKS_ALGS)

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=decode_algorithms,
            audience="authenticated",
            issuer=f"{supabase_url}/auth/v1",
        )
    except JWTError as e:
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
