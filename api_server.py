"""
OfferCompare Pro - FastAPI Server

Endpoints:
- GET  /health            -> health check
- GET  /api/demo          -> run analysis on sample offers
- POST /api/analyze       -> run analysis on posted offers and preferences

Run:
  uvicorn api_server:app --reload --port 8000
"""

from __future__ import annotations

import os
from typing import List, Dict, Any, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from flow import get_sample_offers, create_quick_analysis_flow
from utils.json_sanitize import sanitize_for_json
from utils.auth import (
    verify_jwt,
    check_and_consume_rate_limit,
    get_usage as get_usage_data,
)
from nodes import (
    MarketResearchNode,
    TaxCalculationNode,
    COLAnalysisNode,
    MarketBenchmarkingNode,
    PreferenceScoringNode,
    AIAnalysisNode,
    VisualizationPreparationNode,
    ReportGenerationNode,
)
from pocketflow import Flow, AsyncFlow
from utils.call_llm import get_provider_info


class Offer(BaseModel):
    id: Optional[str] = None
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
    level: Optional[str] = None  # Internal company level (e.g. "61", "IC3")
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


class AnalyzeRequest(BaseModel):
    offers: List[Offer] = Field(default_factory=list)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)


class AnalyzeResponse(BaseModel):
    executive_summary: str
    final_report: Dict[str, Any]
    comparison_results: Dict[str, Any]
    visualization_data: Dict[str, Any]
    offers: List[Dict[str, Any]]


app = FastAPI(title="BenchMarked API", version="1.0.0")

_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001")
_origins_list = [o.strip() for o in _origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _require_auth_and_rate_limit(authorization: Optional[str] = Header(None)) -> str:
    """Verify JWT and consume one rate-limit slot. Returns user_id."""
    user_id = verify_jwt(authorization)
    check_and_consume_rate_limit(user_id)
    return user_id


@app.get("/health")
def health() -> Dict[str, Any]:
    provider_info = get_provider_info()
    return {"status": "ok", "providers": provider_info}


from utils.levels import get_level_suggestions

@app.get("/api/levels", response_model=Dict[str, List[str]])
def get_levels(company: str, position: str = "Software Engineer") -> Dict[str, List[str]]:
    """Get common levels for a specific company and position."""
    # Force reload
    levels = get_level_suggestions(company, position)
    return {"levels": levels}

from utils.positions import get_all_positions

@app.get("/api/positions", response_model=Dict[str, List[str]])
def get_positions() -> Dict[str, List[str]]:
    """Get all common position suggestions."""
    return {"positions": get_all_positions()}


@app.get("/api/usage")
def get_usage(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Return current user's daily usage (count, limit, remaining). Requires auth."""
    user_id = verify_jwt(authorization)
    return get_usage_data(user_id)


def _build_flow() -> AsyncFlow:
    market_research = MarketResearchNode()
    tax_calculation = TaxCalculationNode()
    col_analysis = COLAnalysisNode()
    market_benchmarking = MarketBenchmarkingNode()
    preference_scoring = PreferenceScoringNode()
    ai_analysis = AIAnalysisNode()
    visualization_prep = VisualizationPreparationNode()
    report_generation = ReportGenerationNode()

    market_research >> tax_calculation
    tax_calculation >> col_analysis
    col_analysis >> market_benchmarking
    market_benchmarking >> preference_scoring
    preference_scoring >> ai_analysis
    ai_analysis >> visualization_prep
    visualization_prep >> report_generation

    return AsyncFlow(start=market_research)


async def _run_analysis(shared: Dict[str, Any]) -> Dict[str, Any]:
    flow = _build_flow()
    await flow.run_async(shared)
    return shared


@app.get("/api/demo", response_model=AnalyzeResponse)
async def run_demo() -> AnalyzeResponse:
    shared = get_sample_offers()

    # Ensure totals are present
    for offer in shared["offers"]:
        offer.setdefault("total_compensation", offer.get("base_salary", 0) + offer.get("equity", 0) + offer.get("bonus", 0))

    try:
        result = await _run_analysis(shared)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    result = sanitize_for_json(result)
    return AnalyzeResponse(
        executive_summary=result.get("executive_summary", ""),
        final_report=result.get("final_report", {}),
        comparison_results=result.get("comparison_results", {}),
        visualization_data=result.get("visualization_data", {}),
        offers=result.get("offers", []),
    )


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(
    req: AnalyzeRequest,
    _user_id: str = Depends(_require_auth_and_rate_limit),
) -> AnalyzeResponse:
    if not req.offers:
        raise HTTPException(status_code=400, detail="Offers list cannot be empty")

    # Prepare shared store
    offers = []
    for i, o in enumerate(req.offers, start=1):
        data = o.model_dump()
        data["id"] = data.get("id") or f"offer_{i}"
        if data.get("total_compensation") is None:
            data["total_compensation"] = data.get("base_salary", 0) + data.get("equity", 0) + data.get("bonus", 0)
        offers.append(data)

    shared = {
        "offers": offers,
        "user_preferences": req.user_preferences or {},
    }

    try:
        result = await _run_analysis(shared)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    result = sanitize_for_json(result)
    return AnalyzeResponse(
        executive_summary=result.get("executive_summary", ""),
        final_report=result.get("final_report", {}),
        comparison_results=result.get("comparison_results", {}),
        visualization_data=result.get("visualization_data", {}),
        offers=result.get("offers", []),
    )


async def _run_quick_analysis(shared: Dict[str, Any]) -> Dict[str, Any]:
    """Run quick analysis flow."""
    flow = create_quick_analysis_flow()
    await flow.run_async(shared)
    return shared


@app.post("/api/analyze/quick", response_model=AnalyzeResponse)
async def analyze_quick(
    req: AnalyzeRequest,
    _user_id: str = Depends(_require_auth_and_rate_limit),
) -> AnalyzeResponse:
    """
    Quick analysis endpoint - faster results with essential insights.
    Uses combined nodes and cached data for <1 minute analysis.
    """
    if not req.offers:
        raise HTTPException(status_code=400, detail="Offers list cannot be empty")

    # Prepare shared store
    offers = []
    for i, o in enumerate(req.offers, start=1):
        data = o.model_dump()
        data["id"] = data.get("id") or f"offer_{i}"
        if data.get("total_compensation") is None:
            data["total_compensation"] = data.get("base_salary", 0) + data.get("equity", 0) + data.get("bonus", 0)
        offers.append(data)

    shared = {
        "offers": offers,
        "user_preferences": req.user_preferences or {},
    }

    try:
        result = await _run_quick_analysis(shared)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    result = sanitize_for_json(result)
    return AnalyzeResponse(
        executive_summary=result.get("executive_summary", ""),
        final_report=result.get("final_report", {}),
        comparison_results=result.get("comparison_results", {}),
        visualization_data=result.get("visualization_data", {}),
        offers=result.get("offers", []),
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
