"""
Leveling Mapping Utility - Universal leveling scale for tech companies.
Maps specific company levels (e.g., Microsoft 61, Google L5) to a universal scale (L1-L9).
Now detailed with descriptive titles (e.g., "L5 (Senior)") for easier selection.
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
    1: {"name": "L1: Junior", "description": "Entry-level / New Grad (e.g. Google L3, Microsoft 59/60)"},
    2: {"name": "L2: Mid-Level", "description": "Individual Contributor (e.g. Amazon L4/L5, Meta E4)"},
    3: {"name": "L3: Senior", "description": "Independent Contributor (e.g. Google L5, Microsoft 63)"},
    4: {"name": "L4: Staff / Lead", "description": "Technical Influence across teams (e.g. Google L6, Amazon L7)"},
    5: {"name": "L5: Senior Staff / Principal", "description": "Organization-wide strategic impact"},
    6: {"name": "L6: Distinguished / Fellow", "description": "Industry-level influence / Top technical tier"},
    7: {"name": "L7: Director", "description": "Broad technical or people leadership"},
    8: {"name": "L8: VP / Head of Department", "description": "Executive leadership"},
    9: {"name": "L9: C-Suite", "description": "Highest level of company leadership"}
}

# Static Mapping for Top Companies
# Format: { CompanyName: { Pillar: { InternalLevel: UniversalLevel } } }
# Mapped to the new 1-9 scale
DEFAULT_PILLAR = "Engineering"

COMPANY_LEVEL_MAP = {
    "Google": {
        "Engineering": {
            "L3 (SWE II)": 1, "L4 (SWE III)": 2, "L5 (Senior)": 3, 
            "L6 (Staff)": 4, "L7 (Senior Staff)": 5, "L8 (Principal)": 6, 
            "L9 (Distinguished)": 7, "L10 (Google Fellow)": 8, "L11 (Senior Google Fellow)": 9
        },
        "Product Management": {"APM1": 1, "APM2": 2, "PM": 3, "SR PM": 4, "PRINCIPAL PM": 5},
        "Management & Exec": {"L5 (Manager)": 3, "L6 (Sr Manager)": 4, "L7 (Director)": 5, "L8 (Sr Director)": 6, "L9 (VP)": 7}
    },
    "Microsoft": {
        "Engineering": {
            "59 (SDE)": 1, "60 (SDE)": 1, 
            "61 (SDE II)": 2, "62 (SDE II)": 2,
            "63 (Senior SDE)": 3, "64 (Senior SDE)": 4,
            "65 (Principal SDE)": 5, "66 (Principal SDE)": 6,
            "67 (Partner SDE)": 7, "68 (Partner SDE)": 8, "69 (Partner SDE)": 8, 
            "70 (Distinguished Engineer)": 9
        },
        "Product Management": {"59": 1, "60": 1, "61": 2, "62": 2, "63": 3, "64": 4, "PM": 3, "SR PM": 4},
        "Management & Exec": {
            "64 / Senior Manager": 4,
            "Principal EM / Principal Director of Engineering": 5,
            "66": 6,
            "Senior Director / 67": 7,
            "GM, Partner / SDE Group Manager": 8,
            "69": 8,
            "VP / 70": 8,
            "Corporate VP / 80": 9,
            "Executive VP / 81": 9
        }
    },
    "Meta": {
        "Engineering": {
            "E3 (Entry)": 1, "E4 (Software Engineer)": 2, "E5 (Senior)": 3, 
            "E6 (Staff)": 4, "E7 (Senior Staff)": 5, "E8 (Principal)": 6, "E9 (Distinguished)": 7,
            "ICT3": 2, "ICT4": 3, "ICT5": 4, "ICT6": 5
        },
        "Management & Exec": {"M1 (Manager)": 3, "M2 (Sr Manager)": 4, "D1 (Director)": 5, "D2 (Sr Director)": 6, "VP": 7}
    },
    "Amazon": {
        "Engineering": {
            "L4 (SDE I)": 1, "L5 (SDE II)": 2, "L6 (Senior SDE)": 3, 
            "L7 (Principal SDE)": 4, "L8 (Senior Principal SDE)": 5, 
            "L10 (Distinguished)": 7, "L11 (Senior Distinguished)": 8, "L12 (Fellow)": 9
        },
        "Management & Exec": {"L5 (Manager)": 3, "L6 (Sr Manager)": 4, "L7 (Director)": 5, "L8 (Director)": 6, "L10 (VP)": 7}
    },
    "Nvidia": {
        "Engineering": {
            "IC1 / Software Engineer": 1,
            "IC2": 2,
            "IC3 / Senior Engineer": 3,
            "IC4": 4,
            "IC5": 5,
            "IC6 / Principal Engineer": 6,
            "IC7 / Distinguished Engineer": 7,
            "IC8 / Senior Distinguished Engineer": 8
        },
        "Management & Exec": {"M2 (Lead)": 3, "M3 (Manager)": 4, "M4 (Sr Manager)": 5, "M5 (Director)": 6, "M6 (Sr Director)": 7, "M7 (VP)": 8}
    },
    "Apple": {
        "Engineering": {
            "ICT2 (SWE I)": 1, "ICT3 (SWE II)": 2, "ICT4 (Senior)": 3, 
            "ICT5 (Staff)": 4, "ICT6 (Principal)": 5, "ICT7 (Distinguished)": 6
        },
        "Management & Exec": {"M1 (Manager)": 3, "M2 (Sr Manager)": 4, "M3 (Director)": 5, "M4 (Sr Director)": 6}
    },
    "Linkedin": {
        "Engineering": {
            "IND1 (Entry)": 1, "IND2 (Associate)": 2, "IND3 (Senior)": 3, 
            "IND4 (Staff)": 4, "IND5 (Senior Staff)": 5, "IND6 (Principal)": 6
        },
        "Management & Exec": {"M1 (Manager)": 3, "M2 (Sr Manager)": 4, "M3 (Director)": 5, "M4 (Sr Director)": 6, "VP": 7}
    },
    "Stripe": {
        "Engineering": {"L1 (Entry)": 1, "L2 (Mid)": 2, "L3 (Senior)": 3, "L4 (Staff)": 4, "L5 (Principal)": 5},
        "Management & Exec": {"L2 (Manager)": 3, "L3 (Sr Manager)": 4, "L4 (Director)": 5, "L5 (Head)": 6}
    },
    "Uber": {
        "Engineering": {
            "L3 (Software Engineer I)": 1, "L4 (Software Engineer II)": 2, 
            "L5A (Senior Software Engineer I)": 3, "L5B (Senior Software Engineer II)": 4,
            "L6 (Staff)": 5, "L7 (Senior Staff)": 6
        },
        "Management & Exec": {"M1 (Manager)": 3, "M2 (Sr Manager)": 4, "L6 (Director)": 5, "L7 (Sr Director)": 6, "L8 (VP)": 7}
    },
    "Salesforce": {
        "Engineering": {"AMTS": 1, "MTS": 2, "SMTS (Senior)": 3, "LMTS (Lead)": 4, "PRINCIPAL": 5},
        "Management & Exec": {"Manager": 3, "Sr Manager": 4, "Director": 5, "Sr Director": 6, "VP": 7}
    },
    "Databricks": {
        "Engineering": {"L3 (Software Engineer)": 1, "L4 (Senior)": 2, "L5 (Staff)": 3, "L6 (Principal)": 4},
        "Management & Exec": {"L5 (Manager)": 3, "L6 (Sr Manager)": 4, "L7 (Director)": 5, "VP": 7}
    },
    "Snowflake": {
        "Engineering": {"IC1 (Entry)": 1, "IC2 (Mid)": 2, "IC3 (Senior)": 3, "IC4 (Staff)": 4, "IC5 (Principal)": 5},
        "Management & Exec": {"Manager": 3, "Sr Manager": 4, "Director": 5, "Sr Director": 6, "VP": 7}
    },
    "Airbnb": {
        "Engineering": {"L3 (Software Engineer)": 1, "L4 (Senior)": 2, "L5 (Staff)": 3, "L6 (Senior Staff)": 4, "L7 (Principal)": 5},
        "Management & Exec": {"M3 (Manager)": 3, "M4 (Sr Manager)": 4, "M5 (Director)": 5, "M6 (Sr Director)": 6}
    }
}

ROLE_PILLARS = [
    "Engineering",
    "Product Management",
    "Program Management",
    "Data & Analytics",
    "Marketing & Growth",
    "Design & UX",
    "Management & Exec"
]

import os

CACHE_FILE = "company_levels_cache.json"

def _load_cache() -> Dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def _save_cache(cache: Dict):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except:
        pass

def detect_pillar(position: str) -> str:
    """Detect the role pillar based on the position title."""
    p = position.lower()
    
    # Priority 1: High-level leadership/Management
    if any(k in p for k in ["director", "vp", "head of", "cto", "ceo", "exec"]):
        return "Management & Exec"
        
    # Priority 2: Standard Pillars (check specific first)
    if "program manager" in p or "pgm" in p:
        return "Program Management"
    if "product manager" in p or p.endswith("pm") or "product" in p:
        return "Product Management"
    if "engineering manager" in p:
        return "Management & Exec"
    if "software development manager" in p or "sdm" in p:
        return "Management & Exec"
        
    # Priority 3: Functional Discipline
    if any(k in p for k in ["engineer", "developer", "sde", "backend", "frontend", "fullstack", "devops"]):
        return "Engineering"
    if any(k in p for k in ["data", "analyst", "science", "ml", "machine learning"]):
        return "Data & Analytics"
    if any(k in p for k in ["design", "ux", "ui", "researcher"]):
        return "Design & UX"
    if any(k in p for k in ["marketing", "growth"]):
        return "Marketing & Growth"
        
    return DEFAULT_PILLAR

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
    Map the following company-specific job level to our universal scale (1-9).
    
    Company: {company}
    Level String: {level_str}
    Position: {position}
    
    Universal Scale Reference (L1-L9):
    1: L1 - Junior / Entry (Google L3, Amazon L4)
    2: L2 - Mid-Level (Amazon L5, Meta E4)
    3: L3 - Senior (Google L5, Microsoft 63)
    4: L4 - Staff / Lead (Google L6, Amazon L7)
    5: L5 - Senior Staff / Principal
    6: L6 - Distinguished / Fellow
    7: L7 - Director
    8: L8 - VP / Head of Department
    9: L9 - C-Suite
    
    Return a JSON object:
    {{
        "universal_level": integer (1-9),
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
        if isinstance(level, int) and 1 <= level <= 9:
            return level
    except Exception as e:
        pass
        
    return None

async def get_universal_level_async(company: str, company_level: str, position: str = "Software Engineer") -> Optional[int]:
    """
    Map a company-specific level to the universal level scale (Async version with AI fallback and caching).
    """
    # Normalize inputs
    company_clean = company.strip().title()
    level_clean = company_level.strip().upper()
    pillar = detect_pillar(position)
    
    # 1. Try static mapping
    if company_clean in COMPANY_LEVEL_MAP:
        mapping = COMPANY_LEVEL_MAP[company_clean]
        # Check pillar specific map
        if pillar in mapping and level_clean in mapping[pillar]:
             return mapping[pillar][level_clean]
        
        # Fallback to Engineering if present
        if "Engineering" in mapping and level_clean in mapping["Engineering"]:
             return mapping["Engineering"][level_clean]
             
        # Try numeric part in any pillar
        try:
            level_num = str(int(level_clean))
            for p_map in mapping.values():
                if isinstance(p_map, dict) and level_num in p_map:
                    return p_map[level_num]
        except (ValueError, TypeError):
            pass
            
    # 2. Try Cache
    cache = _load_cache()
    cache_key = f"{company_clean}:{pillar}:{level_clean}"
    if cache_key in cache:
        return cache[cache_key]
    
    # 3. AI Fallback
    res = await infer_level_async(company_clean, level_clean, position)
    if res:
        cache[cache_key] = res
        _save_cache(cache)
    return res

def get_universal_level(company: str, company_level: str, position: str = "Software Engineer") -> Optional[int]:
    """
    Sync version (no AI fallback).
    """
    company_clean = company.strip().title()
    level_clean = company_level.strip().upper()
    pillar = detect_pillar(position)
    
    if company_clean in COMPANY_LEVEL_MAP:
        mapping = COMPANY_LEVEL_MAP[company_clean]
        if pillar in mapping and level_clean in mapping[pillar]:
            return mapping[pillar][level_clean]
        if "Engineering" in mapping and level_clean in mapping["Engineering"]:
            return mapping["Engineering"][level_clean]
            
    return None

def get_level_suggestions(company: str, position: str = "Software Engineer") -> List[str]:
    """Get common levels for a specific company and position pillar, sorted by seniority."""
    company_clean = company.strip().title()
    pillar = detect_pillar(position)
    
    if company_clean in COMPANY_LEVEL_MAP:
        mapping = COMPANY_LEVEL_MAP[company_clean]
        
        target_map = {}
        # 1. Try Specific Pillar
        if pillar in mapping:
            target_map = mapping[pillar]
        # 2. Fallback to Engineering
        elif "Engineering" in mapping:
            target_map = mapping["Engineering"]
            
        if target_map:
            # Sort by value (seniority), then key (name)
            items = target_map.items()
            # Sort Key: (LevelValue, LevelName)
            # LevelName sort helps if Values are equal (e.g. L4 vs L4A)
            try:
                sorted_items = sorted(items, key=lambda x: (x[1], x[0]))
            except TypeError:
                # Fallback if x[1] is None or inconsistent types? Shouldn't happen based on static map
                sorted_items = sorted(items, key=lambda x: str(x[0]))
                
            return [k for k, v in sorted_items]
            
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
