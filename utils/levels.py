"""
Leveling Mapping Utility - Universal leveling scale for tech companies.
Maps specific company levels (e.g., Microsoft 61) to a universal scale (L1-L8).
"""

from typing import Dict, Optional, List
import json

# Universal Level Scale
# L1: Junior/Entry Level
# L2: Mid-Level
# L3: Senior
# L4: Staff / L2 Senior
# L5: Senior Staff / Principal
# L6: Principal II / Distinguished
# L7: Distinguished II / Fellow
# L8: Senior Fellow / CTO-Level

UNIVERSAL_LEVELS = {
    1: {"name": "Junior", "description": "Entry level / New grad"},
    2: {"name": "Mid-Level", "description": "Individual contributor with some experience"},
    3: {"name": "Senior", "description": "Senior individual contributor / Tech lead"},
    4: {"name": "Staff", "description": "High-level individual contributor / Multi-team lead"},
    5: {"name": "Senior Staff / Principal", "description": "Organization-wide influence"},
    6: {"name": "Principal II / Distinguished", "description": "Strategic technical leadership"},
    7: {"name": "Distinguished II / Fellow", "description": "Industry-level influence"},
    8: {"name": "Senior Fellow", "description": "Top-tier technical visionary"}
}

# Static Mapping for Top Companies
# Format: { CompanyName: { InternalLevel: UniversalLevel } }
COMPANY_LEVEL_MAP = {
    "Google": {
        "L3": 1, "L4": 2, "L5": 3, "L6": 4, "L7": 5, "L8": 6, "L9": 7, "L10": 8
    },
    "Microsoft": {
        "59": 1, "60": 1, "61": 2, "62": 3, "63": 3, "64": 4, "65": 5, "66": 6, "67": 7, "68": 8,
        "SDE": 1, "SDE II": 2, "Senior SDE": 3, "Principal SDE": 4, "Partner SDE": 6
    },
    "Meta": {
        "E3": 1, "E4": 2, "E5": 3, "E6": 4, "E7": 5, "E8": 6, "E9": 7,
        "ICT3": 2, "ICT4": 3, "ICT5": 4, "ICT6": 5
    },
    "Amazon": {
        "L4": 1, "L5": 2, "L6": 3, "L7": 4, "L8": 5, "L10": 7
    },
    "Nvidia": {
        "IC1": 1, "IC2": 2, "IC3": 3, "IC4": 4, "IC5": 5, "IC6": 6, "IC7": 7, "IC8": 8
    },
    "Apple": {
        "ICT2": 1, "ICT3": 2, "ICT4": 3, "ICT5": 4, "ICT6": 5
    },
    "Linkedin": {
        "IND1": 1, "IND2": 2, "IND3": 3, "IND4": 4, "IND5": 5, "IND6": 6,
        "SENIOR": 2, "STAFF": 3, "PRINCIPAL": 5
    },
    "Stripe": {
        "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5
    },
    "Uber": {
        "L3": 1, "L4": 2, "L5": 3, "L6": 4, "L7": 5
    },
    "Salesforce": {
        "AMTS": 1, "MTS": 2, "SMTS": 3, "LMTS": 4, "PRINCIPAL": 5
    },
    "Databricks": {
        "L3": 1, "L4": 2, "L5": 3, "L6": 4
    },
    "Snowflake": {
        "L3": 1, "L4": 2, "L5": 3, "L6": 4, "L7": 5
    },
    "Airbnb": {
        "L3": 1, "L4": 2, "L5": 3, "L6": 4, "L7": 5
    }
}

from .call_llm import call_llm_structured_async

async def infer_level_async(company: str, level_str: str, position: str = "Software Engineer") -> Optional[int]:
    """
    Use AI to infer the universal level for a company level string.
    
    Args:
        company (str): Company name
        level_str (str): Level string (e.g., "IC3", "61")
        position (str): Position title for context
        
    Returns:
        Optional[int]: Universal level (1-8)
    """
    prompt = f"""
    Map the following company-specific job level to our universal scale (1-8).
    
    Company: {company}
    Level String: {level_str}
    Position: {position}
    
    Universal Scale Reference:
    1: Junior (Entry level, new grad, L3 at Google)
    2: Mid-Level (L4 at Google, SDE II at Microsoft)
    3: Senior (L5 at Google, Senior SDE at Microsoft)
    4: Staff (L6 at Google, Principal at Microsoft)
    5: Senior Staff / Principal (L7 at Google)
    6: Principal II / Distinguished (L8 at Google)
    7: Distinguished II / Fellow (L9 at Google)
    8: Senior Fellow / Technical Visionary (L10 at Google)
    
    Return a JSON object:
    {{
        "universal_level": integer (1-8),
        "confidence": float (0-1),
        "reasoning": "brief explanation"
    }}
    """
    
    try:
        response_json = await call_llm_structured_async(
            prompt,
            response_format={"type": "json_object"},
            temperature=0.1
        )
        if not response_json:
            return None
            
        data = json.loads(response_json)
        level = data.get("universal_level")
        if isinstance(level, int) and 1 <= level <= 8:
            return level
    except Exception as e:
        # Avoid flooding logs with API errors during verification
        pass
        
    return None

async def get_universal_level_async(company: str, company_level: str, position: str = "Software Engineer") -> Optional[int]:
    """
    Map a company-specific level to the universal level scale (Async version with AI fallback).
    """
    # Normalize inputs
    company_clean = company.strip().title()
    level_clean = company_level.strip().upper()
    
    # 1. Try static mapping
    if company_clean in COMPANY_LEVEL_MAP:
        if level_clean in COMPANY_LEVEL_MAP[company_clean]:
            return COMPANY_LEVEL_MAP[company_clean][level_clean]
        
        # Try numeric part
        try:
            level_num = str(int(level_clean))
            if level_num in COMPANY_LEVEL_MAP[company_clean]:
                return COMPANY_LEVEL_MAP[company_clean][level_num]
        except ValueError:
            pass
    
    # 2. AI Fallback
    return await infer_level_async(company_clean, level_clean, position)

def get_universal_level(company: str, company_level: str) -> Optional[int]:
    """
    Sync version (no AI fallback).
    """
    company = company.strip().title()
    company_level = company_level.strip().upper()
    
    if company in COMPANY_LEVEL_MAP:
        if company_level in COMPANY_LEVEL_MAP[company]:
            return COMPANY_LEVEL_MAP[company][company_level]
        try:
            level_num = str(int(company_level))
            if level_num in COMPANY_LEVEL_MAP[company]:
                return COMPANY_LEVEL_MAP[company][level_num]
        except ValueError:
            pass
            
    return None

def get_level_suggestions(company: str) -> List[str]:
    """Get common levels for a specific company for UI suggestions."""
    company = company.strip().title()
    if company in COMPANY_LEVEL_MAP:
        levels = list(COMPANY_LEVEL_MAP[company].keys())
        # Sort levels to be somewhat logical
        return sorted(levels)
    return []

def get_level_description(level: int) -> str:
    """Get text description for a universal level."""
    if level in UNIVERSAL_LEVELS:
        return f"{UNIVERSAL_LEVELS[level]['name']} ({UNIVERSAL_LEVELS[level]['description']})"
    return "Unknown Level"

if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("NVIDIA", "IC3"),
        ("Google", "L5"),
        ("Microsoft", "62"),
        ("Meta", "E4"),
        ("Apple", "ict4")
    ]
    
    for company, level in test_cases:
        uni = get_universal_level(company, level)
        print(f"{company} {level} -> Universal L{uni}: {get_level_description(uni)}")
