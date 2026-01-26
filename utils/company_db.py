"""
Company Database - Culture metrics and benefits data
Maintains database of company information and default metrics
"""

import json
from typing import Dict, Any, Optional, List

# Comprehensive company database with culture and benefits metrics
COMPANY_DATABASE = {
    # FAANG/Big Tech
    "Google": {
        "industry": "Technology",
        "size": "Large (>50k employees)",
        "stage": "public",
        "founded": 1998,
        "headquarters": "Mountain View, CA",
        "culture_metrics": {
            "innovation": 9.2,
            "work_life_balance": 7.8,
            "career_growth": 8.5,
            "compensation": 9.0,
            "management": 7.5,
            "diversity": 7.8,
            "company_outlook": 8.2
        },
        "benefits": {
            "health_insurance": "Excellent",
            "dental_vision": "Excellent", 
            "retirement_401k": "6% match",
            "pto_vacation": "Flexible PTO",
            "parental_leave": "18 weeks paid",
            "mental_health": "Comprehensive",
            "fitness_wellness": "On-site gyms, wellness programs",
            "food_perks": "Free meals, snacks",
            "learning_development": "$5,000 annual budget",
            "remote_work": "Hybrid flexible",
            "unique_perks": ["20% time for side projects", "Sabbatical program", "Employee resource groups"]
        },
        "glassdoor_rating": 4.3,
        "ceo_approval": 87
    },
    
    "Apple": {
        "industry": "Technology",
        "size": "Large (>50k employees)",
        "stage": "public",
        "founded": 1976,
        "headquarters": "Cupertino, CA",
        "culture_metrics": {
            "innovation": 8.8,
            "work_life_balance": 7.2,
            "career_growth": 7.8,
            "compensation": 8.7,
            "management": 7.3,
            "diversity": 7.5,
            "company_outlook": 8.5
        },
        "benefits": {
            "health_insurance": "Excellent",
            "dental_vision": "Excellent",
            "retirement_401k": "6% match",
            "pto_vacation": "3-4 weeks",
            "parental_leave": "12 weeks paid",
            "mental_health": "Good",
            "fitness_wellness": "On-site fitness",
            "food_perks": "Subsidized meals",
            "learning_development": "Extensive programs",
            "remote_work": "Limited remote",
            "unique_perks": ["Product discounts", "Stock purchase plan", "Tuition reimbursement"]
        },
        "glassdoor_rating": 4.1,
        "ceo_approval": 82
    },
    
    "Microsoft": {
        "industry": "Technology", 
        "size": "Large (>50k employees)",
        "stage": "public",
        "founded": 1975,
        "headquarters": "Redmond, WA",
        "culture_metrics": {
            "innovation": 8.3,
            "work_life_balance": 8.5,
            "career_growth": 8.2,
            "compensation": 8.5,
            "management": 8.0,
            "diversity": 8.2,
            "company_outlook": 8.7
        },
        "benefits": {
            "health_insurance": "Excellent",
            "dental_vision": "Excellent",
            "retirement_401k": "5% match",
            "pto_vacation": "Flexible PTO",
            "parental_leave": "20 weeks paid",
            "mental_health": "Excellent",
            "fitness_wellness": "Comprehensive wellness",
            "food_perks": "Subsidized cafeterias",
            "learning_development": "Unlimited LinkedIn Learning",
            "remote_work": "Hybrid flexible",
            "unique_perks": ["Xbox Game Pass", "Surface devices", "Volunteer time off"]
        },
        "glassdoor_rating": 4.4,
        "ceo_approval": 91
    },
    
    "Amazon": {
        "industry": "Technology/E-commerce",
        "size": "Large (>100k employees)",
        "stage": "public", 
        "founded": 1994,
        "headquarters": "Seattle, WA",
        "culture_metrics": {
            "innovation": 8.7,
            "work_life_balance": 6.8,
            "career_growth": 8.0,
            "compensation": 8.2,
            "management": 6.9,
            "diversity": 7.5,
            "company_outlook": 7.8
        },
        "benefits": {
            "health_insurance": "Good",
            "dental_vision": "Good",
            "retirement_401k": "4% match",
            "pto_vacation": "2-3 weeks",
            "parental_leave": "14 weeks paid",
            "mental_health": "Good",
            "fitness_wellness": "Basic programs",
            "food_perks": "Subsidized meals",
            "learning_development": "Career Choice program",
            "remote_work": "Role dependent",
            "unique_perks": ["Stock units", "Employee discount", "Tuition assistance"]
        },
        "glassdoor_rating": 3.9,
        "ceo_approval": 74
    },
    
    "Meta": {
        "industry": "Technology/Social Media",
        "size": "Large (>50k employees)",
        "stage": "public",
        "founded": 2004,
        "headquarters": "Menlo Park, CA",
        "culture_metrics": {
            "innovation": 8.5,
            "work_life_balance": 7.5,
            "career_growth": 8.0,
            "compensation": 9.2,
            "management": 7.2,
            "diversity": 7.8,
            "company_outlook": 7.0
        },
        "benefits": {
            "health_insurance": "Excellent",
            "dental_vision": "Excellent",
            "retirement_401k": "7% match",
            "pto_vacation": "Flexible PTO",
            "parental_leave": "16 weeks paid",
            "mental_health": "Excellent",
            "fitness_wellness": "Comprehensive programs",
            "food_perks": "Free meals, snacks",
            "learning_development": "$5,000 annual budget",
            "remote_work": "Flexible hybrid",
            "unique_perks": ["$10k baby bonus", "Commuter benefits", "Wellness stipend"]
        },
        "glassdoor_rating": 4.2,
        "ceo_approval": 73
    },
    
    # Other Major Tech Companies
    "Netflix": {
        "industry": "Technology/Streaming",
        "size": "Medium (10k-50k employees)",
        "stage": "public",
        "founded": 1997,
        "headquarters": "Los Gatos, CA",
        "culture_metrics": {
            "innovation": 8.8,
            "work_life_balance": 7.0,
            "career_growth": 7.8,
            "compensation": 9.5,
            "management": 7.5,
            "diversity": 8.0,
            "company_outlook": 8.0
        },
        "benefits": {
            "health_insurance": "Excellent",
            "dental_vision": "Excellent",
            "retirement_401k": "4% match",
            "pto_vacation": "Unlimited PTO",
            "parental_leave": "12 months paid",
            "mental_health": "Good",
            "fitness_wellness": "Stipend provided",
            "food_perks": "Free snacks, drinks",
            "learning_development": "Extensive programs",
            "remote_work": "Flexible",
            "unique_perks": ["High pay philosophy", "Performance culture", "Stock options"]
        },
        "glassdoor_rating": 4.1,
        "ceo_approval": 85
    },

    "LinkedIn": {
        "industry": "Technology/Social Network",
        "size": "Large (10k-50k employees)",
        "stage": "public",
        "founded": 2003,
        "headquarters": "Sunnyvale, CA",
        "culture_metrics": {
            "innovation": 8.2,
            "work_life_balance": 8.4,
            "career_growth": 8.3,
            "compensation": 8.6,
            "management": 8.1,
            "diversity": 8.4,
            "company_outlook": 8.0
        },
        "benefits": {
            "health_insurance": "Excellent",
            "dental_vision": "Excellent",
            "retirement_401k": "3% match",
            "pto_vacation": "Flexible PTO",
            "parental_leave": "16 weeks paid",
            "mental_health": "Extensive",
            "fitness_wellness": "On-site gyms, wellness stipend",
            "food_perks": "Free meals, snacks, gourmet drinks",
            "learning_development": "$5,000 annual budget, LinkedIn Learning",
            "remote_work": "Hybrid flexible",
            "unique_perks": ["InDay", "Generous volunteer time off", "Education reimbursement"]
        },
        "glassdoor_rating": 4.2,
        "ceo_approval": 92
    },
    
    "Salesforce": {
        "industry": "Technology/SaaS",
        "size": "Large (>50k employees)",
        "stage": "public",
        "founded": 1999,
        "headquarters": "San Francisco, CA",
        "culture_metrics": {
            "innovation": 8.0,
            "work_life_balance": 8.2,
            "career_growth": 8.3,
            "compensation": 8.0,
            "management": 8.0,
            "diversity": 8.5,
            "company_outlook": 8.2
        },
        "benefits": {
            "health_insurance": "Excellent",
            "dental_vision": "Excellent",
            "retirement_401k": "6% match",
            "pto_vacation": "Flexible PTO",
            "parental_leave": "26 weeks paid",
            "mental_health": "Excellent",
            "fitness_wellness": "Comprehensive programs",
            "food_perks": "Free meals, snacks",
            "learning_development": "Trailhead platform",
            "remote_work": "Work from anywhere",
            "unique_perks": ["Volunteer time off", "Mindfulness programs", "Equality initiatives"]
        },
        "glassdoor_rating": 4.4,
        "ceo_approval": 90
    },
    
    # Startups and Growth Companies
    "Stripe": {
        "industry": "Technology/FinTech",
        "size": "Medium (3k-10k employees)",
        "stage": "private",
        "founded": 2010,
        "headquarters": "San Francisco, CA",
        "culture_metrics": {
            "innovation": 9.0,
            "work_life_balance": 7.5,
            "career_growth": 8.5,
            "compensation": 8.8,
            "management": 8.2,
            "diversity": 8.0,
            "company_outlook": 8.8
        },
        "benefits": {
            "health_insurance": "Excellent",
            "dental_vision": "Excellent",
            "retirement_401k": "6% match",
            "pto_vacation": "Flexible PTO",
            "parental_leave": "16 weeks paid",
            "mental_health": "Good",
            "fitness_wellness": "Stipend provided",
            "food_perks": "Meal stipends",
            "learning_development": "$3,000 annual budget",
            "remote_work": "Remote first",
            "unique_perks": ["Home office stipend", "Continuous learning budget", "Global remote work"]
        },
        "glassdoor_rating": 4.6,
        "ceo_approval": 95
    },
    
    "Airbnb": {
        "industry": "Technology/Travel",
        "size": "Medium (5k-10k employees)",
        "stage": "public",
        "founded": 2008,
        "headquarters": "San Francisco, CA",
        "culture_metrics": {
            "innovation": 8.5,
            "work_life_balance": 8.0,
            "career_growth": 8.0,
            "compensation": 8.5,
            "management": 7.8,
            "diversity": 8.2,
            "company_outlook": 7.8
        },
        "benefits": {
            "health_insurance": "Excellent",
            "dental_vision": "Excellent",
            "retirement_401k": "5% match",
            "pto_vacation": "Flexible PTO",
            "parental_leave": "22 weeks paid",
            "mental_health": "Good",
            "fitness_wellness": "Wellness stipend",
            "food_perks": "Meal allowances",
            "learning_development": "Good programs",
            "remote_work": "Work from anywhere",
            "unique_perks": ["Annual travel stipend", "Belonging initiatives", "Work anywhere program"]
        },
        "glassdoor_rating": 4.3,
        "ceo_approval": 87
    }
}

