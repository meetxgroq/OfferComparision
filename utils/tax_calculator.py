"""
Tax Calculator - Estimates effective tax rates based on location.
Includes Federal, State, and FICA estimates for major tech hubs.
"""

# Estimated Total Effective Tax Rates (Federal + State + FICA) for high income bracket ($150k-$300k)
# These are rough estimates for comparison purposes.
TAX_RATES = {
    # High Tax States (CA, NY)
    "San Francisco, CA": 0.38,
    "San Jose, CA": 0.38,
    "Palo Alto, CA": 0.38,
    "Mountain View, CA": 0.38,
    "Los Angeles, CA": 0.38,
    "San Diego, CA": 0.38,
    "New York, NY": 0.39,      # NYC City Tax
    "Manhattan, NY": 0.39,
    "Brooklyn, NY": 0.39,
    
    # Moderate Tax States (OR, MA, etc.)
    "Portland, OR": 0.35,
    "Boston, MA": 0.32,
    "Cambridge, MA": 0.32,
    "Chicago, IL": 0.32,
    
    # No State Income Tax (WA, TX, FL, NV, TN)
    "Seattle, WA": 0.26,
    "Redmond, WA": 0.26,
    "Bellevue, WA": 0.26,
    "Austin, TX": 0.26,
    "Dallas, TX": 0.26,
    "Houston, TX": 0.26,
    "Miami, FL": 0.26,
    "Orlando, FL": 0.26,
    "Las Vegas, NV": 0.26,
    "Nashville, TN": 0.26,
    
    # Other Major Tech Hubs
    "Atlanta, GA": 0.32,   # ~5.5% State
    "Phoenix, AZ": 0.29,   # 2.5% State
    "Denver, CO": 0.30,    # 4.4% State
    "Boulder, CO": 0.30,
    "Minneapolis, MN": 0.34, # High State Tax
    "Philadelphia, PA": 0.33, # State + City Wage Tax
    "Pittsburgh, PA": 0.31,
    "Raleigh, NC": 0.31,   # ~4.75% State
    "Durham, NC": 0.31,
    "Salt Lake City, UT": 0.31, # ~4.65% State
    "Washington, DC": 0.32,
    "Arlington, VA": 0.32,
    "Detroit, MI": 0.33,   # State + City
    
    # International (Rough Estimates)
    "London, UK": 0.40,
    "Berlin, Germany": 0.42,
    "Amsterdam, Netherlands": 0.40,
    "Toronto, Canada": 0.35,
    "Vancouver, Canada": 0.35,
    "Singapore": 0.15,         # Very low tax
    "Dubai, UAE": 0.00,        # No income tax
}

DEFAULT_TAX_RATE = 0.30  # Fallback for unknown locations

