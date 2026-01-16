"""
OfferCompare Pro - Utility Functions Tests
Comprehensive test coverage for all utility modules
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock

# Import all utilities to test
from utils.call_llm import get_provider_info, call_llm, AI_PROVIDERS
from utils.col_calculator import (
    estimate_annual_expenses, 
    get_location_insights,
    get_cost_index,
    normalize_location
)
from utils.tax_calculator import (
    calculate_net_pay,
    estimate_tax_rate,
    normalize_location_for_tax
)
from utils.market_data import (
    get_market_salary_range,
    calculate_market_percentile,
    get_compensation_insights,
    normalize_position_title,
    infer_experience_level
)
from utils.scoring import (
    calculate_offer_score,
    compare_offers,
    customize_weights,
    normalize_score
)
from utils.company_db import (
    get_company_data,
    search_companies,
    enrich_company_data,
    get_industry_benchmarks
)
from utils.viz_formatter import (
    create_visualization_package,
    format_radar_chart,
    format_comparison_table,
    generate_colors
)
from utils.web_research import research_company, get_market_sentiment


class TestCallLLM:
    """Test LLM interface and provider management."""
    
    def test_get_provider_info(self):
        """Test provider information retrieval."""
        info = get_provider_info()
        
        assert isinstance(info, dict)
        assert "available_providers" in info
        assert "default_provider" in info
        assert "provider_details" in info
        assert isinstance(info["available_providers"], list)
    
    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"})
    def test_provider_detection_with_api_key(self):
        """Test provider detection when API key is available."""
        info = get_provider_info()
        assert "gemini" in info["available_providers"]
    
    @patch.dict(os.environ, {}, clear=True)
    def test_provider_detection_without_api_keys(self):
        """Test provider detection when no API keys are available."""
        info = get_provider_info()
        assert len(info["available_providers"]) == 0

    def test_gemini_3_flash_in_cascade(self):
        """Verify gemini-3-flash is the primary model in the Gemini cascade."""
        gemini_models = AI_PROVIDERS["gemini"]["models"]
        assert "gemini-3-flash" in gemini_models
        assert gemini_models[0] == "gemini-3-flash"


class TestCOLCalculator:
    """Test cost of living calculation functions."""
    
    def test_normalize_location(self):
        """Test location name normalization."""
        assert normalize_location("san francisco") == "San Francisco, CA"
        assert normalize_location("NYC") == "New York, NY"
        assert normalize_location("Seattle") == "Seattle, WA"
        assert normalize_location("Unknown City") == "Unknown City"
    
    def test_get_cost_index(self):
        """Test cost index retrieval."""
        sf_index = get_cost_index("San Francisco, CA")
        assert sf_index == 100.0
        
        seattle_index = get_cost_index("Seattle, WA") 
        assert isinstance(seattle_index, (int, float))
        assert seattle_index > 0
        
        unknown_index = get_cost_index("Unknown City")
        assert unknown_index == 75.0  # Default fallback
    
    def test_estimate_annual_expenses(self):
        """Test annual expense estimation."""
        result = estimate_annual_expenses("Austin, TX")
        
        assert isinstance(result, dict)
        assert "location" in result
        assert "cost_index" in result
        assert "estimated_annual_expenses" in result
        assert result["location"] == "Austin, TX"
        assert result["estimated_annual_expenses"] > 0
    
    def test_calculate_net_pay(self):
        """Test net pay calculation after taxes."""
        result = calculate_net_pay(150000, "Seattle, WA")
        
        assert isinstance(result, dict)
        assert "gross_pay" in result
        assert "estimated_net_pay" in result
        assert "estimated_tax_amount" in result
        assert result["gross_pay"] == 150000
        assert result["estimated_net_pay"] == 150000 * 0.74 # 26% tax in WA
    
    def test_get_location_insights(self):
        """Test location insights generation."""
        insights = get_location_insights("Seattle, WA")
        
        assert isinstance(insights, dict)
        assert "location" in insights
        assert "cost_category" in insights
        assert "relative_to_sf" in insights
        assert "analysis" in insights


class TestMarketData:
    """Test market data and salary analysis functions."""
    
    def test_normalize_position_title(self):
        """Test position title normalization."""
        assert normalize_position_title("software engineer") == "Software Engineer"
        assert normalize_position_title("Sr. SWE") == "Senior Software Engineer"
        assert normalize_position_title("PM") == "Product Manager"
        assert normalize_position_title("Unknown Role") == "Unknown Role"
    
    def test_infer_experience_level(self):
        """Test experience level inference."""
        assert infer_experience_level(1) == "entry_level"
        assert infer_experience_level(3) == "mid_level"
        assert infer_experience_level(7) == "staff_level"
        assert infer_experience_level(12) == "principal_level"
    
    def test_get_market_salary_range(self):
        """Test market salary range retrieval."""
        result = get_market_salary_range("Software Engineer", "Seattle, WA", "mid_level")
        
        assert isinstance(result, dict)
        assert "position" in result
        assert "location" in result
        assert "adjusted_range" in result
        assert "location_multiplier" in result
        
        salary_range = result["adjusted_range"]
        assert "min" in salary_range
        assert "median" in salary_range
        assert "max" in salary_range
        assert salary_range["min"] < salary_range["median"] < salary_range["max"]
    
    def test_calculate_market_percentile(self):
        """Test market percentile calculation."""
        result = calculate_market_percentile(150000, "Senior Software Engineer", "Seattle, WA")
        
        assert isinstance(result, dict)
        assert "market_percentile" in result
        assert "category" in result
        assert "competitiveness" in result
        assert 0 <= result["market_percentile"] <= 100
        assert result["category"] in ["Below Market", "Market Rate", "Above Market", "Top Tier"]
    
    def test_get_compensation_insights(self):
        """Test compensation insights generation."""
        result = get_compensation_insights("Software Engineer", "Seattle, WA", 140000, 5)
        
        assert isinstance(result, dict)
        assert "position_analysis" in result
        assert "market_comparison" in result
        assert "location_analysis" in result
        assert "experience_fit" in result


class TestScoringEngine:
    """Test scoring and comparison functions."""
    
    def test_normalize_score(self):
        """Test score normalization."""
        assert normalize_score(50, 0, 100) == 50.0
        assert normalize_score(75, 50, 100) == 50.0  # Normalized to 0-100 scale
        assert normalize_score(0, 0, 10) == 0.0
        assert normalize_score(10, 0, 10) == 100.0
    
    def test_calculate_offer_score(self):
        """Test offer scoring calculation."""
        offer_data = {
            "id": "test_offer",
            "company": "Test Company",
            "position": "Software Engineer",
            "location": "Seattle, WA",
            "base_salary": 150000,
            "equity": 30000,
            "market_analysis": {"market_percentile": 70},
            "total_comp_analysis": {"market_percentile": 75},
            "company_research": {
                "stage": "growth",
                "metrics": {
                    "wlb_score": {"score": 8},
                    "growth_score": {"score": 9},
                    "culture_score": {"score": 7},
                    "benefits_score": {"score": 8},
                    "stability_score": {"score": 8}
                }
            }
        }
        
        result = calculate_offer_score(offer_data)
        
        assert isinstance(result, dict)
        assert "total_score" in result
        assert "rating" in result
        assert "factor_scores" in result
        assert "top_strengths" in result
        assert "improvement_areas" in result
        assert 0 <= result["total_score"] <= 100
        assert result["rating"] in ["Poor", "Fair", "Good", "Very Good", "Excellent"]
    
    def test_compare_offers(self):
        """Test offer comparison functionality."""
        offers = [
            {"id": "offer1", "company": "Company A", "base_salary": 150000, "equity": 20000},
            {"id": "offer2", "company": "Company B", "base_salary": 140000, "equity": 30000}
        ]
        
        # Add required fields for scoring
        for offer in offers:
            offer.update({
                "position": "Software Engineer",
                "location": "Seattle, WA",
                "market_analysis": {"market_percentile": 70},
                "total_comp_analysis": {"market_percentile": 75},
                "company_research": {
                    "stage": "growth",
                    "metrics": {
                        "wlb_score": {"score": 8},
                        "growth_score": {"score": 8},
                        "culture_score": {"score": 7},
                        "benefits_score": {"score": 8},
                        "stability_score": {"score": 8}
                    }
                }
            })
        
        result = compare_offers(offers)
        
        assert isinstance(result, dict)
        assert "ranked_offers" in result
        assert "top_offer" in result
        assert "comparison_summary" in result
        assert len(result["ranked_offers"]) == 2
    
    def test_customize_weights(self):
        """Test weight customization."""
        priorities = {
            "salary_focused": True,
            "growth_focused": False,
            "balance_focused": False
        }
        
        weights = customize_weights(priorities)
        
        assert isinstance(weights, dict)
        assert "base_salary" in weights
        assert "total_compensation" in weights
        assert sum(weights.values()) == pytest.approx(1.0, rel=1e-2)
        
        # Salary focused should have higher salary weights
        assert weights["base_salary"] > 0.28


class TestCompanyDB:
    """Test company database functions."""
    
    def test_get_company_data(self):
        """Test company data retrieval."""
        google_data = get_company_data("Google")
        
        assert isinstance(google_data, dict)
        assert "industry" in google_data
        assert "size" in google_data
        assert "culture_metrics" in google_data
        assert "benefits" in google_data
        assert "glassdoor_rating" in google_data
    
    def test_search_companies(self):
        """Test company search functionality."""
        results = search_companies("goog")
        
        assert isinstance(results, list)
        if results:  # If any matches found
            assert "name" in results[0]
            assert "match_score" in results[0]
    
    def test_enrich_company_data(self):
        """Test company data enrichment."""
        basic_data = {
            "position_context": "Software Engineer",
            "location": "Seattle, WA"
        }
        
        enriched = enrich_company_data("Test Company", basic_data)
        
        assert isinstance(enriched, dict)
        assert "industry" in enriched
        assert "size" in enriched
        assert "stage" in enriched
        assert enriched["position_context"] == "Software Engineer"
    
    def test_get_industry_benchmarks(self):
        """Test industry benchmarks retrieval."""
        benchmarks = get_industry_benchmarks("Technology")
        
        assert isinstance(benchmarks, dict)
        assert "industry" in benchmarks
        assert "avg_culture_score" in benchmarks
        assert "avg_wlb_score" in benchmarks
        assert "common_benefits" in benchmarks


class TestVizFormatter:
    """Test visualization formatting functions."""
    
    def test_generate_colors(self):
        """Test color generation."""
        colors = generate_colors(5)
        
        assert isinstance(colors, list)
        assert len(colors) == 5
        assert all(color.startswith("#") for color in colors)
        assert all(len(color) == 7 for color in colors)  # hex format
    
    def test_format_comparison_table(self):
        """Test comparison table formatting."""
        offers = [
            {
                "company": "Company A",
                "position": "Software Engineer",
                "base_salary": 150000,
                "total_score": 85.5,
                "rating": "Very Good",
                "top_strengths": [{"factor": "salary", "score": 90}],
                "improvement_areas": [{"factor": "culture", "score": 60}]
            }
        ]
        
        result = format_comparison_table(offers)
        
        assert isinstance(result, dict)
        assert "headers" in result
        assert "rows" in result
        assert "best_values" in result
        assert isinstance(result["headers"], list)
        assert isinstance(result["rows"], list)
    
    def test_create_visualization_package(self):
        """Test complete visualization package creation."""
        offers = [
            {
                "company": "Company A",
                "base_salary": 150000,
                "total_compensation": 200000,
                "total_score": 85,
                "factor_scores": {
                    "base_salary": 80,
                    "work_life_balance": 90,
                    "career_growth": 85
                },
                "market_analysis": {"market_percentile": 75}
            }
        ]
        
        result = create_visualization_package(offers)
        
        assert isinstance(result, dict)
        assert "radar_chart" in result
        assert "overall_scores" in result
        assert "salary_comparison" in result
        assert "comparison_table" in result
        assert "summary_stats" in result


class TestWebResearch:
    """Test web research functions (mocked)."""
    
    @patch('utils.web_research.call_llm')
    @patch('utils.web_research.call_llm_structured')
    def test_research_company(self, mock_structured, mock_llm):
        """Test company research functionality."""
        # Mock LLM responses
        mock_llm.return_value = "Comprehensive company analysis..."
        mock_structured.return_value = json.dumps({
            "culture_score": {"score": 8, "explanation": "Great culture"},
            "wlb_score": {"score": 7, "explanation": "Good work-life balance"},
            "growth_score": {"score": 9, "explanation": "High growth potential"},
            "benefits_score": {"score": 8, "explanation": "Excellent benefits"},
            "stability_score": {"score": 8, "explanation": "Stable company"},
            "reputation_score": {"score": 9, "explanation": "Great reputation"},
            "key_strengths": ["innovation", "culture"],
            "potential_concerns": ["work pressure"],
            "recent_highlights": ["new product launch"]
        })
        
        result = research_company("Google", "Software Engineer")
        
        assert isinstance(result, dict)
        assert "company_name" in result
        assert "research_analysis" in result
        assert "metrics" in result
        assert "research_timestamp" in result
        
        # Verify metrics structure
        metrics = result["metrics"]
        assert "culture_score" in metrics
        assert "wlb_score" in metrics
        assert "key_strengths" in metrics
    
    @patch('utils.web_research.call_llm')
    def test_get_market_sentiment(self, mock_llm):
        """Test market sentiment analysis."""
        mock_llm.return_value = "Positive market sentiment analysis..."
        
        result = get_market_sentiment("Google", "Software Engineer")
        
        assert isinstance(result, dict)
        assert "company_name" in result
        assert "sentiment_analysis" in result
        assert "analysis_timestamp" in result


# Test data fixtures
@pytest.fixture
def sample_offer():
    """Sample offer data for testing."""
    return {
        "id": "test_offer_1",
        "company": "Test Company",
        "position": "Senior Software Engineer",
        "location": "Seattle, WA",
        "base_salary": 150000,
        "equity": 30000,
        "bonus": 20000,
        "total_compensation": 200000,
        "years_experience": 5,
        "vesting_years": 4
    }

@pytest.fixture
def sample_offers_list():
    """Sample offers list for testing."""
    return [
        {
            "id": "offer_1",
            "company": "Google",
            "position": "Senior Software Engineer",
            "location": "Seattle, WA",
            "base_salary": 180000,
            "equity": 50000,
            "bonus": 20000,
            "total_compensation": 250000,
            "years_experience": 6,
            "vesting_years": 4
        },
        {
            "id": "offer_2", 
            "company": "Microsoft",
            "position": "Senior Software Engineer",
            "location": "Seattle, WA",
            "base_salary": 175000,
            "equity": 40000,
            "bonus": 25000,
            "total_compensation": 240000,
            "years_experience": 6,
            "vesting_years": 4
        }
    ]


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 