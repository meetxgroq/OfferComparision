"""
Tests for utils.country_data — profiles, location → country, relocation factors.
"""

import pytest

from utils.country_data import (
    COUNTRY_PROFILES,
    get_all_countries,
    get_relocation_factors,
    infer_country,
)

REQUIRED_PROFILE_KEYS = (
    "currency",
    "tax_regime",
    "max_marginal_rate",
    "major_tech_hubs",
    "social_security",
    "healthcare",
    "visa_for_work",
    "retirement_system",
    "quality_of_life_index",
    "safety_index",
    "typical_benefits",
    "considerations",
)

RELOCATION_KEYS = (
    "from_country",
    "to_country",
    "visa_notes",
    "tax_delta_description",
    "from_tax_regime",
    "to_tax_regime",
    "healthcare_comparison",
    "qol_delta",
    "safety_delta",
    "to_considerations",
    "to_typical_benefits",
)


class TestCountryProfiles:
    def test_has_india_uae_united_states(self):
        assert "India" in COUNTRY_PROFILES
        assert "UAE" in COUNTRY_PROFILES
        assert "United States" in COUNTRY_PROFILES

    def test_all_profiles_have_required_keys(self):
        for name, profile in COUNTRY_PROFILES.items():
            for key in REQUIRED_PROFILE_KEYS:
                assert key in profile, f"{name} missing {key}"
            assert isinstance(profile["currency"], str) and profile["currency"]
            assert isinstance(profile["tax_regime"], str)
            assert isinstance(profile["max_marginal_rate"], (int, float))
            assert 0.0 <= float(profile["max_marginal_rate"]) <= 1.0
            assert isinstance(profile["major_tech_hubs"], list)
            assert profile["major_tech_hubs"]
            for hub in profile["major_tech_hubs"]:
                assert isinstance(hub, str)
            assert isinstance(profile["quality_of_life_index"], int)
            assert isinstance(profile["safety_index"], int)
            assert isinstance(profile["typical_benefits"], list)
            assert isinstance(profile["considerations"], list)


class TestInferCountry:
    @pytest.mark.parametrize(
        "location,expected",
        [
            ("Bangalore, India", "India"),
            ("Bengaluru, India", "India"),
            ("San Francisco, CA", "United States"),
            ("SF", "United States"),
            ("Dubai, UAE", "UAE"),
            ("London, United Kingdom", "United Kingdom"),
            ("Paris, France", "France"),
            ("Barcelona, Spain", "Spain"),
            ("Stockholm, Sweden", "Sweden"),
            ("Auckland, New Zealand", "New Zealand"),
        ],
    )
    def test_known_locations(self, location, expected):
        assert infer_country(location) == expected

    def test_unknown_returns_none(self):
        assert infer_country("Fictional City, Nowhere") is None

    def test_remote_returns_none(self):
        assert infer_country("Remote") is None
        assert infer_country("remote") is None


class TestRelocationFactors:
    def test_same_country_returns_none(self):
        assert get_relocation_factors("India", "India") is None

    def test_cross_country_has_required_keys(self):
        out = get_relocation_factors("India", "United States")
        assert out is not None
        for key in RELOCATION_KEYS:
            assert key in out

    def test_unknown_country_returns_none(self):
        assert get_relocation_factors("India", "Atlantis") is None
        assert get_relocation_factors("Narnia", "India") is None


class TestGetAllCountries:
    def test_returns_name_and_currency(self):
        rows = get_all_countries()
        assert isinstance(rows, list)
        assert len(rows) >= 20
        for row in rows:
            assert "name" in row
            assert "currency" in row
            assert "tax_regime" in row
            assert "major_tech_hubs" in row
            assert "quality_of_life_index" in row
            assert row["name"] in COUNTRY_PROFILES
