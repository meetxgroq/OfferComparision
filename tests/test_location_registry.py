"""Tests for utils.location_registry — canonical location data and helpers."""

import pytest

from utils.location_registry import (
    LOCATION_REGISTRY,
    normalize_location,
    get_tax_rate,
    get_col_index,
    get_salary_multiplier,
    infer_currency,
    infer_country,
    get_all_locations,
)


class TestNormalizeLocation:
    def test_canonical_passthrough(self):
        assert normalize_location("San Francisco, CA") == "San Francisco, CA"

    def test_alias_sf(self):
        assert normalize_location("sf") == "San Francisco, CA"

    def test_alias_bay_area(self):
        assert normalize_location("bay area") == "San Francisco, CA"

    def test_bare_bangalore(self):
        assert normalize_location("Bangalore") == "Bangalore, India"

    def test_bare_hyderabad(self):
        assert normalize_location("Hyderabad") == "Hyderabad, India"

    def test_bengaluru_alias(self):
        assert normalize_location("bengaluru") == "Bangalore, India"

    def test_case_insensitive(self):
        assert normalize_location("SEATTLE, WA") == "Seattle, WA"
        assert normalize_location("london, uk") == "London, UK"

    def test_unknown_passthrough(self):
        result = normalize_location("Atlantis, Underwater")
        assert result == "Atlantis, Underwater"

    def test_remote(self):
        assert normalize_location("Remote") == "Remote"

    def test_whitespace_trimmed(self):
        assert normalize_location("  Seattle, WA  ") == "Seattle, WA"


class TestGetTaxRate:
    def test_sf_rate(self):
        assert get_tax_rate("San Francisco, CA") == 0.38

    def test_bangalore_rate(self):
        assert get_tax_rate("Bangalore, India") == 0.312

    def test_bare_bangalore(self):
        assert get_tax_rate("bangalore") == 0.312

    def test_dubai_zero(self):
        assert get_tax_rate("Dubai, UAE") == 0.0

    def test_unknown_default(self):
        assert get_tax_rate("Atlantis, Underwater") == 0.30


class TestGetColIndex:
    def test_sf_baseline(self):
        assert get_col_index("San Francisco, CA") == 100.0

    def test_hyderabad(self):
        assert get_col_index("Hyderabad, India") == 22.0

    def test_remote(self):
        assert get_col_index("Remote") == 50.0

    def test_unknown_default(self):
        assert get_col_index("Atlantis") == 75.0


class TestGetSalaryMultiplier:
    def test_sf_baseline(self):
        assert get_salary_multiplier("San Francisco, CA") == 1.0

    def test_bangalore(self):
        assert get_salary_multiplier("Bangalore, India") == 0.25

    def test_unknown_default(self):
        assert get_salary_multiplier("Atlantis") == 0.85


class TestInferCurrency:
    def test_bangalore_india(self):
        assert infer_currency("Bangalore, India") == "INR"

    def test_bare_bangalore(self):
        assert infer_currency("bangalore") == "INR"

    def test_dubai_uae(self):
        assert infer_currency("Dubai, UAE") == "AED"

    def test_sf(self):
        assert infer_currency("San Francisco, CA") == "USD"

    def test_london_uk(self):
        assert infer_currency("London, UK") == "GBP"

    def test_suffix_fallback_india(self):
        assert infer_currency("Mysore, India") == "INR"

    def test_unknown_defaults_usd(self):
        assert infer_currency("Atlantis, Underwater") == "USD"

    def test_empty_defaults_usd(self):
        assert infer_currency("") == "USD"

    def test_remote(self):
        assert infer_currency("Remote") == "USD"


class TestCurrencySuffixAmbiguity:
    def test_gary_indiana_gets_usd(self):
        assert infer_currency("Gary, IN") == "USD"

    def test_fake_city_california_gets_usd(self):
        assert infer_currency("Random City, CA") == "USD"

    def test_explicit_india_still_inr(self):
        assert infer_currency("Mysore, India") == "INR"

    def test_toronto_on_gets_cad(self):
        assert infer_currency("Brampton, ON") == "CAD"


