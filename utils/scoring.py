"""
Scoring Engine - Personalized weighted scoring algorithm
Calculates offer scores based on user-defined preferences and weightings
"""

import json
from typing import Dict, List, Any

# Default scoring weights (can be customized by user)
DEFAULT_WEIGHTS = {
    "base_salary": 0.20,
    "total_compensation": 0.15,
    "net_savings": 0.15,
    "equity_upside": 0.15,
    "work_life_balance": 0.10,
    "career_growth": 0.10,
    "company_culture": 0.08,
    "benefits_quality": 0.05,
    "location_preference": 0.02
}

# Scoring factors and their evaluation criteria
SCORING_FACTORS = {
    "base_salary": {
        "description": "Base salary competitiveness",
        "scale": "Market percentile (0-100)",
        "calculation": "market_percentile"
    },
    "total_compensation": {
        "description": "Total compensation package value",
        "scale": "Market percentile (0-100)", 
        "calculation": "total_comp_percentile"
    },
    "equity_upside": {
        "description": "Equity growth potential",
        "scale": "Risk-adjusted upside (0-100)",
        "calculation": "equity_score"
    },
    "work_life_balance": {
        "description": "Work-life balance quality",
        "scale": "Company rating (0-100)",
        "calculation": "wlb_score"
    },
    "career_growth": {
        "description": "Professional development opportunities",
        "scale": "Growth potential (0-100)",
        "calculation": "growth_score"
    },
    "company_culture": {
        "description": "Company culture fit",
        "scale": "Culture rating (0-100)",
        "calculation": "culture_score"
    },
    "benefits_quality": {
        "description": "Benefits package quality",
        "scale": "Benefits rating (0-100)",
        "calculation": "benefits_score"
    },
    "location_preference": {
        "description": "Location desirability",
        "scale": "Personal preference (0-100)",
        "calculation": "location_score"
    },
    "net_savings": {
        "description": "Estimated annual savings",
        "scale": "Based on $100k target (0-100)",
        "calculation": "savings_score"
    }
}

def normalize_score(value, min_val=0, max_val=100):
    """
    Normalize a score to 0-100 scale.
    
    Args:
        value (float): Value to normalize
        min_val (float): Minimum possible value
        max_val (float): Maximum possible value
    
    Returns:
        float: Normalized score (0-100)
    """
    if max_val == min_val:
        return 50.0  # Default to middle if no range
    
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    return max(0, min(100, normalized))

def calculate_equity_score(equity_value, company_stage, company_stability, vesting_years=4):
    """
    Calculate equity upside score based on value, company stage, and risk factors.
    
    Args:
        equity_value (float): Annual equity value
        company_stage (str): Company maturity (startup, growth, public, etc.)
        company_stability (float): Stability score (0-10)
        vesting_years (int): Vesting period in years
    
    Returns:
        float: Risk-adjusted equity score (0-100)
    """
    if equity_value <= 0:
        return 0
    
    # Base score from equity value (logarithmic scale for diminishing returns)
    import math
    value_score = min(100, math.log10(equity_value + 1) * 20)
    
    # Stage multipliers
    stage_multipliers = {
        "startup": 1.5,    # High risk, high reward
        "series_a": 1.3,
        "series_b": 1.2,
        "series_c": 1.1,
        "growth": 1.0,
        "pre_ipo": 0.9,
        "public": 0.7,     # Lower risk, lower upside
        "established": 0.6
    }
    
    stage_multiplier = stage_multipliers.get(company_stage.lower(), 1.0)
    
    # Stability adjustment (0-10 scale to 0.5-1.5 multiplier)
    stability_multiplier = 0.5 + (company_stability / 10)
    
    # Vesting penalty (longer vesting = lower score)
    vesting_penalty = max(0.7, 1 - (vesting_years - 4) * 0.1)
    
    final_score = value_score * stage_multiplier * stability_multiplier * vesting_penalty
    return min(100, max(0, final_score))