def get_company_data(company_name: str) -> Optional[Dict[str, Any]]:
    """
    Get comprehensive company data.
    
    Args:
        company_name (str): Name of the company
    
    Returns:
        dict: Company data or None if not found
    """
    # Normalize company name
    normalized_name = normalize_company_name(company_name)
    
    # Direct lookup
    if normalized_name in COMPANY_DATABASE:
        return COMPANY_DATABASE[normalized_name].copy()
    
    # Fuzzy matching
    for db_name in COMPANY_DATABASE.keys():
        if normalized_name.lower() in db_name.lower() or db_name.lower() in normalized_name.lower():
            return COMPANY_DATABASE[db_name].copy()
    
    return None

def normalize_company_name(company_name: str) -> str:
    """
    Normalize company name for consistent lookup.
    
    Args:
        company_name (str): Raw company name
    
    Returns:
        str: Normalized company name
    """
    # Remove common suffixes and normalize
    name = company_name.strip()
    
    # Handle common variations
    name_mappings = {
        "Google Inc": "Google",
        "Alphabet": "Google", 
        "Apple Inc": "Apple",
        "Microsoft Corporation": "Microsoft",
        "Amazon.com": "Amazon",
        "Meta Platforms": "Meta",
        "Facebook": "Meta",
        "Instagram": "Meta",
        "WhatsApp": "Meta"
    }
    
    if name in name_mappings:
        return name_mappings[name]
    
    # Remove common suffixes
    suffixes = [" Inc", " Inc.", " Corporation", " Corp", " Corp.", " LLC", " Ltd", " Ltd.", " Co", " Co."]
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break
    
    return name.strip()

