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

def normalize_location_for_tax(location):
    """
    Normalize location string to match tax database keys.
    Similar to col_calculator logic.
    """
    location = location.strip()
    lower_loc = location.lower()
    
    # Simple mapping for common variations
    if "san francisco" in lower_loc or "bay area" in lower_loc or "sf" == lower_loc:
        return "San Francisco, CA"
    if "new york" in lower_loc or "nyc" in lower_loc:
        return "New York, NY"
    if "seattle" in lower_loc:
        return "Seattle, WA"
    if "redmond" in lower_loc:
        return "Redmond, WA"
    if "bellevue" in lower_loc:
        return "Bellevue, WA"
    if "austin" in lower_loc:
        return "Austin, TX"
    if "atlanta" in lower_loc:
        return "Atlanta, GA"
    if "phoenix" in lower_loc or "scottsdale" in lower_loc:
        return "Phoenix, AZ"
    if "denver" in lower_loc:
        return "Denver, CO"
    if "minneapolis" in lower_loc:
        return "Minneapolis, MN"
    if "philadelphia" in lower_loc:
        return "Philadelphia, PA"
    if "raleigh" in lower_loc or "durham" in lower_loc:
        return "Raleigh, NC"
    if "remote" in lower_loc:
        return "Remote"
        
    # Try exact match keys (case-insensitive)
    for key in TAX_RATES.keys():
        if key.lower() == lower_loc:
            return key
            
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