class TestInferCountry:
    def test_sf(self):
        assert infer_country("San Francisco, CA") == "United States"

    def test_bangalore(self):
        assert infer_country("Bangalore, India") == "India"

    def test_bare_bangalore(self):
        assert infer_country("bangalore") == "India"

    def test_remote_none(self):
        assert infer_country("Remote") is None

    def test_suffix_fallback_france(self):
        assert infer_country("Nice, France") == "France"

    def test_empty_none(self):
        assert infer_country("") is None


class TestGetAllLocations:
    def test_returns_sorted_list(self):
        locs = get_all_locations()
        assert isinstance(locs, list)
        assert locs == sorted(locs)

    def test_remote_excluded(self):
        assert "Remote" not in get_all_locations()

    def test_sf_present(self):
        assert "San Francisco, CA" in get_all_locations()

    def test_no_bare_city_duplicates(self):
        locs = get_all_locations()
        assert "Bangalore" not in locs
        assert "Hyderabad" not in locs
        assert "Bangalore, India" in locs
        assert "Hyderabad, India" in locs


class TestRegistryDataIntegrity:
    def test_all_entries_have_country(self):
        for key, entry in LOCATION_REGISTRY.items():
            if key == "Remote":
                continue
            assert entry.country, f"{key} has no country"

    def test_all_entries_have_currency(self):
        for key, entry in LOCATION_REGISTRY.items():
            assert entry.currency, f"{key} has no currency"

    def test_col_index_positive(self):
        for key, entry in LOCATION_REGISTRY.items():
            assert entry.col_index > 0, f"{key} has non-positive COL index"

    def test_salary_multiplier_positive(self):
        for key, entry in LOCATION_REGISTRY.items():
            assert entry.salary_multiplier > 0, f"{key} has non-positive salary multiplier"

    def test_tax_rate_in_range(self):
        for key, entry in LOCATION_REGISTRY.items():
            assert 0.0 <= entry.tax_rate <= 1.0, f"{key} tax rate out of range: {entry.tax_rate}"


class TestDisambiguation:
    """Bare city names that exist in multiple countries resolve per documented policy."""

    def test_bare_cambridge_resolves_to_us(self):
        assert normalize_location("cambridge") == "Cambridge, MA"

    def test_cambridge_uk_explicit(self):
        assert normalize_location("Cambridge, UK") == "Cambridge, UK"


class TestMigrationAudit:
    """Verify every key from old data dicts resolves to a valid registry entry.

    These tests load the OLD dicts and assert normalize_location() maps each key
    to a canonical registry key. Run this BEFORE deleting old dicts.
    """

    def test_col_keys_covered(self):
        from utils.col_calculator import COST_OF_LIVING_DATA

        for key in COST_OF_LIVING_DATA:
            canonical = normalize_location(key)
            assert canonical in LOCATION_REGISTRY, f"COL key {key!r} -> {canonical!r} not in registry"

    def test_tax_keys_covered(self):
        from utils.tax_calculator import TAX_RATES

        for key in TAX_RATES:
            canonical = normalize_location(key)
            assert canonical in LOCATION_REGISTRY, f"Tax key {key!r} -> {canonical!r} not in registry"

    def test_currency_keys_covered(self):
        from utils.currency import LOCATION_TO_CURRENCY

        for key in LOCATION_TO_CURRENCY:
            if key == "remote":
                continue
            canonical = normalize_location(key)
            assert canonical in LOCATION_REGISTRY, f"Currency key {key!r} -> {canonical!r} not in registry"

    def test_country_keys_covered(self):
        from utils.country_data import _LOCATION_TO_COUNTRY

        for key in _LOCATION_TO_COUNTRY:
            if key in ("sf",):  # abbreviation alias, not a city entry
                continue
            canonical = normalize_location(key)
            assert canonical in LOCATION_REGISTRY, f"Country key {key!r} -> {canonical!r} not in registry"

    def test_multiplier_keys_covered(self):
        from utils.market_data import LOCATION_SALARY_MULTIPLIERS

        for key in LOCATION_SALARY_MULTIPLIERS:
            if key == "Remote":
                continue
            canonical = normalize_location(key)
            assert canonical in LOCATION_REGISTRY, f"Multiplier key {key!r} -> {canonical!r} not in registry"