def get_default_metrics(company_stage: str = "growth") -> Dict[str, float]:
    """
    Get default culture metrics based on company stage.
    
    Args:
        company_stage (str): Company stage (startup, growth, public, etc.)
    
    Returns:
        dict: Default culture metrics
    """
    stage_defaults = {
        "startup": {
            "innovation": 8.5,
            "work_life_balance": 6.5,
            "career_growth": 8.0,
            "compensation": 7.0,
            "management": 7.0,
            "diversity": 7.0,
            "company_outlook": 7.5
        },
        "growth": {
            "innovation": 8.0,
            "work_life_balance": 7.0,
            "career_growth": 7.5,
            "compensation": 7.5,
            "management": 7.2,
            "diversity": 7.2,
            "company_outlook": 7.8
        },
        "public": {
            "innovation": 7.5,
            "work_life_balance": 7.5,
            "career_growth": 7.2,
            "compensation": 8.0,
            "management": 7.5,
            "diversity": 7.5,
            "company_outlook": 7.5
        },
        "established": {
            "innovation": 7.0,
            "work_life_balance": 8.0,
            "career_growth": 7.0,
            "compensation": 8.2,
            "management": 7.8,
            "diversity": 7.8,
            "company_outlook": 7.2
        }
    }
    
    return stage_defaults.get(company_stage, stage_defaults["growth"])

