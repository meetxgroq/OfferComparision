"""
BenchMarked - Pytest Configuration and Shared Fixtures
Shared test fixtures and configuration for all test modules
"""

import pytest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from typing import Dict, List, Any


# Test configuration
def pytest_configure(config):
    """Configure pytest execution."""
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance benchmarks")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "api: Tests requiring API access")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Mark API tests
        if "test_web_research" in item.name or "call_llm" in item.name:
            item.add_marker(pytest.mark.api)
        
        # Mark performance tests
        if "performance" in item.name or "benchmark" in item.name:
            item.add_marker(pytest.mark.performance)
        
        # Mark integration tests
        if "integration" in item.name or "flow" in item.name:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)


# Core fixtures
@pytest.fixture
def sample_offer() -> Dict[str, Any]:
    """Single sample offer for testing."""
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
def sample_offers() -> List[Dict[str, Any]]:
    """Multiple sample offers for testing."""
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
            "location": "Redmond, WA",
            "base_salary": 175000,
            "equity": 40000,
            "bonus": 25000,
            "total_compensation": 240000,
            "years_experience": 6,
            "vesting_years": 4
        },
        {
            "id": "offer_3",
            "company": "Amazon",
            "position": "Senior Software Engineer", 
            "location": "Seattle, WA",
            "base_salary": 170000,
            "equity": 60000,
            "bonus": 15000,
            "total_compensation": 245000,
            "years_experience": 6,
            "vesting_years": 4
        }
    ]


@pytest.fixture
def sample_user_preferences() -> Dict[str, Any]:
    """Sample user preferences for testing."""
    return {
        "growth_focused": True,
        "salary_focused": False,
        "balance_focused": False,
        "base_location": "San Francisco, CA",
        "location_preferences": {
            "Seattle, WA": 85,
            "Remote": 95,
            "San Francisco, CA": 70
        },
        "custom_weights": {}
    }


@pytest.fixture 
def sample_shared_data(sample_offers, sample_user_preferences) -> Dict[str, Any]:
    """Complete shared data structure for testing."""
    return {
        "offers": sample_offers,
        "user_preferences": sample_user_preferences
    }


@pytest.fixture
def enriched_offer() -> Dict[str, Any]:
    """Fully enriched offer with all analysis data."""
    return {
        "id": "enriched_offer_1",
        "company": "Google",
        "position": "Senior Software Engineer",
        "location": "Seattle, WA", 
        "base_salary": 180000,
        "equity": 50000,
        "bonus": 20000,
        "total_compensation": 250000,
        "years_experience": 6,
        "vesting_years": 4,
        "company_research": {
            "company_name": "Google",
            "research_analysis": "Top-tier technology company...",
            "metrics": {
                "culture_score": {"score": 8, "explanation": "Strong culture"},
                "wlb_score": {"score": 7, "explanation": "Good work-life balance"},
                "growth_score": {"score": 9, "explanation": "Excellent growth opportunities"},
                "benefits_score": {"score": 9, "explanation": "Outstanding benefits"},
                "stability_score": {"score": 9, "explanation": "Very stable company"},
                "reputation_score": {"score": 10, "explanation": "Industry leader"},
                "key_strengths": ["innovation", "compensation", "brand"],
                "potential_concerns": ["work intensity", "bureaucracy"],
                "recent_highlights": ["AI breakthroughs", "strong earnings"]
            }
        },
        "market_sentiment": {
            "company_name": "Google",
            "sentiment_analysis": "Very positive market sentiment...",
            "analysis_timestamp": "2024-01-01"
        },
        "col_analysis": {
            "adjusted_salary": 168000,
            "adjustment_factor": 0.933,
            "purchasing_power_ratio": 1.07,
            "cost_difference_percent": -6.7
        },
        "market_analysis": {
            "market_percentile": 85,
            "competitiveness": "Above Market",
            "category": "Above Market"
        },
        "total_comp_analysis": {
            "market_percentile": 90,
            "competitiveness": "Top Tier", 
            "category": "Top Tier"
        },
        "total_score": 87.5,
        "rating": "Excellent",
        "factor_scores": {
            "base_salary": 85,
            "total_compensation": 90,
            "equity_upside": 80,
            "work_life_balance": 75,
            "career_growth": 95,
            "company_culture": 85,
            "benefits_quality": 90,
            "location_preference": 80
        }
    }


