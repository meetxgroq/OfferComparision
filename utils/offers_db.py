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