def calculate_location_score(location, user_preferences):
    """
    Calculate location preference score.
    
    Args:
        location (str): Job location
        user_preferences (dict): User location preferences
    
    Returns:
        float: Location preference score (0-100)
    """
    preferences = user_preferences.get("location_preferences", {})
    
    # Default preferences if none specified
    if not preferences:
        # Basic tech hub scoring
        tech_hub_scores = {
            "San Francisco, CA": 85,
            "Seattle, WA": 80,
            "New York, NY": 75,
            "Austin, TX": 70,
            "Boston, MA": 70,
            "Remote": 90  # Many people prefer remote
        }
        return tech_hub_scores.get(location, 60)
    
    # Use user-specified preferences
    if location in preferences:
        return preferences[location]
    
    # Check for partial matches
    for pref_location, score in preferences.items():
        if pref_location.lower() in location.lower() or location.lower() in pref_location.lower():
            return score
    
    return 50  # Neutral score for unspecified locations

# Grade to Score Mapping
GRADE_TO_SCORE = {
    "A+": 100, "A": 96, "A-": 92,
    "B+": 88, "B": 84, "B-": 80,
    "C+": 78, "C": 74, "C-": 70,
    "D+": 68, "D": 64, "D-": 60,
    "F": 50
}

def _convert_grade_to_score(grade_or_score):
    """Convert a letter grade or numeric score to a 0-100 float."""
    if isinstance(grade_or_score, (int, float)):
        return float(grade_or_score)
    if isinstance(grade_or_score, str):
        # normalize
        cleaned = grade_or_score.upper().strip()
        # Handle "8/10" or "8" strings
        try:
            val = float(cleaned)
            if val <= 10: return val * 10
            return val
        except ValueError:
            pass
        return GRADE_TO_SCORE.get(cleaned, 75.0) # Default to C/B border
    return 0.0