# Robust City -> State Mapping for Inference
CITY_TO_STATE_MAPPING = {
    # California
    "san francisco": "San Francisco, CA", "sf": "San Francisco, CA", "bay area": "San Francisco, CA",
    "san jose": "San Jose, CA", "sunnyvale": "San Jose, CA", "santa clara": "San Jose, CA", "cupertino": "San Jose, CA",
    "palo alto": "Palo Alto, CA", "menlo park": "Palo Alto, CA",
    "mountain view": "Mountain View, CA",
    "los angeles": "Los Angeles, CA", "la": "Los Angeles, CA", "santa monica": "Los Angeles, CA",
    "san diego": "San Diego, CA",

    # New York
    "new york": "New York, NY", "nyc": "New York, NY", "ny": "New York, NY", "manhattan": "Manhattan, NY", "brooklyn": "Brooklyn, NY",

    # Washington
    "seattle": "Seattle, WA", "redmond": "Redmond, WA", "bellevue": "Bellevue, WA", "kirkland": "Redmond, WA",

    # Texas
    "austin": "Austin, TX",
    "dallas": "Dallas, TX",
    "houston": "Houston, TX",

    # Massachusetts
    "boston": "Boston, MA", "cambridge": "Cambridge, MA",

    # Others
    "portland": "Portland, OR",
    "chicago": "Chicago, IL",
    "miami": "Miami, FL", "orlando": "Orlando, FL",
    "las vegas": "Las Vegas, NV", "vegas": "Las Vegas, NV",
    "nashville": "Nashville, TN",
    "atlanta": "Atlanta, GA",
    "phoenix": "Phoenix, AZ", "scottsdale": "Phoenix, AZ",
    "denver": "Denver, CO", "boulder": "Boulder, CO",
    "minneapolis": "Minneapolis, MN",
    "philadelphia": "Philadelphia, PA", "philly": "Philadelphia, PA",
    "pittsburgh": "Pittsburgh, PA",
    "raleigh": "Raleigh, NC", "durham": "Durham, NC", "rtp": "Raleigh, NC",
    "salt lake city": "Salt Lake City, UT", "slc": "Salt Lake City, UT",
    "washington": "Washington, DC", "dc": "Washington, DC",
    "arlington": "Arlington, VA",
    "detroit": "Detroit, MI",

    # International
    "london": "London, UK",
    "berlin": "Berlin, Germany",
    "amsterdam": "Amsterdam, Netherlands",
    "toronto": "Toronto, Canada",
    "vancouver": "Vancouver, Canada",
    "singapore": "Singapore",
    "dubai": "Dubai, UAE"
}

def normalize_location_for_tax(location):
    """
    Normalize location string to match tax database keys.
    Uses Smart Inference to map "City" -> "City, State".
    """
    if not location:
        return "Remote"
        
    location = location.strip()
    lower_loc = location.lower()
    
    # 1. Exact Match Check (Fast Path)
    for key in TAX_RATES.keys():
        if key.lower() == lower_loc:
            return key
            
    # 2. Remote Check
    if "remote" in lower_loc:
        return "Remote"

    # 3. Smart Inference (Dictionary Lookup)
    import re
    
    # Sort keys by length (descending) to match "San Francisco" before "San"
    sorted_cities = sorted(CITY_TO_STATE_MAPPING.keys(), key=len, reverse=True)
    
    for city in sorted_cities:
        # Escape city for regex to be safe
        escaped_city = re.escape(city)
        # Use word boundaries (\b) to prevent "ny" matching "company"
        # We allow the match if it's the whole string OR surrounded by word boundaries
        pattern = r"(^|\b)" + escaped_city + r"(\b|$)"
        
        if re.search(pattern, lower_loc):
            return CITY_TO_STATE_MAPPING[city]
            
    # 4. Fallback: Return original capitalized
    return location

def estimate_tax_rate(location):
    """
    Estimate the total effective tax rate for a given location.
    
    Args:
        location (str): Location name
        
    Returns:
        float: Estimated tax rate (0.0 to 1.0)
    """
    norm_loc = normalize_location_for_tax(location)
    
    # Note: 'Remote' logic is handled by the caller (nodes.py) 
    # passing the user's base location if the offer is Remote.
    # If 'Remote' is passed here directly, return default.
    if norm_loc == "Remote":
        return DEFAULT_TAX_RATE
        
    return TAX_RATES.get(norm_loc, DEFAULT_TAX_RATE)

def calculate_net_pay(total_compensation, location):
    """
    Calculate estimated net pay.
    
    Args:
        total_compensation (float): Total annual compensation
        location (str): Location name
        
    Returns:
        dict: Net pay analysis
    """
    rate = estimate_tax_rate(location)
    net_pay = total_compensation * (1 - rate)
    tax_amount = total_compensation * rate
    
    return {
        "gross_pay": total_compensation,
        "estimated_tax_rate": rate,
        "estimated_tax_amount": round(tax_amount, 2),
        "estimated_net_pay": round(net_pay, 2),
        "location": location
    }
