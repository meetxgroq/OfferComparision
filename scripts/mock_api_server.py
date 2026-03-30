from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json

app = FastAPI(title="OfferCompare Pro API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Offer(BaseModel):
    company: str
    position: str
    location: str
    base_salary: float
    equity: Optional[float] = 0
    bonus: Optional[float] = 0
    benefits_grade: Optional[str] = "B"
    wlb_score: Optional[float] = 7.0
    growth_score: Optional[float] = 7.0
    role_fit: Optional[float] = 7.0

class UserPreferences(BaseModel):
    salary_weight: Optional[float] = 0.3
    equity_weight: Optional[float] = 0.2
    wlb_weight: Optional[float] = 0.2
    growth_weight: Optional[float] = 0.15
    culture_weight: Optional[float] = 0.1
    benefits_weight: Optional[float] = 0.05

class AnalyzeRequest(BaseModel):
    offers: List[Offer]
    user_preferences: Optional[UserPreferences] = None

@app.get("/health")
def health():
    return {"status": "ok", "providers": {"mock": True}}

@app.post("/api/demo")
async def demo():
    # Mock response for demo - matches real API structure
    mock_ranked_offers = [
        {
            "offer_id": "mock_1",
            "company": "Mock Company A",
            "position": "Senior Software Engineer",
            "location": "San Francisco, CA",
            "total_score": 8.5,
            "rating": "Excellent",
            "score_breakdown": {
                "compensation_score": 8.2,
                "growth_score": 9.0,
                "wlb_score": 7.5,
                "culture_score": 8.0,
                "benefits_score": 7.8
            },
            "offer_data": {
                "id": "mock_1",
                "company": "Mock Company A",
                "base_salary": 200000,
                "equity": 50000,
                "bonus": 25000
            },
            "rank": 1,
            "score_gap": 0
        },
        {
            "offer_id": "mock_2",
            "company": "Mock Company B",
            "position": "Software Engineer",
            "location": "Seattle, WA",
            "total_score": 7.8,
            "rating": "Good",
            "score_breakdown": {
                "compensation_score": 7.5,
                "growth_score": 8.2,
                "wlb_score": 8.0,
                "culture_score": 7.5,
                "benefits_score": 7.6
            },
            "offer_data": {
                "id": "mock_2",
                "company": "Mock Company B",
                "base_salary": 180000,
                "equity": 40000,
                "bonus": 20000
            },
            "rank": 2,
            "score_gap": 0.7
        }
    ]
    
    return {
        "executive_summary": "Mock analysis complete! This is a demonstration of the OfferCompare Pro system.",
        "final_report": {
            "detailed_analysis": "Based on our comprehensive analysis, Mock Company A offers the best overall package.\n\nThis recommendation considers multiple factors including total compensation, growth potential, and work-life balance.\n\nThe equity component provides significant upside potential, while the base salary is competitive for the San Francisco market.",
            "decision_framework": "When making your final decision, consider your personal priorities and career goals.\n\nFocus on long-term value creation rather than just immediate compensation.\n\nConsider the company's trajectory and your role in their growth story.",
            "offer_rankings": [
                {
                    "offer_id": "mock_1",
                    "company": "Mock Company A",
                    "position": "Senior Software Engineer",
                    "total_score": 8.5,
                    "rank": 1,
                    "ai_recommendation": "Strong recommendation - excellent growth potential with competitive compensation package."
                },
                {
                    "offer_id": "mock_2",
                    "company": "Mock Company B",
                    "position": "Software Engineer",
                    "total_score": 7.8,
                    "rank": 2,
                    "ai_recommendation": "Good option - solid choice with strong engineering culture and work-life balance."
                }
            ]
        },
        "comparison_results": {
            "ranked_offers": mock_ranked_offers,
            "top_offer": mock_ranked_offers[0],
            "comparison_summary": "Top choice: Mock Company A (Score: 8.5). Analysis of 2 demo offers completed.",
            "weights_used": {
                "compensation_weight": 0.30,
                "growth_weight": 0.20,
                "wlb_weight": 0.20,
                "culture_weight": 0.15,
                "benefits_weight": 0.15
            }
        },
        "visualization_data": {
            "radar_chart": {
                "labels": ["Compensation", "Growth", "Work-Life Balance", "Culture"],
                "datasets": [
                    {
                        "label": "Mock Company A",
                        "data": [8, 9, 7, 8],
                        "backgroundColor": "rgba(59, 130, 246, 0.2)",
                        "borderColor": "rgb(59, 130, 246)"
                    }
                ]
            },
            "comparison_table": [
                {
                    "company": "Mock Company A",
                    "total_compensation": 250000,
                    "col_adjusted": 225000,
                    "score": 8.5
                }
            ]
        },
        "offers": [
            {
                "id": "mock_1",
                "company": "Mock Company A",
                "position": "Senior Software Engineer",
                "location": "San Francisco, CA",
                "base_salary": 200000,
                "equity": 50000,
                "bonus": 25000,
                "total_score": 8.5,
                "col_adjusted_salary": 180000,
                "market_percentile": 75
            }
        ]
        }

@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        # Mock processing of real offers
        processed_offers = []
        for i, offer in enumerate(req.offers):
            processed_offer = {
                "id": f"offer_{i+1}",
                "company": offer.company,
                "position": offer.position,
                "location": offer.location,
                "base_salary": offer.base_salary,
                "equity": offer.equity or 0,
                "bonus": offer.bonus or 0,
                "benefits_grade": offer.benefits_grade or "B",
                "wlb_score": offer.wlb_score or 7.0,
                "growth_score": offer.growth_score or 7.0,
                "role_fit": offer.role_fit or 7.0,
                "total_score": 7.5 + (i * 0.3),  # Mock scoring
                "col_adjusted_salary": offer.base_salary * 0.9,  # Mock COL adjustment
                "market_percentile": 70 + (i * 5),  # Mock percentile
                "research_data": {
                    "company_info": f"Mock research data for {offer.company}",
                    "market_sentiment": "Positive"
                }
            }
            processed_offers.append(processed_offer)
        
        # Sort by score for rankings
        ranked_offers_data = sorted(processed_offers, key=lambda x: x["total_score"], reverse=True)
        
        # Create ranked_offers with full structure matching real API
        ranked_offers = [
            {
                "offer_id": offer["id"],
                "company": offer["company"],
                "position": offer["position"],
                "location": offer["location"],
                "total_score": offer["total_score"],
                "rating": "Excellent" if offer["total_score"] > 8.0 else "Good" if offer["total_score"] > 7.0 else "Fair",
                "score_breakdown": {
                    "compensation_score": offer["total_score"] * 0.3,
                    "growth_score": offer["growth_score"],
                    "wlb_score": offer["wlb_score"],
                    "culture_score": 7.0,
                    "benefits_score": 6.5
                },
                "offer_data": offer,
                "rank": i + 1,
                "score_gap": (ranked_offers_data[i-1]["total_score"] - offer["total_score"]) if i > 0 else 0
            } for i, offer in enumerate(ranked_offers_data)
        ]
        
        return {
            "executive_summary": f"Analysis complete for {len(req.offers)} offers. Top recommendation: {ranked_offers[0]['company']}",
            "final_report": {
                "detailed_analysis": f"After analyzing {len(req.offers)} job offers, our AI recommends {ranked_offers[0]['company']} as the top choice.\n\nKey factors in this recommendation include:\n• Highest overall score of {ranked_offers[0]['total_score']:.1f}\n• Strong compensation package with ${ranked_offers_data[0]['base_salary']:,.0f} base salary\n• Good growth potential and work-life balance metrics\n\nThis analysis considered your preferences and market conditions to provide personalized recommendations.",
                "decision_framework": "Consider these key factors when making your final decision:\n\n1. Total Compensation: Look beyond base salary to include equity and bonuses\n2. Growth Potential: Consider the company's trajectory and your career development\n3. Work-Life Balance: Ensure the role aligns with your personal priorities\n4. Cost of Living: Factor in location-based expenses for true value comparison\n\nRemember that the best offer depends on your individual circumstances and career goals.",
                "offer_rankings": [
                    {
                        "offer_id": offer["offer_id"],
                        "company": offer["company"],
                        "position": offer["position"],
                        "total_score": offer["total_score"],
                        "rank": offer["rank"],
                        "ai_recommendation": f"{'Strong recommendation' if offer['total_score'] > 7.5 else 'Good option' if offer['total_score'] > 6.5 else 'Consider carefully'} - Score: {offer['total_score']:.1f}. {offer['company']} offers {'excellent' if offer['total_score'] > 7.5 else 'good' if offer['total_score'] > 6.5 else 'moderate'} overall value."
                    } for offer in ranked_offers
                ]
            },
            "comparison_results": {
                "ranked_offers": ranked_offers,
                "top_offer": ranked_offers[0] if ranked_offers else None,
                "comparison_summary": f"Top choice: {ranked_offers[0]['company']} (Score: {ranked_offers[0]['total_score']:.1f}). Analysis of {len(req.offers)} offers completed.",
                "weights_used": {
                    "compensation_weight": 0.30,
                    "growth_weight": 0.20,
                    "wlb_weight": 0.20,
                    "culture_weight": 0.15,
                    "benefits_weight": 0.15
                }
            },
            "visualization_data": {
                "radar_chart": {
                    "labels": ["Compensation", "Growth", "Work-Life Balance", "Culture", "Benefits"],
                    "datasets": [
                        {
                            "label": offer["company"],
                            "data": [
                                offer["base_salary"] / 50000,  # Normalized
                                offer["growth_score"],
                                offer["wlb_score"],
                                7.0,  # Mock culture score
                                6.5   # Mock benefits score
                            ],
                            "backgroundColor": f"rgba({59 + i*50}, {130 - i*20}, {246 - i*30}, 0.2)",
                            "borderColor": f"rgb({59 + i*50}, {130 - i*20}, {246 - i*30})"
                        } for i, offer in enumerate(processed_offers[:3])  # Limit to 3 for visibility
                    ]
                },
                "comparison_table": [
                    {
                        "company": offer["company"],
                        "total_compensation": offer["base_salary"] + offer["equity"] + offer["bonus"],
                        "col_adjusted": offer["col_adjusted_salary"],
                        "score": offer["total_score"]
                    } for offer in processed_offers
                ]
            },
            "offers": processed_offers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