def get_default_benefits(company_size: str = "medium") -> Dict[str, str]:
    """
    Get default benefits based on company size.
    
    Args:
        company_size (str): Company size category
    
    Returns:
        dict: Default benefits package
    """
    size_defaults = {
        "startup": {
            "health_insurance": "Basic",
            "dental_vision": "Basic",
            "retirement_401k": "3% match",
            "pto_vacation": "2-3 weeks",
            "parental_leave": "6-8 weeks",
            "mental_health": "Basic",
            "fitness_wellness": "Stipend",
            "food_perks": "Snacks, coffee",
            "learning_development": "$1,000 budget",
            "remote_work": "Flexible",
            "unique_perks": ["Equity", "Flexible hours", "Casual environment"]
        },
        "medium": {
            "health_insurance": "Good",
            "dental_vision": "Good",
            "retirement_401k": "4% match",
            "pto_vacation": "3-4 weeks",
            "parental_leave": "10-12 weeks",
            "mental_health": "Good",
            "fitness_wellness": "Programs available",
            "food_perks": "Subsidized meals",
            "learning_development": "$2,500 budget",
            "remote_work": "Hybrid",
            "unique_perks": ["Stock options", "Professional development", "Team events"]
        },
        "large": {
            "health_insurance": "Excellent",
            "dental_vision": "Excellent", 
            "retirement_401k": "5-6% match",
            "pto_vacation": "Flexible PTO",
            "parental_leave": "12-16 weeks",
            "mental_health": "Comprehensive",
            "fitness_wellness": "Full programs",
            "food_perks": "Free meals",
            "learning_development": "$5,000 budget",
            "remote_work": "Flexible options",
            "unique_perks": ["Comprehensive benefits", "Career advancement", "Global opportunities"]
        }
    }
    
    return size_defaults.get(company_size, size_defaults["medium"])

