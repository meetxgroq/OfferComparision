"""
Cost of Living Calculator - Location-based compensation adjustments
Calculates purchasing power parity and cost adjustments across locations
"""

import json

# Comprehensive cost of living indices (base: San Francisco = 100)
COST_OF_LIVING_DATA = {
    # Major US Tech Hubs
    "San Francisco, CA": 100.0,
    "San Jose, CA": 95.0,
    "Palo Alto, CA": 110.0,
    "Mountain View, CA": 105.0,
    "New York, NY": 85.0,
    "Manhattan, NY": 90.0,
    "Brooklyn, NY": 75.0,
    "Seattle, WA": 78.0,
    "Los Angeles, CA": 70.0,
    "San Diego, CA": 65.0,
    "Boston, MA": 72.0,
    "Cambridge, MA": 75.0,
    "Washington, DC": 68.0,
    "Chicago, IL": 55.0,
    "Denver, CO": 58.0,
    "Portland, OR": 60.0,
    "Austin, TX": 52.0,
    "Dallas, TX": 48.0,
    "Houston, TX": 45.0,
    "Atlanta, GA": 45.0,
    "Miami, FL": 50.0,
    "Phoenix, AZ": 42.0,
    "Las Vegas, NV": 40.0,
    "Salt Lake City, UT": 45.0,
    "Minneapolis, MN": 50.0,
    "Detroit, MI": 35.0,
    "Pittsburgh, PA": 38.0,
    "Philadelphia, PA": 55.0,
    "Raleigh, NC": 40.0,
    "Nashville, TN": 42.0,
    "Orlando, FL": 45.0,
    
    # International Tech Hubs
    "London, UK": 85.0,
    "Dublin, Ireland": 75.0,
    "Amsterdam, Netherlands": 78.0,
    "Berlin, Germany": 65.0,
    "Munich, Germany": 70.0,
    "Zurich, Switzerland": 120.0,
    "Geneva, Switzerland": 125.0,
    "Paris, France": 80.0,
    "Stockholm, Sweden": 75.0,
    "Copenhagen, Denmark": 85.0,
    "Oslo, Norway": 90.0,
    "Helsinki, Finland": 70.0,
    "Barcelona, Spain": 60.0,
    "Madrid, Spain": 62.0,
    "Milan, Italy": 68.0,
    "Rome, Italy": 65.0,
    "Vienna, Austria": 65.0,
    "Prague, Czech Republic": 45.0,
    "Warsaw, Poland": 40.0,
    "Budapest, Hungary": 38.0,
    
    # Asia-Pacific
    "Tokyo, Japan": 85.0,
    "Singapore": 95.0,
    "Hong Kong": 110.0,
    "Sydney, Australia": 80.0,
    "Melbourne, Australia": 75.0,
    "Toronto, Canada": 65.0,
    "Vancouver, Canada": 70.0,
    "Montreal, Canada": 55.0,
    "Tel Aviv, Israel": 75.0,
    "Seoul, South Korea": 70.0,
    "Taipei, Taiwan": 50.0,
    "Shanghai, China": 55.0,
    "Beijing, China": 60.0,
    "Shenzhen, China": 58.0,
    "Bangalore, India": 25.0,
    "Mumbai, India": 35.0,
    "Hyderabad, India": 22.0,
    "Delhi, India": 30.0,
    "Pune, India": 20.0,
    
    # Emerging Markets
    "Mexico City, Mexico": 30.0,
    "Sao Paulo, Brazil": 35.0,
    "Buenos Aires, Argentina": 25.0,
    "Lisbon, Portugal": 50.0,
    "Cape Town, South Africa": 28.0,
    "Dubai, UAE": 65.0,
    "Riyadh, Saudi Arabia": 50.0,
    "Cairo, Egypt": 18.0,
}

def normalize_location(location):
    """
    Normalize location string for consistent matching.
    
    Args:
        location (str): Location string
    
    Returns:
        str: Normalized location
    """
    location = location.strip()
    
    # Case-insensitive mappings and common synonyms
    location_mappings = {
        "sf": "San Francisco, CA",
        "san francisco": "San Francisco, CA",
        "san francisco, ca": "San Francisco, CA",
        "nyc": "New York, NY",
        "new york": "New York, NY",
        "new york, ny": "New York, NY",
        "la": "Los Angeles, CA",
        "los angeles": "Los Angeles, CA",
        "los angeles, ca": "Los Angeles, CA",
        "seattle": "Seattle, WA",
        "seattle, wa": "Seattle, WA",
        "bay area": "San Francisco, CA",
        "silicon valley": "San Jose, CA",
        "london": "London, UK",
        "berlin": "Berlin, Germany",
        "tokyo": "Tokyo, Japan",
        "singapore": "Singapore",
        "remote": "Remote"
    }
    
    lower_loc = location.lower()
    if lower_loc in location_mappings:
        return location_mappings[lower_loc]
    
    # Try exact key match in COST_OF_LIVING_DATA ignoring case
    for known in COST_OF_LIVING_DATA.keys():
        if known.lower() == lower_loc:
            return known
    
    # Fallback: Title-case unknown city names (retain original if looks custom)
    return location

def get_cost_index(location):
    """
    Get cost of living index for a location.
    
    Args:
        location (str): Location name
    
    Returns:
        float: Cost index (San Francisco = 100.0)
    """
    normalized_location = normalize_location(location)
    
    if normalized_location == "Remote":
        return 50.0  # Default for remote work
    
    return COST_OF_LIVING_DATA.get(normalized_location, 75.0)  # Default for unknown locations (per tests)

BASELINE_ANNUAL_EXPENSES = 60000.0  # Baseline annual living expenses for a single person in SF

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