def calculate_offer_score(offer_data, user_preferences=None, weights=None):
    """
    Calculate comprehensive score for a job offer.
    
    Args:
        offer_data (dict): Complete offer information
        user_preferences (dict): User preferences and priorities
        weights (dict): Custom scoring weights
    
    Returns:
        dict: Detailed scoring breakdown
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()
    
    if user_preferences is None:
        user_preferences = {}
    
    # Initialize scores dictionary
    factor_scores = {}
    
    # 1. Base Salary Score (from market analysis)
    market_data = offer_data.get("market_analysis", {})
    factor_scores["base_salary"] = market_data.get("market_percentile", 50)
    
    # 2. Total Compensation Score
    total_comp_data = offer_data.get("total_comp_analysis", {})
    factor_scores["total_compensation"] = total_comp_data.get("market_percentile", 50)
    
    # 3. Equity Score
    equity_value = offer_data.get("equity", 0)
    company_data = offer_data.get("company_research", {})
    company_stage = company_data.get("stage", "growth")
    stability_score = company_data.get("metrics", {}).get("stability_score", {}).get("score", 7)
    factor_scores["equity_upside"] = calculate_equity_score(equity_value, company_stage, stability_score)
    
    # 4. Work-Life Balance Score
    # Check for direct grade user input first, then company metrics
    wlb_input = offer_data.get("wlb_grade")
    if wlb_input:
        factor_scores["work_life_balance"] = _convert_grade_to_score(wlb_input)
    else:
        wlb_data = company_data.get("metrics", {}).get("wlb_score", {})
        factor_scores["work_life_balance"] = wlb_data.get("score", 7) * 10  # Convert 1-10 to 0-100
    
    # 5. Career Growth Score
    growth_input = offer_data.get("growth_grade")
    if growth_input:
        factor_scores["career_growth"] = _convert_grade_to_score(growth_input)
    else:
        growth_data = company_data.get("metrics", {}).get("growth_score", {})
        factor_scores["career_growth"] = growth_data.get("score", 7) * 10
    
    # 6. Company Culture Score
    # Culture is less often graded explicitly by user, usually inferred or rated 1-10
    culture_data = company_data.get("metrics", {}).get("culture_score", {})
    factor_scores["company_culture"] = culture_data.get("score", 7) * 10
    
    # 7. Benefits Quality Score
    benefits_input = offer_data.get("benefits_grade")
    if benefits_input:
        factor_scores["benefits_quality"] = _convert_grade_to_score(benefits_input)
    else:
        benefits_data = company_data.get("metrics", {}).get("benefits_score", {})
        factor_scores["benefits_quality"] = benefits_data.get("score", 7) * 10
    
    # 8. Location Preference Score
    location = offer_data.get("location", "")
    factor_scores["location_preference"] = calculate_location_score(location, user_preferences)

    # 9. Net Savings Score
    net_savings = offer_data.get("net_savings", 0)
    # Scale: 0 -> 0, 100k -> 100
    savings_score = min(100, max(0, (net_savings / 100000) * 100))
    factor_scores["net_savings"] = round(savings_score, 1)
    
    # Calculate weighted total score
    total_score = 0
    factor_breakdown = {}
    
    for factor, score in factor_scores.items():
        weight = weights.get(factor, 0)
        weighted_score = score * weight
        total_score += weighted_score
        
        factor_breakdown[factor] = {
            "raw_score": round(score, 1),
            "weight": weight,
            "weighted_score": round(weighted_score, 1),
            "description": SCORING_FACTORS[factor]["description"]
        }
    
    # Determine overall rating
    if total_score >= 80:
        rating = "Excellent"
    elif total_score >= 70:
        rating = "Very Good"
    elif total_score >= 60:
        rating = "Good"
    elif total_score >= 50:
        rating = "Fair"
    else:
        rating = "Below Average"
    
    return {
        "total_score": round(total_score, 1),
        "rating": rating,
        "factor_scores": factor_scores,
        "factor_breakdown": factor_breakdown,
        "weights_used": weights,
        "top_strengths": _get_top_factors(factor_scores, top_n=3),
        "improvement_areas": _get_bottom_factors(factor_scores, bottom_n=2)
    }

def _get_top_factors(factor_scores, top_n=3):
    """Get top scoring factors."""
    sorted_factors = sorted(factor_scores.items(), key=lambda x: x[1], reverse=True)
    return [{"factor": factor, "score": round(score, 1)} for factor, score in sorted_factors[:top_n]]

def _get_bottom_factors(factor_scores, bottom_n=2):
    """Get lowest scoring factors."""
    sorted_factors = sorted(factor_scores.items(), key=lambda x: x[1])
    return [{"factor": factor, "score": round(score, 1)} for factor, score in sorted_factors[:bottom_n]]

def compare_offers(offers_data, user_preferences=None, weights=None):
    """
    Compare multiple offers and rank them.
    
    Args:
        offers_data (list): List of offer data dictionaries
        user_preferences (dict): User preferences
        weights (dict): Scoring weights
    
    Returns:
        dict: Comparison results with rankings
    """
    scored_offers = []
    
    for i, offer in enumerate(offers_data):
        score_data = calculate_offer_score(offer, user_preferences, weights)
        scored_offers.append({
            "offer_id": offer.get("id", f"offer_{i+1}"),
            "company": offer.get("company", "Unknown"),
            "position": offer.get("position", "Unknown"),
            "location": offer.get("location", "Unknown"),
            "total_score": score_data["total_score"],
            "rating": score_data["rating"],
            "score_breakdown": score_data,
            "offer_data": offer
        })
    
    # Sort by total score (descending)
    scored_offers.sort(key=lambda x: x["total_score"], reverse=True)
    
    # Add rankings
    for i, offer in enumerate(scored_offers):
        offer["rank"] = i + 1
    
    # Calculate score gaps
    if len(scored_offers) > 1:
        for i in range(1, len(scored_offers)):
            gap = scored_offers[i-1]["total_score"] - scored_offers[i]["total_score"]
            scored_offers[i]["score_gap"] = round(gap, 1)
    
    return {
        "ranked_offers": scored_offers,
        "top_offer": scored_offers[0] if scored_offers else None,
        "comparison_summary": _generate_comparison_summary(scored_offers),
        "weights_used": weights or DEFAULT_WEIGHTS
    }

def _generate_comparison_summary(scored_offers):
    """Generate a summary of the comparison."""
    if not scored_offers:
        return "No offers to compare"
    
    if len(scored_offers) == 1:
        return f"Single offer from {scored_offers[0]['company']} with score {scored_offers[0]['total_score']}"
    
    top_offer = scored_offers[0]
    second_offer = scored_offers[1] if len(scored_offers) > 1 else None
    
    summary = f"Top choice: {top_offer['company']} (Score: {top_offer['total_score']})"
    
    if second_offer:
        gap = top_offer["total_score"] - second_offer["total_score"]
        if gap < 5:
            summary += f". Very close race with {second_offer['company']} (Gap: {gap:.1f})"
        elif gap < 15:
            summary += f". Clear but not overwhelming lead over {second_offer['company']} (Gap: {gap:.1f})"
        else:
            summary += f". Strong lead over {second_offer['company']} (Gap: {gap:.1f})"
    
    return summary

def customize_weights(user_priorities):
    """
    Create custom scoring weights based on user priorities.
    
    Args:
        user_priorities (dict): User-specified priorities
    
    Returns:
        dict: Customized weights
    """
    # Start with defaults
    weights = DEFAULT_WEIGHTS.copy()
    
    # Apply user customizations
    if user_priorities.get("salary_focused"):
        weights["base_salary"] = 0.35
        weights["total_compensation"] = 0.25
        weights["equity_upside"] = 0.20
        weights["work_life_balance"] = 0.10
        weights["career_growth"] = 0.05
        weights["company_culture"] = 0.03
        weights["benefits_quality"] = 0.02
    
    elif user_priorities.get("growth_focused"):
        weights["career_growth"] = 0.30
        weights["equity_upside"] = 0.25
        weights["company_culture"] = 0.15
        weights["total_compensation"] = 0.15
        weights["base_salary"] = 0.10
        weights["work_life_balance"] = 0.03
        weights["benefits_quality"] = 0.02
    
    elif user_priorities.get("balance_focused"):
        weights["work_life_balance"] = 0.35
        weights["company_culture"] = 0.20
        weights["location_preference"] = 0.15
        weights["base_salary"] = 0.15
        weights["benefits_quality"] = 0.10
        weights["total_compensation"] = 0.03
        weights["equity_upside"] = 0.02
    
    # Apply specific weight overrides
    if "custom_weights" in user_priorities:
        custom = user_priorities["custom_weights"]
        for factor, weight in custom.items():
            if factor in weights:
                weights[factor] = weight
        
        # Normalize weights to sum to 1.0
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v/total_weight for k, v in weights.items()}
    # Ensure weights sum to 1.0
    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {k: v/total_weight for k, v in weights.items()}
    
    return weights

if __name__ == "__main__":
    # Test scoring system
    sample_offer = {
        "id": "offer_1",
        "company": "Google",
        "position": "Senior Software Engineer",
        "location": "Seattle, WA",
        "base_salary": 180000,
        "equity": 50000,
        "market_analysis": {"market_percentile": 75},
        "total_comp_analysis": {"market_percentile": 80},
        "company_research": {
            "stage": "public",
            "metrics": {
                "wlb_score": {"score": 8},
                "growth_score": {"score": 9},
                "culture_score": {"score": 8},
                "benefits_score": {"score": 9},
                "stability_score": {"score": 9}
            }
        }
    }
    
    score_result = calculate_offer_score(sample_offer)
    print("Offer Score:", json.dumps(score_result, indent=2)) 