def enrich_company_data(company_name: str, basic_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Enrich company data with database information or defaults.
    
    Args:
        company_name (str): Company name
        basic_data (dict): Basic company data from research
    
    Returns:
        dict: Enriched company data
    """
    # Try to get from database first
    db_data = get_company_data(company_name)
    if db_data:
        # Merge with any additional basic data (do not drop provided keys)
        if basic_data:
            merged = db_data.copy()
            merged.update(basic_data)
            return merged
        return db_data
    
    # Create default data structure
    stage = basic_data.get("stage", "growth") if basic_data else "growth"
    size = basic_data.get("size", "medium") if basic_data else "medium"
    
    default_data = {
        "industry": basic_data.get("industry", "Technology") if basic_data else "Technology",
        "size": size,
        "stage": stage,
        "founded": basic_data.get("founded") if basic_data else None,
        "headquarters": basic_data.get("headquarters") if basic_data else None,
        "culture_metrics": get_default_metrics(stage),
        "benefits": get_default_benefits(size),
        "glassdoor_rating": basic_data.get("glassdoor_rating", 4.0) if basic_data else 4.0,
        "ceo_approval": basic_data.get("ceo_approval", 75) if basic_data else 75,
        "data_source": "default_estimates"
    }
    # Preserve basic_data passthrough fields like position_context/location
    if basic_data:
        for k, v in basic_data.items():
            if k not in default_data:
                default_data[k] = v
    
    return default_data

def search_companies(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search companies in database.
    
    Args:
        query (str): Search query
        limit (int): Maximum results to return
    
    Returns:
        list: Matching companies
    """
    query_lower = query.lower()
    matches = []
    
    for company_name, data in COMPANY_DATABASE.items():
        if query_lower in company_name.lower():
            match_data = data.copy()
            match_data["name"] = company_name
            match_data["match_score"] = round(0.8 + (len(query_lower) / max(1, len(company_name))) * 0.2, 2)
            matches.append(match_data)
    
    return matches[:limit]

def get_industry_benchmarks(industry: str = "Technology") -> Dict[str, float]:
    """
    Get industry benchmark metrics.
    
    Args:
        industry (str): Industry name
    
    Returns:
        dict: Industry benchmark metrics
    """
    # Calculate averages from companies in the industry
    industry_companies = [
        data for data in COMPANY_DATABASE.values() 
        if data["industry"].lower().startswith(industry.lower())
    ]
    
    if not industry_companies:
        return {"industry": industry, **get_default_metrics()}
    
    # Calculate averages
    benchmarks = {"industry": industry}
    metric_keys = list(industry_companies[0]["culture_metrics"].keys())
    
    for metric in metric_keys:
        total = sum(company["culture_metrics"][metric] for company in industry_companies)
        benchmarks[metric] = round(total / len(industry_companies), 1)
    # Provide aggregated fields expected by tests
    avg_culture = sum(c["culture_metrics"].get("company_outlook", 7.5) for c in industry_companies) / len(industry_companies)
    avg_wlb = sum(c["culture_metrics"].get("work_life_balance", 7.0) for c in industry_companies) / len(industry_companies)
    benchmarks["avg_culture_score"] = round(avg_culture, 1)
    benchmarks["avg_wlb_score"] = round(avg_wlb, 1)
    # Common benefits across companies in the industry
    from collections import Counter
    benefit_counter = Counter()
    for company in industry_companies:
        benefits = company.get("benefits", {})
        for key, val in benefits.items():
            if isinstance(val, str):
                benefit_counter[key] += 1
    common = [k for k, v in benefit_counter.most_common(5)]
    benchmarks["common_benefits"] = common
    
    return benchmarks

if __name__ == "__main__":
    # Test company database functions
    google_data = get_company_data("Google")
    print("Google Data:", json.dumps(google_data, indent=2))
    
    unknown_company = enrich_company_data("Unknown Startup", {"stage": "startup", "size": "startup"})
    print("Unknown Company Data:", json.dumps(unknown_company, indent=2))
    
    tech_benchmarks = get_industry_benchmarks("Technology")
    print("Tech Industry Benchmarks:", json.dumps(tech_benchmarks, indent=2)) 