"""
Cost of Living Calculator - Location-based compensation adjustments
Calculates purchasing power parity and cost adjustments across locations
"""

import json

from utils.location_registry import (
    LOCATION_REGISTRY,
    normalize_location,
    get_col_index,
)

# Backward-compatible view: { canonical_key: col_index }
COST_OF_LIVING_DATA = {k: e.col_index for k, e in LOCATION_REGISTRY.items() if k != "Remote"}


def get_cost_index(location):
    """Get cost of living index for a location (SF = 100.0)."""
    return get_col_index(location)


BASELINE_ANNUAL_EXPENSES = 60000.0  # Baseline annual living expenses for a single person in SF

BASELINE_EXPENSES_BY_COUNTRY = {
    "United States": 60000,
    "India": 6000,
    "UAE": 30000,
    "United Kingdom": 42000,
    "Germany": 30000,
    "Singapore": 36000,
    "Canada": 36000,
    "Australia": 40000,
    "Japan": 36000,
    "Netherlands": 33000,
    "Switzerland": 55000,
    "Ireland": 36000,
    "South Korea": 24000,
    "Saudi Arabia": 24000,
    "Qatar": 28000,
    "Israel": 36000,
}

def estimate_annual_expenses(location):
    """
    Estimate annual living expenses for a single person in a given location.
    
    Args:
        location (str): Location name
        
    Returns:
        dict: Expense analysis
    """
    idx = get_cost_index(location)
    
    # Calculate estimated expenses based on SF baseline
    # Formula: Baseline * (Location_Index / 100)
    estimated_expenses = BASELINE_ANNUAL_EXPENSES * (idx / 100.0)
    
    return {
        "location": normalize_location(location),
        "cost_index": idx,
        "estimated_annual_expenses": round(estimated_expenses, 2),
        "baseline_expenses": BASELINE_ANNUAL_EXPENSES,
        "relative_to_baseline": f"{idx}%"
    }


def get_location_insights(location):
    """
    Get insights about a specific location for job seekers.
    
    Args:
        location (str): Location to analyze
    
    Returns:
        dict: Location insights
    """
    cost_index = get_cost_index(location)
    normalized_loc = normalize_location(location)
    
    # Categorize cost level
    if cost_index >= 90:
        cost_category = "Very High Cost"
        advice = "Consider negotiating higher compensation. Focus on equity and benefits."
    elif cost_index >= 70:
        cost_category = "High Cost" 
        advice = "Ensure salary adequately covers living expenses. Consider housing options."
    elif cost_index >= 50:
        cost_category = "Moderate Cost"
        advice = "Good balance of opportunities and cost. Evaluate career growth potential."
    elif cost_index >= 30:
        cost_category = "Low Cost"
        advice = "Great value for money. Consider long-term career prospects."
    else:
        cost_category = "Very Low Cost"
        advice = "Excellent cost of living. Evaluate market opportunities and growth."
    
    return {
        "location": normalized_loc,
        "cost_index": cost_index,
        "cost_category": cost_category,
        "relative_to_sf": f"{cost_index}% of San Francisco costs",
        "advice": advice,
        "is_tech_hub": normalized_loc in [
            "San Francisco, CA", "San Jose, CA", "Seattle, WA", "New York, NY",
            "Boston, MA", "Austin, TX", "London, UK", "Singapore", "Tokyo, Japan"
        ],
        # Added for tests expecting a narrative analysis field
        "analysis": f"{normalized_loc} is a {cost_category.lower()} area with cost index {cost_index}. {advice}"
    }

if __name__ == "__main__":
    expenses = estimate_annual_expenses("Austin, TX")
    print("Annual Expenses:", json.dumps(expenses, indent=2))
    
    insights = get_location_insights("Denver, CO")
    print("Location Insights:", json.dumps(insights, indent=2)) 