# Mock fixtures
@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    def _mock_response(prompt="", **kwargs):
        return "Mocked LLM response for testing purposes."
    return _mock_response


@pytest.fixture
def mock_structured_llm_response():
    """Mock structured LLM response for testing."""
    def _mock_response(prompt="", **kwargs):
        return json.dumps({
            "culture_score": {"score": 8, "explanation": "Good culture"},
            "wlb_score": {"score": 7, "explanation": "Good work-life balance"},
            "growth_score": {"score": 9, "explanation": "High growth potential"},
            "benefits_score": {"score": 8, "explanation": "Good benefits"},
            "stability_score": {"score": 8, "explanation": "Stable company"},
            "reputation_score": {"score": 9, "explanation": "Great reputation"},
            "key_strengths": ["innovation", "culture", "compensation"],
            "potential_concerns": ["work pressure", "competition"],
            "recent_highlights": ["product launch", "positive earnings"]
        })
    return _mock_response


@pytest.fixture
def mock_api_calls(mock_llm_response, mock_structured_llm_response):
    """Mock all external API calls."""
    with patch('utils.web_research.call_llm', side_effect=mock_llm_response), \
         patch('utils.web_research.call_llm_structured', side_effect=mock_structured_llm_response), \
         patch('utils.market_data.call_llm', side_effect=mock_llm_response), \
         patch('nodes.call_llm', side_effect=mock_llm_response):
        yield


# Temporary file fixtures
@pytest.fixture
def temp_dir():
    """Temporary directory for testing file operations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def temp_json_file():
    """Temporary JSON file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        yield f.name
    # Clean up
    if os.path.exists(f.name):
        os.unlink(f.name)


# Environment fixtures  
@pytest.fixture
def clean_env():
    """Clean environment without API keys."""
    api_keys = ['OPENAI_API_KEY', 'GEMINI_API_KEY', 'ANTHROPIC_API_KEY']
    original_values = {}
    
    # Store original values
    for key in api_keys:
        original_values[key] = os.environ.get(key)
        if key in os.environ:
            del os.environ[key]
    
    yield
    
    # Restore original values
    for key, value in original_values.items():
        if value is not None:
            os.environ[key] = value


@pytest.fixture
def mock_gemini_env():
    """Environment with mock Gemini API key."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_gemini_key"}):
        yield


@pytest.fixture  
def mock_all_providers_env():
    """Environment with all AI provider API keys."""
    with patch.dict(os.environ, {
        "GEMINI_API_KEY": "test_gemini_key",
        "OPENAI_API_KEY": "test_openai_key", 
        "ANTHROPIC_API_KEY": "test_anthropic_key"
    }):
        yield


# Test data validation fixtures
@pytest.fixture
def validate_offer_structure():
    """Validator for offer data structure."""
    def _validate(offer_data):
        required_fields = [
            "id", "company", "position", "location",
            "base_salary", "equity", "bonus", "total_compensation",
            "years_experience", "vesting_years"
        ]
        
        for field in required_fields:
            assert field in offer_data, f"Missing required field: {field}"
            
        # Type validation
        assert isinstance(offer_data["base_salary"], (int, float))
        assert isinstance(offer_data["equity"], (int, float))
        assert isinstance(offer_data["bonus"], (int, float))
        assert isinstance(offer_data["years_experience"], int)
        assert isinstance(offer_data["vesting_years"], int)
        
        # Value validation
        assert offer_data["base_salary"] > 0
        assert offer_data["equity"] >= 0
        assert offer_data["bonus"] >= 0
        assert offer_data["years_experience"] >= 0
        assert offer_data["vesting_years"] > 0
    
    return _validate


# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer for performance testing."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


# Skip markers for conditional tests
def pytest_runtest_setup(item):
    """Setup function to handle conditional test skipping."""
    # Skip API tests unless explicitly requested
    if item.get_closest_marker("api"):
        if not item.config.getoption("--run-api", default=False):
            pytest.skip("API tests skipped (use --run-api to include)")


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-api",
        action="store_true",
        default=False,
        help="Run tests that require API access"
    )
    parser.addoption(
        "--run-slow",
        action="store_true", 
        default=False,
        help="Run slow tests"
    ) 