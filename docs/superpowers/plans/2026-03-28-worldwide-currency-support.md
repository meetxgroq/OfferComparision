# Worldwide Currency Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add multi-country, multi-currency support so users can compare job offers denominated in different currencies (e.g., Dubai/AED vs Bengaluru/INR), with currency conversion, international tax/COL, relocation analysis, and dual-currency UI.

**Architecture:** New utility modules (`utils/currency.py`, `utils/country_data.py`) provide static FX rates and country metadata. The backend normalizes all offer amounts to a user-chosen comparison currency before scoring. The frontend adds currency selectors, dual-currency display, and a relocation analysis section. An LLM-powered prompt extension generates cross-country relocation pros/cons when offers span multiple countries.

**Tech Stack:** Python 3.11+ / FastAPI / Pydantic (backend), Next.js 14 / TypeScript / React / Chart.js (frontend), PocketFlow nodes (orchestration).

---

## File Structure

### New Files

| File | Responsibility |
|------|---------------|
| `utils/currency.py` | Currency metadata, FX rates, conversion functions, location-to-currency inference |
| `utils/country_data.py` | Country profiles, relocation factors, country inference |
| `frontend/lib/currency.ts` | Client-side currency formatting, symbol lookup, locale-aware display |
| `tests/test_currency.py` | Tests for `utils/currency.py` |
| `tests/test_country_data.py` | Tests for `utils/country_data.py` |

### Modified Files

| File | What Changes |
|------|-------------|
| `api_server.py:44-72` | Add `currency`, `country`, `comparison_currency` fields to Pydantic models; add `/api/currencies` and `/api/countries` endpoints |
| `frontend/types/index.ts:1-32` | Add `currency`, `country` to `Offer`; add `relocation_analysis` to `AnalysisResults` |
| `nodes.py:1347-1412` | `QuickFinancialAnalysisNode` — currency-aware net pay via conversion |
| `nodes.py:1860-2027` | `_build_quick_analysis_prompt` — add relocation analysis section for cross-country |
| `utils/tax_calculator.py:8-61` | Expand `TAX_RATES` with ~30 more international cities |
| `utils/col_calculator.py:9-95,160` | Add missing international cities; add `BASELINE_EXPENSES_BY_COUNTRY` |
| `utils/scoring.py:265-269` | Currency-aware net savings scoring (normalize $100k reference) |
| `utils/market_data.py:105-144` | Add more international city multipliers |
| `frontend/components/AdvancedOfferForm.tsx` | Currency selector dropdown, dynamic `$`→symbol labels |
| `frontend/components/OfferCards.tsx` | Dual-currency display (local primary, normalized secondary) |
| `frontend/components/AnalysisResults.tsx` | Dual-currency in tables, relocation analysis section |
| `frontend/app/page.tsx` | `comparisonCurrency` state, "Compare in" dropdown, pass currency to children |

---

## Task 1: Create `utils/currency.py` — Currency Data & Conversion

**Files:**
- Create: `utils/currency.py`
- Test: `tests/test_currency.py`

- [ ] **Step 1: Write failing tests for currency data and conversion**

```python
# tests/test_currency.py
"""Tests for utils/currency.py — currency metadata, FX rates, conversion."""

import pytest
from utils.currency import (
    CURRENCY_DATA,
    FX_RATES_TO_USD,
    LOCATION_TO_CURRENCY,
    convert_to_usd,
    convert_from_usd,
    get_fx_rate,
    infer_currency,
    get_all_currencies,
)


class TestCurrencyData:
    def test_currency_data_has_required_keys(self):
        for code, meta in CURRENCY_DATA.items():
            assert "symbol" in meta, f"{code} missing symbol"
            assert "name" in meta, f"{code} missing name"
            assert "locale" in meta, f"{code} missing locale"

    def test_usd_in_currency_data(self):
        assert "USD" in CURRENCY_DATA
        assert CURRENCY_DATA["USD"]["symbol"] == "$"

    def test_inr_in_currency_data(self):
        assert "INR" in CURRENCY_DATA
        assert CURRENCY_DATA["INR"]["symbol"] == "₹"

    def test_fx_rates_has_all_non_usd_currencies(self):
        for code in CURRENCY_DATA:
            if code != "USD":
                assert code in FX_RATES_TO_USD, f"{code} missing FX rate"

    def test_usd_not_in_fx_rates(self):
        assert "USD" not in FX_RATES_TO_USD


class TestConversion:
    def test_convert_usd_to_usd(self):
        assert convert_to_usd(100, "USD") == 100.0

    def test_convert_inr_to_usd(self):
        result = convert_to_usd(100_000, "INR")
        assert isinstance(result, float)
        assert result > 0
        assert result < 100_000  # INR is worth less than USD

    def test_convert_from_usd_to_inr(self):
        result = convert_from_usd(1000, "INR")
        assert result > 1000  # More INR than USD

    def test_round_trip_conversion(self):
        original = 50_000.0
        usd = convert_to_usd(original, "GBP")
        back = convert_from_usd(usd, "GBP")
        assert abs(back - original) < 0.01

    def test_get_fx_rate_same_currency(self):
        assert get_fx_rate("USD", "USD") == 1.0

    def test_get_fx_rate_cross(self):
        rate = get_fx_rate("INR", "GBP")
        assert isinstance(rate, float)
        assert rate > 0

    def test_convert_unknown_currency_raises(self):
        with pytest.raises(KeyError):
            convert_to_usd(100, "ZZZ")


class TestInferCurrency:
    def test_infer_bangalore(self):
        assert infer_currency("Bangalore, India") == "INR"

    def test_infer_dubai(self):
        assert infer_currency("Dubai, UAE") == "AED"

    def test_infer_san_francisco(self):
        assert infer_currency("San Francisco, CA") == "USD"

    def test_infer_london(self):
        assert infer_currency("London, UK") == "GBP"

    def test_infer_unknown_defaults_usd(self):
        assert infer_currency("Atlantis, Underwater") == "USD"

    def test_infer_remote_defaults_usd(self):
        assert infer_currency("Remote") == "USD"

    def test_infer_case_insensitive(self):
        assert infer_currency("bangalore, india") == "INR"


class TestGetAllCurrencies:
    def test_returns_list_of_dicts(self):
        result = get_all_currencies()
        assert isinstance(result, list)
        assert len(result) > 0
        first = result[0]
        assert "code" in first
        assert "symbol" in first
        assert "name" in first
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_currency.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'utils.currency'`

- [ ] **Step 3: Implement `utils/currency.py`**

```python
# utils/currency.py
"""
Currency metadata, FX rates (static baseline), and conversion utilities.

Covers ~20 currencies for major global tech hubs. Rates are static baselines
that can be optionally refreshed via fetch_live_rates().
"""

CURRENCY_DATA = {
    "USD": {"symbol": "$", "name": "US Dollar", "locale": "en-US"},
    "INR": {"symbol": "₹", "name": "Indian Rupee", "locale": "en-IN"},
    "AED": {"symbol": "د.إ", "name": "UAE Dirham", "locale": "ar-AE"},
    "GBP": {"symbol": "£", "name": "British Pound", "locale": "en-GB"},
    "EUR": {"symbol": "€", "name": "Euro", "locale": "de-DE"},
    "SGD": {"symbol": "S$", "name": "Singapore Dollar", "locale": "en-SG"},
    "CAD": {"symbol": "C$", "name": "Canadian Dollar", "locale": "en-CA"},
    "AUD": {"symbol": "A$", "name": "Australian Dollar", "locale": "en-AU"},
    "JPY": {"symbol": "¥", "name": "Japanese Yen", "locale": "ja-JP"},
    "CHF": {"symbol": "CHF", "name": "Swiss Franc", "locale": "de-CH"},
    "SEK": {"symbol": "kr", "name": "Swedish Krona", "locale": "sv-SE"},
    "NOK": {"symbol": "kr", "name": "Norwegian Krone", "locale": "nb-NO"},
    "DKK": {"symbol": "kr", "name": "Danish Krone", "locale": "da-DK"},
    "PLN": {"symbol": "zł", "name": "Polish Zloty", "locale": "pl-PL"},
    "CZK": {"symbol": "Kč", "name": "Czech Koruna", "locale": "cs-CZ"},
    "ILS": {"symbol": "₪", "name": "Israeli Shekel", "locale": "he-IL"},
    "KRW": {"symbol": "₩", "name": "South Korean Won", "locale": "ko-KR"},
    "TWD": {"symbol": "NT$", "name": "New Taiwan Dollar", "locale": "zh-TW"},
    "CNY": {"symbol": "¥", "name": "Chinese Yuan", "locale": "zh-CN"},
    "BRL": {"symbol": "R$", "name": "Brazilian Real", "locale": "pt-BR"},
    "MXN": {"symbol": "$", "name": "Mexican Peso", "locale": "es-MX"},
    "SAR": {"symbol": "﷼", "name": "Saudi Riyal", "locale": "ar-SA"},
    "QAR": {"symbol": "﷼", "name": "Qatari Riyal", "locale": "ar-QA"},
    "THB": {"symbol": "฿", "name": "Thai Baht", "locale": "th-TH"},
    "VND": {"symbol": "₫", "name": "Vietnamese Dong", "locale": "vi-VN"},
    "IDR": {"symbol": "Rp", "name": "Indonesian Rupiah", "locale": "id-ID"},
    "MYR": {"symbol": "RM", "name": "Malaysian Ringgit", "locale": "ms-MY"},
    "PHP": {"symbol": "₱", "name": "Philippine Peso", "locale": "fil-PH"},
    "NZD": {"symbol": "NZ$", "name": "New Zealand Dollar", "locale": "en-NZ"},
    "HKD": {"symbol": "HK$", "name": "Hong Kong Dollar", "locale": "zh-HK"},
}

# Static baseline FX rates: 1 unit of currency → USD
# Source: approximate mid-market rates as of early 2026
FX_RATES_TO_USD = {
    "INR": 0.012,
    "AED": 0.272,
    "GBP": 1.27,
    "EUR": 1.08,
    "SGD": 0.74,
    "CAD": 0.74,
    "AUD": 0.65,
    "JPY": 0.0067,
    "CHF": 1.12,
    "SEK": 0.096,
    "NOK": 0.094,
    "DKK": 0.145,
    "PLN": 0.25,
    "CZK": 0.043,
    "ILS": 0.28,
    "KRW": 0.00075,
    "TWD": 0.031,
    "CNY": 0.14,
    "BRL": 0.19,
    "MXN": 0.058,
    "SAR": 0.267,
    "QAR": 0.275,
    "THB": 0.029,
    "VND": 0.00004,
    "IDR": 0.000063,
    "MYR": 0.22,
    "PHP": 0.018,
    "NZD": 0.61,
    "HKD": 0.128,
}

LOCATION_TO_CURRENCY = {
    # United States
    "San Francisco, CA": "USD", "San Jose, CA": "USD", "Los Angeles, CA": "USD",
    "New York, NY": "USD", "Seattle, WA": "USD", "Austin, TX": "USD",
    "Boston, MA": "USD", "Chicago, IL": "USD", "Denver, CO": "USD",
    "Atlanta, GA": "USD", "Miami, FL": "USD", "Washington, DC": "USD",
    "San Diego, CA": "USD", "Portland, OR": "USD", "Dallas, TX": "USD",
    "Houston, TX": "USD", "Phoenix, AZ": "USD", "Minneapolis, MN": "USD",
    "Philadelphia, PA": "USD", "Raleigh, NC": "USD", "Pittsburgh, PA": "USD",
    # India
    "Bangalore, India": "INR", "Bengaluru, India": "INR",
    "Mumbai, India": "INR", "Hyderabad, India": "INR",
    "Delhi, India": "INR", "New Delhi, India": "INR",
    "Pune, India": "INR", "Chennai, India": "INR",
    "Gurgaon, India": "INR", "Noida, India": "INR",
    # UAE
    "Dubai, UAE": "AED", "Abu Dhabi, UAE": "AED",
    # UK
    "London, UK": "GBP", "Edinburgh, UK": "GBP", "Manchester, UK": "GBP",
    "Cambridge, UK": "GBP", "Bristol, UK": "GBP",
    # Europe
    "Berlin, Germany": "EUR", "Munich, Germany": "EUR", "Frankfurt, Germany": "EUR",
    "Amsterdam, Netherlands": "EUR", "Dublin, Ireland": "EUR",
    "Paris, France": "EUR", "Barcelona, Spain": "EUR", "Madrid, Spain": "EUR",
    "Lisbon, Portugal": "EUR", "Milan, Italy": "EUR", "Helsinki, Finland": "EUR",
    "Stockholm, Sweden": "SEK", "Oslo, Norway": "NOK", "Copenhagen, Denmark": "DKK",
    "Warsaw, Poland": "PLN", "Prague, Czech Republic": "CZK",
    "Zurich, Switzerland": "CHF", "Geneva, Switzerland": "CHF",
    # Asia-Pacific
    "Singapore": "SGD", "Tokyo, Japan": "JPY", "Seoul, South Korea": "KRW",
    "Taipei, Taiwan": "TWD", "Shanghai, China": "CNY", "Beijing, China": "CNY",
    "Shenzhen, China": "CNY", "Hong Kong": "HKD",
    "Sydney, Australia": "AUD", "Melbourne, Australia": "AUD",
    "Auckland, New Zealand": "NZD",
    "Jakarta, Indonesia": "IDR", "Bangkok, Thailand": "THB",
    "Ho Chi Minh City, Vietnam": "VND", "Kuala Lumpur, Malaysia": "MYR",
    "Manila, Philippines": "PHP",
    # Middle East
    "Riyadh, Saudi Arabia": "SAR", "Doha, Qatar": "QAR",
    "Tel Aviv, Israel": "ILS",
    # Americas
    "Toronto, Canada": "CAD", "Vancouver, Canada": "CAD",
    "Montreal, Canada": "CAD",
    "São Paulo, Brazil": "BRL", "Mexico City, Mexico": "MXN",
}

# Country suffix → currency fallback for locations not in the map
_COUNTRY_SUFFIX_TO_CURRENCY = {
    "US": "USD", "USA": "USD", "United States": "USD",
    "India": "INR",
    "UAE": "AED", "United Arab Emirates": "AED",
    "UK": "GBP", "United Kingdom": "GBP", "England": "GBP",
    "Germany": "EUR", "France": "EUR", "Netherlands": "EUR",
    "Ireland": "EUR", "Spain": "EUR", "Portugal": "EUR",
    "Italy": "EUR", "Finland": "EUR", "Austria": "EUR",
    "Belgium": "EUR", "Greece": "EUR",
    "Sweden": "SEK", "Norway": "NOK", "Denmark": "DKK",
    "Poland": "PLN", "Czech Republic": "CZK",
    "Switzerland": "CHF",
    "Singapore": "SGD", "Japan": "JPY",
    "South Korea": "KRW", "Korea": "KRW",
    "Taiwan": "TWD", "China": "CNY",
    "Australia": "AUD", "New Zealand": "NZD",
    "Canada": "CAD",
    "Brazil": "BRL", "Mexico": "MXN",
    "Saudi Arabia": "SAR", "Qatar": "QAR",
    "Israel": "ILS",
    "Indonesia": "IDR", "Thailand": "THB",
    "Vietnam": "VND", "Malaysia": "MYR",
    "Philippines": "PHP", "Hong Kong": "HKD",
}


def convert_to_usd(amount: float, from_currency: str) -> float:
    """Convert an amount in `from_currency` to USD."""
    if from_currency == "USD":
        return float(amount)
    rate = FX_RATES_TO_USD[from_currency]  # KeyError if unknown
    return round(amount * rate, 2)


def convert_from_usd(amount: float, to_currency: str) -> float:
    """Convert a USD amount to `to_currency`."""
    if to_currency == "USD":
        return float(amount)
    rate = FX_RATES_TO_USD[to_currency]
    return round(amount / rate, 2)


def get_fx_rate(from_currency: str, to_currency: str) -> float:
    """Get the exchange rate from `from_currency` to `to_currency` (via USD pivot)."""
    if from_currency == to_currency:
        return 1.0
    usd_per_from = FX_RATES_TO_USD.get(from_currency, 1.0) if from_currency != "USD" else 1.0
    usd_per_to = FX_RATES_TO_USD.get(to_currency, 1.0) if to_currency != "USD" else 1.0
    return round(usd_per_from / usd_per_to, 6)


def infer_currency(location: str) -> str:
    """Infer the ISO currency code for a location string. Defaults to USD."""
    if not location or location.lower() == "remote":
        return "USD"

    loc_lower = location.lower().strip()

    for known_loc, code in LOCATION_TO_CURRENCY.items():
        if known_loc.lower() == loc_lower:
            return code

    # Fallback: check country suffix
    parts = [p.strip() for p in location.split(",")]
    if len(parts) >= 2:
        country_part = parts[-1]
        for suffix, code in _COUNTRY_SUFFIX_TO_CURRENCY.items():
            if suffix.lower() == country_part.lower():
                return code

    return "USD"


def get_all_currencies() -> list[dict]:
    """Return a list of currency info dicts for the /api/currencies endpoint."""
    result = []
    for code, meta in sorted(CURRENCY_DATA.items()):
        entry = {"code": code, "symbol": meta["symbol"], "name": meta["name"]}
        if code != "USD":
            entry["rate_to_usd"] = FX_RATES_TO_USD.get(code)
        else:
            entry["rate_to_usd"] = 1.0
        result.append(entry)
    return result


if __name__ == "__main__":
    print("=== Currency Module Smoke Test ===")
    print(f"Currencies: {len(CURRENCY_DATA)}")
    print(f"FX rates: {len(FX_RATES_TO_USD)}")
    print(f"Location mappings: {len(LOCATION_TO_CURRENCY)}")
    print(f"₹50,00,000 INR = ${convert_to_usd(5_000_000, 'INR'):,.2f} USD")
    print(f"$100,000 USD = ₹{convert_from_usd(100_000, 'INR'):,.2f} INR")
    print(f"INR→GBP rate: {get_fx_rate('INR', 'GBP')}")
    print(f"Infer 'Bangalore, India': {infer_currency('Bangalore, India')}")
    print(f"Infer 'Remote': {infer_currency('Remote')}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_currency.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add utils/currency.py tests/test_currency.py
git commit -m "feat: add currency utility with FX rates, conversion, and location inference"
```

---

## Task 2: Create `utils/country_data.py` — Country Profiles & Relocation

**Files:**
- Create: `utils/country_data.py`
- Test: `tests/test_country_data.py`

- [ ] **Step 1: Write failing tests for country data**

```python
# tests/test_country_data.py
"""Tests for utils/country_data.py — country profiles and relocation factors."""

import pytest
from utils.country_data import (
    COUNTRY_PROFILES,
    infer_country,
    get_relocation_factors,
    get_all_countries,
)


class TestCountryProfiles:
    def test_profiles_has_india(self):
        assert "India" in COUNTRY_PROFILES

    def test_profiles_has_uae(self):
        assert "UAE" in COUNTRY_PROFILES

    def test_profiles_has_us(self):
        assert "United States" in COUNTRY_PROFILES

    def test_profile_required_keys(self):
        required = {"currency", "tax_regime", "max_marginal_rate", "major_tech_hubs"}
        for country, profile in COUNTRY_PROFILES.items():
            for key in required:
                assert key in profile, f"{country} missing '{key}'"


class TestInferCountry:
    def test_infer_bangalore(self):
        assert infer_country("Bangalore, India") == "India"

    def test_infer_sf(self):
        assert infer_country("San Francisco, CA") == "United States"

    def test_infer_dubai(self):
        assert infer_country("Dubai, UAE") == "UAE"

    def test_infer_london(self):
        assert infer_country("London, UK") == "United Kingdom"

    def test_infer_unknown_returns_none(self):
        assert infer_country("Atlantis, Underwater") is None

    def test_infer_remote_returns_none(self):
        assert infer_country("Remote") is None


class TestRelocationFactors:
    def test_same_country_returns_none(self):
        result = get_relocation_factors("India", "India")
        assert result is None

    def test_cross_country_has_keys(self):
        result = get_relocation_factors("United States", "India")
        assert result is not None
        assert "visa_notes" in result
        assert "tax_delta_description" in result
        assert "from_country" in result
        assert "to_country" in result

    def test_unknown_country_returns_none(self):
        result = get_relocation_factors("Narnia", "India")
        assert result is None


class TestGetAllCountries:
    def test_returns_list(self):
        result = get_all_countries()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_entry_has_name_and_currency(self):
        result = get_all_countries()
        for entry in result:
            assert "name" in entry
            assert "currency" in entry
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_country_data.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement `utils/country_data.py`**

```python
# utils/country_data.py
"""
Country profiles for relocation analysis and international offer comparison.
"""

COUNTRY_PROFILES = {
    "United States": {
        "currency": "USD",
        "tax_regime": "progressive federal + state",
        "max_marginal_rate": 0.37,
        "social_security": "Social Security + Medicare (FICA 7.65%)",
        "healthcare": "employer-sponsored typical",
        "visa_for_work": "H-1B / L-1 / O-1 required for non-citizens",
        "retirement_system": "401(k) + Social Security",
        "quality_of_life_index": 70,
        "safety_index": 55,
        "major_tech_hubs": [
            "San Francisco", "San Jose", "Seattle", "New York",
            "Austin", "Boston", "Los Angeles",
        ],
        "typical_benefits": ["401(k) match", "Health/dental/vision", "Stock options/RSUs", "PTO"],
        "considerations": [
            "High healthcare costs without employer coverage",
            "At-will employment in most states",
            "Wide variation in COL across cities",
        ],
    },
    "India": {
        "currency": "INR",
        "tax_regime": "progressive",
        "max_marginal_rate": 0.312,
        "social_security": "EPF/EPS mandatory (12% employee + 12% employer)",
        "healthcare": "private recommended",
        "visa_for_work": "Employment visa required for non-citizens",
        "retirement_system": "EPF + NPS (voluntary)",
        "quality_of_life_index": 55,
        "safety_index": 45,
        "major_tech_hubs": ["Bangalore", "Hyderabad", "Pune", "Mumbai", "Delhi/NCR", "Chennai"],
        "typical_benefits": ["Gratuity", "PF matching", "Medical insurance", "Meal coupons"],
        "considerations": [
            "Traffic/commute in metros",
            "Air quality concerns in some cities",
            "Strong and growing tech community",
            "Lower absolute salary but high purchasing power",
        ],
    },
    "UAE": {
        "currency": "AED",
        "tax_regime": "no income tax",
        "max_marginal_rate": 0.0,
        "social_security": "GPSSA for UAE nationals; none for expats",
        "healthcare": "employer-provided mandatory",
        "visa_for_work": "Employment/residence visa (employer-sponsored)",
        "retirement_system": "End-of-service gratuity",
        "quality_of_life_index": 72,
        "safety_index": 85,
        "major_tech_hubs": ["Dubai", "Abu Dhabi"],
        "typical_benefits": ["Housing allowance", "Annual flight home", "Medical insurance", "Education allowance"],
        "considerations": [
            "No income tax — significant savings advantage",
            "Hot climate much of the year",
            "Expat-friendly but cultural adjustment needed",
            "Gratuity paid at end of service",
        ],
    },
    "United Kingdom": {
        "currency": "GBP",
        "tax_regime": "progressive",
        "max_marginal_rate": 0.45,
        "social_security": "National Insurance (13.25% up to threshold)",
        "healthcare": "NHS (public, free at point of use)",
        "visa_for_work": "Skilled Worker visa required for non-citizens",
        "retirement_system": "State Pension + workplace pensions (auto-enrolment)",
        "quality_of_life_index": 68,
        "safety_index": 65,
        "major_tech_hubs": ["London", "Cambridge", "Edinburgh", "Manchester", "Bristol"],
        "typical_benefits": ["25+ days PTO", "Pension matching", "Private health (supplemental)", "Cycle-to-work"],
        "considerations": [
            "High COL in London",
            "Strong worker protections",
            "Free public healthcare via NHS",
            "Significant tech ecosystem in London/Cambridge",
        ],
    },
    "Germany": {
        "currency": "EUR",
        "tax_regime": "progressive",
        "max_marginal_rate": 0.45,
        "social_security": "~20% employee contribution (health, pension, unemployment, care)",
        "healthcare": "statutory health insurance (public, high quality)",
        "visa_for_work": "EU Blue Card / work visa for non-EU citizens",
        "retirement_system": "State pension + company pension (Betriebsrente)",
        "quality_of_life_index": 73,
        "safety_index": 72,
        "major_tech_hubs": ["Berlin", "Munich", "Frankfurt", "Hamburg"],
        "typical_benefits": ["30 days PTO", "13th month salary (some)", "Public transport subsidy", "Pension contribution"],
        "considerations": [
            "High social security deductions",
            "Excellent public infrastructure",
            "Strong worker protections and works councils",
            "Berlin is affordable; Munich is expensive",
        ],
    },
    "Singapore": {
        "currency": "SGD",
        "tax_regime": "progressive (low rates)",
        "max_marginal_rate": 0.22,
        "social_security": "CPF (20% employee + 17% employer for citizens/PRs)",
        "healthcare": "MediShield Life + employer coverage",
        "visa_for_work": "Employment Pass (EP) for professionals",
        "retirement_system": "CPF (mandatory savings)",
        "quality_of_life_index": 80,
        "safety_index": 90,
        "major_tech_hubs": ["Singapore"],
        "typical_benefits": ["AWS (13th month)", "Health insurance", "Transport allowance"],
        "considerations": [
            "Very low taxes",
            "High COL especially housing",
            "Excellent infrastructure and safety",
            "Gateway to Southeast Asia tech market",
        ],
    },
    "Canada": {
        "currency": "CAD",
        "tax_regime": "progressive federal + provincial",
        "max_marginal_rate": 0.33,
        "social_security": "CPP + EI contributions",
        "healthcare": "public universal healthcare (provincial)",
        "visa_for_work": "Work permit / Express Entry PR pathway",
        "retirement_system": "CPP + OAS + RRSP",
        "quality_of_life_index": 75,
        "safety_index": 78,
        "major_tech_hubs": ["Toronto", "Vancouver", "Montreal", "Ottawa"],
        "typical_benefits": ["Health benefits (dental/vision)", "RRSP matching", "Generous PTO"],
        "considerations": [
            "Universal healthcare",
            "Clear PR pathway via Express Entry",
            "Toronto/Vancouver are expensive",
            "Growing tech ecosystem",
        ],
    },
    "Australia": {
        "currency": "AUD",
        "tax_regime": "progressive",
        "max_marginal_rate": 0.45,
        "social_security": "Superannuation (11.5% employer mandatory)",
        "healthcare": "Medicare (public) + private option",
        "visa_for_work": "Skilled Worker visa (subclass 482/494)",
        "retirement_system": "Superannuation + Age Pension",
        "quality_of_life_index": 76,
        "safety_index": 80,
        "major_tech_hubs": ["Sydney", "Melbourne"],
        "typical_benefits": ["11.5% super", "4 weeks annual leave (mandated)", "Long service leave"],
        "considerations": [
            "Mandatory super is a major benefit",
            "4 weeks minimum PTO by law",
            "High COL in Sydney/Melbourne",
            "Great lifestyle and climate",
        ],
    },
    "Japan": {
        "currency": "JPY",
        "tax_regime": "progressive national + local",
        "max_marginal_rate": 0.45,
        "social_security": "~15% employee (health + pension + employment insurance)",
        "healthcare": "National Health Insurance (universal)",
        "visa_for_work": "Engineer/Specialist visa or Highly Skilled Professional visa",
        "retirement_system": "Employees' Pension + National Pension",
        "quality_of_life_index": 74,
        "safety_index": 88,
        "major_tech_hubs": ["Tokyo"],
        "typical_benefits": ["Commuter allowance", "Biannual bonuses", "Health insurance"],
        "considerations": [
            "Very safe and clean cities",
            "Language barrier in many workplaces",
            "High social security contributions",
            "Culture of long work hours (improving)",
        ],
    },
    "Netherlands": {
        "currency": "EUR",
        "tax_regime": "progressive (30% ruling for expats)",
        "max_marginal_rate": 0.495,
        "social_security": "~27% social contributions (partially by employer)",
        "healthcare": "mandatory private health insurance",
        "visa_for_work": "Highly Skilled Migrant visa",
        "retirement_system": "State pension (AOW) + occupational pension",
        "quality_of_life_index": 77,
        "safety_index": 75,
        "major_tech_hubs": ["Amsterdam"],
        "typical_benefits": ["30% ruling tax benefit for expats", "25 days PTO", "Pension", "OV-chipkaart"],
        "considerations": [
            "30% ruling makes first 5 years very tax-efficient",
            "Excellent English proficiency",
            "High housing costs in Amsterdam",
            "Great work-life balance culture",
        ],
    },
    "Switzerland": {
        "currency": "CHF",
        "tax_regime": "progressive (federal + cantonal + municipal)",
        "max_marginal_rate": 0.40,
        "social_security": "AHV/IV (~5.3% employee) + pension fund",
        "healthcare": "mandatory private insurance",
        "visa_for_work": "L/B permit (quotas apply for non-EU)",
        "retirement_system": "Three-pillar system (state + occupational + private)",
        "quality_of_life_index": 83,
        "safety_index": 88,
        "major_tech_hubs": ["Zurich", "Geneva"],
        "typical_benefits": ["High base salaries", "Pension contribution", "Transport subsidy"],
        "considerations": [
            "Highest salaries in Europe",
            "Extremely high COL",
            "Excellent infrastructure and quality of life",
            "Strict work permit quotas for non-EU/EFTA",
        ],
    },
    "Ireland": {
        "currency": "EUR",
        "tax_regime": "progressive",
        "max_marginal_rate": 0.40,
        "social_security": "PRSI (~4% employee)",
        "healthcare": "public + private",
        "visa_for_work": "Critical Skills Employment Permit",
        "retirement_system": "State pension + occupational",
        "quality_of_life_index": 72,
        "safety_index": 75,
        "major_tech_hubs": ["Dublin"],
        "typical_benefits": ["Health insurance", "Pension contribution", "20+ days PTO"],
        "considerations": [
            "Major European tech hub (Google, Meta, Apple HQs)",
            "English-speaking",
            "Dublin housing is expensive and limited",
            "Low corporate tax attracts MNCs",
        ],
    },
    "South Korea": {
        "currency": "KRW",
        "tax_regime": "progressive",
        "max_marginal_rate": 0.45,
        "social_security": "~9% employee (NP + NHI + EI + LTC)",
        "healthcare": "National Health Insurance (universal)",
        "visa_for_work": "E-7 visa (professional) or F-2 points-based",
        "retirement_system": "National Pension + severance pay",
        "quality_of_life_index": 70,
        "safety_index": 82,
        "major_tech_hubs": ["Seoul"],
        "typical_benefits": ["Severance (1 month/year)", "Health insurance", "Meal allowance"],
        "considerations": [
            "Major tech ecosystem (Samsung, LG, Kakao, Naver)",
            "High housing costs in Seoul",
            "Korean language often needed",
            "Intense work culture (improving)",
        ],
    },
    "Saudi Arabia": {
        "currency": "SAR",
        "tax_regime": "no income tax",
        "max_marginal_rate": 0.0,
        "social_security": "GOSI (2% employee for nationals)",
        "healthcare": "employer-provided mandatory for expats",
        "visa_for_work": "Employment visa (employer-sponsored)",
        "retirement_system": "End-of-service gratuity",
        "quality_of_life_index": 60,
        "safety_index": 70,
        "major_tech_hubs": ["Riyadh"],
        "typical_benefits": ["Housing allowance", "Transport allowance", "Annual flight home"],
        "considerations": [
            "No income tax",
            "Vision 2030 tech investment",
            "Cultural adjustment required",
            "Hot climate",
        ],
    },
    "Qatar": {
        "currency": "QAR",
        "tax_regime": "no income tax",
        "max_marginal_rate": 0.0,
        "social_security": "none for expats",
        "healthcare": "employer-provided mandatory",
        "visa_for_work": "Employment visa",
        "retirement_system": "End-of-service gratuity",
        "quality_of_life_index": 65,
        "safety_index": 80,
        "major_tech_hubs": ["Doha"],
        "typical_benefits": ["Housing allowance", "Annual flight", "Medical insurance"],
        "considerations": [
            "No income tax",
            "High expat population",
            "Small but growing tech scene",
            "Very hot summers",
        ],
    },
    "Israel": {
        "currency": "ILS",
        "tax_regime": "progressive",
        "max_marginal_rate": 0.50,
        "social_security": "Bituach Leumi (~3.5% employee up to threshold)",
        "healthcare": "universal public healthcare",
        "visa_for_work": "B-1 work visa",
        "retirement_system": "Mandatory pension (employer + employee contributions)",
        "quality_of_life_index": 68,
        "safety_index": 50,
        "major_tech_hubs": ["Tel Aviv"],
        "typical_benefits": ["Pension (mandatory)", "Study fund", "Health insurance top-up", "13th salary (some)"],
        "considerations": [
            "Startup Nation — vibrant tech ecosystem",
            "High COL in Tel Aviv",
            "Mandatory military reserve duty for citizens",
            "Security situation can be a factor",
        ],
    },
    "France": {
        "currency": "EUR",
        "tax_regime": "progressive",
        "max_marginal_rate": 0.45,
        "social_security": "~22% employee contributions",
        "healthcare": "universal public healthcare (Sécurité Sociale)",
        "visa_for_work": "Talent Passport or work permit",
        "retirement_system": "State pension + supplementary",
        "quality_of_life_index": 72,
        "safety_index": 60,
        "major_tech_hubs": ["Paris"],
        "typical_benefits": ["35-hour workweek", "5 weeks PTO (minimum)", "Health coverage", "Restaurant vouchers"],
        "considerations": [
            "Strong worker protections",
            "35-hour workweek is standard",
            "High social charges reduce take-home",
            "Paris has a strong startup ecosystem (Station F)",
        ],
    },
    "Spain": {
        "currency": "EUR",
        "tax_regime": "progressive",
        "max_marginal_rate": 0.47,
        "social_security": "~6.35% employee",
        "healthcare": "universal public healthcare",
        "visa_for_work": "Digital nomad visa or work permit",
        "retirement_system": "State pension",
        "quality_of_life_index": 73,
        "safety_index": 68,
        "major_tech_hubs": ["Barcelona", "Madrid"],
        "typical_benefits": ["22+ days PTO", "Health insurance", "Meal vouchers"],
        "considerations": [
            "Excellent quality of life and climate",
            "Lower salaries than Northern Europe",
            "Growing tech scene in Barcelona",
            "Digital nomad visa available",
        ],
    },
    "Sweden": {
        "currency": "SEK",
        "tax_regime": "progressive (municipal + state)",
        "max_marginal_rate": 0.52,
        "social_security": "~7% employee",
        "healthcare": "universal public healthcare",
        "visa_for_work": "Work permit",
        "retirement_system": "State pension + occupational + private",
        "quality_of_life_index": 78,
        "safety_index": 72,
        "major_tech_hubs": ["Stockholm"],
        "typical_benefits": ["25 days PTO", "Parental leave (480 days shared)", "Friskvårdsbidrag (wellness)"],
        "considerations": [
            "Very high taxes but excellent public services",
            "Stockholm is a startup hub (Spotify, Klarna)",
            "Dark winters, great summers",
            "Generous parental leave",
        ],
    },
    "Norway": {
        "currency": "NOK",
        "tax_regime": "progressive",
        "max_marginal_rate": 0.47,
        "social_security": "~7.8% employee",
        "healthcare": "universal public healthcare",
        "visa_for_work": "Skilled worker visa",
        "retirement_system": "State pension + AFP",
        "quality_of_life_index": 80,
        "safety_index": 85,
        "major_tech_hubs": ["Oslo"],
        "typical_benefits": ["25 days PTO", "Generous parental leave", "Pension"],
        "considerations": [
            "Very high COL",
            "Excellent quality of life",
            "Oil-fund-backed economy",
            "Limited tech job market compared to larger hubs",
        ],
    },
    "Denmark": {
        "currency": "DKK",
        "tax_regime": "progressive",
        "max_marginal_rate": 0.52,
        "social_security": "~8% employee (AM-bidrag)",
        "healthcare": "universal public healthcare",
        "visa_for_work": "Pay Limit Scheme or Positive List",
        "retirement_system": "State pension + ATP + occupational",
        "quality_of_life_index": 79,
        "safety_index": 82,
        "major_tech_hubs": ["Copenhagen"],
        "typical_benefits": ["25 days PTO", "Parental leave", "Pension contributions"],
        "considerations": [
            "High taxes, high quality of life",
            "Flexicurity labor model",
            "Growing tech scene in Copenhagen",
            "Cycling-friendly city infrastructure",
        ],
    },
    "Portugal": {
        "currency": "EUR",
        "tax_regime": "progressive (NHR tax regime for newcomers)",
        "max_marginal_rate": 0.48,
        "social_security": "~11% employee",
        "healthcare": "universal public healthcare (SNS)",
        "visa_for_work": "Tech Visa or D7 visa",
        "retirement_system": "State pension",
        "quality_of_life_index": 70,
        "safety_index": 78,
        "major_tech_hubs": ["Lisbon"],
        "typical_benefits": ["22 days PTO", "Health insurance", "Meal allowance"],
        "considerations": [
            "NHR tax regime: 20% flat for 10 years (qualified professionals)",
            "Growing tech hub (Web Summit city)",
            "Lower COL than Western Europe",
            "Excellent climate and quality of life",
        ],
    },
    "New Zealand": {
        "currency": "NZD",
        "tax_regime": "progressive",
        "max_marginal_rate": 0.39,
        "social_security": "ACC levy (~1.6%)",
        "healthcare": "public healthcare system",
        "visa_for_work": "Accredited Employer Work Visa",
        "retirement_system": "KiwiSaver (3%+ employee + 3% employer)",
        "quality_of_life_index": 76,
        "safety_index": 82,
        "major_tech_hubs": ["Auckland"],
        "typical_benefits": ["4 weeks annual leave (mandated)", "KiwiSaver match", "Public holidays"],
        "considerations": [
            "Excellent quality of life",
            "Small but growing tech scene",
            "Remote location (travel costs)",
            "4 weeks minimum PTO by law",
        ],
    },
}

# Location → Country mapping (city-level specificity)
_LOCATION_TO_COUNTRY = {
    "San Francisco, CA": "United States", "San Jose, CA": "United States",
    "Seattle, WA": "United States", "New York, NY": "United States",
    "Austin, TX": "United States", "Boston, MA": "United States",
    "Los Angeles, CA": "United States", "Chicago, IL": "United States",
    "Denver, CO": "United States", "Atlanta, GA": "United States",
    "Miami, FL": "United States", "Washington, DC": "United States",
    "San Diego, CA": "United States", "Portland, OR": "United States",
    "Dallas, TX": "United States", "Houston, TX": "United States",
    "Phoenix, AZ": "United States", "Minneapolis, MN": "United States",
    "Philadelphia, PA": "United States", "Raleigh, NC": "United States",
    "Pittsburgh, PA": "United States",
    "Bangalore, India": "India", "Bengaluru, India": "India",
    "Mumbai, India": "India", "Hyderabad, India": "India",
    "Delhi, India": "India", "New Delhi, India": "India",
    "Pune, India": "India", "Chennai, India": "India",
    "Gurgaon, India": "India", "Noida, India": "India",
    "Dubai, UAE": "UAE", "Abu Dhabi, UAE": "UAE",
    "London, UK": "United Kingdom", "Edinburgh, UK": "United Kingdom",
    "Manchester, UK": "United Kingdom", "Cambridge, UK": "United Kingdom",
    "Bristol, UK": "United Kingdom",
    "Berlin, Germany": "Germany", "Munich, Germany": "Germany",
    "Frankfurt, Germany": "Germany",
    "Amsterdam, Netherlands": "Netherlands",
    "Dublin, Ireland": "Ireland",
    "Paris, France": "France",
    "Barcelona, Spain": "Spain",
    "Madrid, Spain": "Spain",
    "Stockholm, Sweden": "Sweden",
    "Oslo, Norway": "Norway",
    "Copenhagen, Denmark": "Denmark",
    "Zurich, Switzerland": "Switzerland", "Geneva, Switzerland": "Switzerland",
    "Singapore": "Singapore",
    "Tokyo, Japan": "Japan",
    "Seoul, South Korea": "South Korea",
    "Sydney, Australia": "Australia", "Melbourne, Australia": "Australia",
    "Toronto, Canada": "Canada", "Vancouver, Canada": "Canada",
    "Montreal, Canada": "Canada",
    "Riyadh, Saudi Arabia": "Saudi Arabia",
    "Doha, Qatar": "Qatar",
    "Tel Aviv, Israel": "Israel",
}

_COUNTRY_SUFFIX_TO_COUNTRY = {
    "US": "United States", "USA": "United States",
    "United States": "United States", "CA": "United States",
    "TX": "United States", "WA": "United States", "NY": "United States",
    "MA": "United States", "IL": "United States", "CO": "United States",
    "GA": "United States", "FL": "United States", "DC": "United States",
    "OR": "United States", "AZ": "United States", "MN": "United States",
    "PA": "United States", "NC": "United States",
    "India": "India",
    "UAE": "UAE", "United Arab Emirates": "UAE",
    "UK": "United Kingdom", "United Kingdom": "United Kingdom",
    "England": "United Kingdom",
    "Germany": "Germany", "France": "France",
    "Netherlands": "Netherlands", "Ireland": "Ireland",
    "Spain": "Spain", "Portugal": "Portugal",
    "Sweden": "Sweden", "Norway": "Norway", "Denmark": "Denmark",
    "Switzerland": "Switzerland",
    "Singapore": "Singapore", "Japan": "Japan",
    "South Korea": "South Korea", "Korea": "South Korea",
    "Australia": "Australia", "New Zealand": "New Zealand",
    "Canada": "Canada",
    "Saudi Arabia": "Saudi Arabia", "Qatar": "Qatar",
    "Israel": "Israel",
}


def infer_country(location: str) -> str | None:
    """Infer country name from a location string. Returns None if unknown."""
    if not location or location.lower() == "remote":
        return None

    loc_lower = location.lower().strip()
    for known_loc, country in _LOCATION_TO_COUNTRY.items():
        if known_loc.lower() == loc_lower:
            return country

    parts = [p.strip() for p in location.split(",")]
    if len(parts) >= 2:
        suffix = parts[-1]
        for s, country in _COUNTRY_SUFFIX_TO_COUNTRY.items():
            if s.lower() == suffix.lower():
                return country

    return None


def get_relocation_factors(from_country: str, to_country: str) -> dict | None:
    """Return relocation factors between two countries. None if same country or unknown."""
    if from_country == to_country:
        return None

    from_profile = COUNTRY_PROFILES.get(from_country)
    to_profile = COUNTRY_PROFILES.get(to_country)

    if not from_profile or not to_profile:
        return None

    from_rate = from_profile["max_marginal_rate"]
    to_rate = to_profile["max_marginal_rate"]
    tax_diff = to_rate - from_rate

    if tax_diff < -0.05:
        tax_desc = f"Tax advantage: {to_country} has ~{abs(tax_diff)*100:.0f}% lower max rate"
    elif tax_diff > 0.05:
        tax_desc = f"Tax disadvantage: {to_country} has ~{tax_diff*100:.0f}% higher max rate"
    else:
        tax_desc = "Similar tax burden between the two countries"

    return {
        "from_country": from_country,
        "to_country": to_country,
        "visa_notes": to_profile.get("visa_for_work", "Check local requirements"),
        "tax_delta_description": tax_desc,
        "from_tax_regime": from_profile["tax_regime"],
        "to_tax_regime": to_profile["tax_regime"],
        "healthcare_comparison": f"From: {from_profile['healthcare']} → To: {to_profile['healthcare']}",
        "qol_delta": to_profile["quality_of_life_index"] - from_profile["quality_of_life_index"],
        "safety_delta": to_profile["safety_index"] - from_profile["safety_index"],
        "to_considerations": to_profile.get("considerations", []),
        "to_typical_benefits": to_profile.get("typical_benefits", []),
    }


def get_all_countries() -> list[dict]:
    """Return country list for the /api/countries endpoint."""
    result = []
    for name, profile in sorted(COUNTRY_PROFILES.items()):
        result.append({
            "name": name,
            "currency": profile["currency"],
            "tax_regime": profile["tax_regime"],
            "major_tech_hubs": profile["major_tech_hubs"],
            "quality_of_life_index": profile["quality_of_life_index"],
        })
    return result


if __name__ == "__main__":
    print(f"Countries: {len(COUNTRY_PROFILES)}")
    print(f"Infer 'Bangalore, India': {infer_country('Bangalore, India')}")
    factors = get_relocation_factors("United States", "India")
    if factors:
        print(f"US → India relocation: {factors['tax_delta_description']}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_country_data.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add utils/country_data.py tests/test_country_data.py
git commit -m "feat: add country data utility with profiles and relocation factors"
```

---

## Task 3: Add `currency` and `country` Fields to Offer Model

**Files:**
- Modify: `api_server.py:44-72`
- Modify: `frontend/types/index.ts:1-32`

- [ ] **Step 1: Add fields to backend `Offer` model**

In `api_server.py`, add two new fields to the `Offer` class (after line 67):

```python
# Add to Offer model (after relocation_support)
    currency: Optional[str] = "USD"   # ISO 4217 code
    country: Optional[str] = None     # Inferred from location if not provided
```

Add `comparison_currency` to `AnalyzeRequest` (after line 72):

```python
class AnalyzeRequest(BaseModel):
    offers: List[Offer] = Field(default_factory=list)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    comparison_currency: str = "USD"
```

- [ ] **Step 2: Add fields to frontend `Offer` type**

In `frontend/types/index.ts`, add to the `Offer` interface (after `relocation_support`):

```typescript
  currency: string     // ISO 4217, default "USD"
  country?: string     // Inferred from location
```

- [ ] **Step 3: Verify existing tests still pass**

Run: `pytest tests/ -v --timeout=30`
Expected: All existing tests PASS (new fields are optional with defaults)

- [ ] **Step 4: Commit**

```bash
git add api_server.py frontend/types/index.ts
git commit -m "feat: add currency and country fields to Offer model (backend + frontend)"
```

---

## Task 4: Add `/api/currencies` and `/api/countries` Endpoints

**Files:**
- Modify: `api_server.py` (add new endpoints)

- [ ] **Step 1: Add import for new utilities at top of `api_server.py`**

```python
from utils.currency import get_all_currencies, infer_currency
from utils.country_data import get_all_countries, infer_country
```

- [ ] **Step 2: Add the two GET endpoints**

Add after the existing `/api/usage` endpoint (~line 146):

```python
@app.get("/api/currencies")
async def list_currencies():
    """Return supported currencies with symbols and FX rates."""
    return get_all_currencies()


@app.get("/api/countries")
async def list_countries():
    """Return country profiles for relocation analysis UI."""
    return get_all_countries()
```

- [ ] **Step 3: Add auto-inference of currency/country in offer preparation**

In both `analyze` (~line 257) and `analyze_quick` (~line 257) endpoints, after building the `offers` list, add currency/country inference:

```python
        # After data["total_compensation"] calculation
        if not data.get("currency") or data["currency"] == "USD":
            inferred = infer_currency(data.get("location", ""))
            if inferred != "USD" and data.get("currency") != inferred:
                pass  # Only auto-infer if not explicitly set
            if not data.get("currency"):
                data["currency"] = inferred
        if not data.get("country"):
            data["country"] = infer_country(data.get("location", ""))
```

- [ ] **Step 4: Verify with a quick curl test**

Run: `python -c "from utils.currency import get_all_currencies; print(len(get_all_currencies()), 'currencies')"`
Expected: prints count of currencies

- [ ] **Step 5: Commit**

```bash
git add api_server.py
git commit -m "feat: add /api/currencies and /api/countries endpoints with auto-inference"
```

---

## Task 5: Backend Currency Normalization in `QuickFinancialAnalysisNode`

**Files:**
- Modify: `nodes.py:1347-1412` (`QuickFinancialAnalysisNode`)
- Modify: `nodes.py` (imports at top)

- [ ] **Step 1: Add currency import to `nodes.py`**

At the top of `nodes.py`, add:

```python
from utils.currency import convert_to_usd, convert_from_usd, get_fx_rate, infer_currency
from utils.country_data import infer_country
```

- [ ] **Step 2: Update `QuickFinancialAnalysisNode.prep` to include comparison_currency**

```python
    def prep(self, shared):
        offers = shared.get("offers", [])
        user_base_location = shared.get("user_preferences", {}).get("base_location", "San Francisco, CA")
        comparison_currency = shared.get("comparison_currency", "USD")

        items = []
        for offer in offers:
            items.append({
                "offer": offer,
                "base_location": user_base_location,
                "comparison_currency": comparison_currency,
            })
        return items
```

- [ ] **Step 3: Update `QuickFinancialAnalysisNode.exec` for currency conversion**

Replace the exec method body to handle multi-currency:

```python
    def exec(self, item):
        offer = item["offer"]
        base_location = item["base_location"]
        comparison_currency = item["comparison_currency"]
        offer_currency = offer.get("currency", "USD")

        tax_location = offer["location"]
        if "remote" in tax_location.lower():
            tax_location = base_location

        # --- Normalize all comp fields to USD first (universal pivot) ---
        total_comp = offer["total_compensation"]
        base_salary = offer.get("base_salary", 0)
        equity = offer.get("equity", 0)
        bonus = offer.get("bonus", 0)

        if offer_currency != "USD":
            total_comp_usd = convert_to_usd(total_comp, offer_currency)
            base_salary_usd = convert_to_usd(base_salary, offer_currency)
            equity_usd = convert_to_usd(equity, offer_currency)
            bonus_usd = convert_to_usd(bonus, offer_currency)
        else:
            total_comp_usd = total_comp
            base_salary_usd = base_salary
            equity_usd = equity
            bonus_usd = bonus

        # Tax calculation uses USD amounts + location-based rates
        net_pay_analysis = calculate_net_pay(total_comp_usd, tax_location)

        # COL is already USD-baseline
        expense_analysis = estimate_annual_expenses(offer["location"])
        annual_expenses = expense_analysis["estimated_annual_expenses"]

        net_pay_usd = net_pay_analysis["estimated_net_pay"]
        net_savings_usd = net_pay_usd - annual_expenses

        # --- Convert from USD to comparison currency if needed ---
        if comparison_currency != "USD":
            net_pay_comp = convert_from_usd(net_pay_usd, comparison_currency)
            net_savings_comp = convert_from_usd(net_savings_usd, comparison_currency)
            total_comp_comp = convert_from_usd(total_comp_usd, comparison_currency)
        else:
            net_pay_comp = net_pay_usd
            net_savings_comp = net_savings_usd
            total_comp_comp = total_comp_usd

        result = {
            "offer_id": offer["id"],
            "net_pay_analysis": net_pay_analysis,
            "expense_analysis": expense_analysis,
            "net_savings": net_savings_comp,
            "comparison_currency": comparison_currency,
            "normalized_base_salary": convert_from_usd(base_salary_usd, comparison_currency) if comparison_currency != "USD" else base_salary_usd,
            "normalized_equity": convert_from_usd(equity_usd, comparison_currency) if comparison_currency != "USD" else equity_usd,
            "normalized_bonus": convert_from_usd(bonus_usd, comparison_currency) if comparison_currency != "USD" else bonus_usd,
            "normalized_total_compensation": total_comp_comp,
        }

        # Preserve local currency fields for dual display
        if offer_currency != comparison_currency:
            fx_rate = get_fx_rate(offer_currency, comparison_currency)
            result["local_currency"] = offer_currency
            result["local_total_compensation"] = offer["total_compensation"]
            result["local_base_salary"] = base_salary
            result["local_equity"] = equity
            result["local_bonus"] = bonus
            result["fx_rate_used"] = fx_rate

        return result
```

- [ ] **Step 4: Update `post` to write local currency fields onto offers**

```python
    def post(self, shared, prep_res, exec_res_list):
        results_lookup = {r["offer_id"]: r for r in exec_res_list}

        for offer in shared["offers"]:
            if offer["id"] in results_lookup:
                res = results_lookup[offer["id"]]
                offer["net_pay_analysis"] = res["net_pay_analysis"]
                offer["estimated_net_pay"] = res["net_pay_analysis"]["estimated_net_pay"]
                offer["expense_analysis"] = res["expense_analysis"]
                offer["estimated_annual_expenses"] = res["expense_analysis"]["estimated_annual_expenses"]
                offer["net_savings"] = res["net_savings"]
                offer["estimated_tax"] = res["net_pay_analysis"]["estimated_tax_amount"]
                offer["comparison_currency"] = res["comparison_currency"]

                # Normalized amounts in comparison currency
                offer["normalized_base_salary"] = res["normalized_base_salary"]
                offer["normalized_equity"] = res["normalized_equity"]
                offer["normalized_bonus"] = res["normalized_bonus"]
                offer["normalized_total_compensation"] = res["normalized_total_compensation"]

                # Local currency fields for dual-display
                if "local_currency" in res:
                    offer["local_currency"] = res["local_currency"]
                    offer["local_total_compensation"] = res["local_total_compensation"]
                    offer["local_base_salary"] = res["local_base_salary"]
                    offer["local_equity"] = res["local_equity"]
                    offer["local_bonus"] = res["local_bonus"]
                    offer["fx_rate_used"] = res["fx_rate_used"]

        print(f"Quick financial analysis completed for {len(exec_res_list)} offers")
        return "default"
```

- [ ] **Step 5: Pass `comparison_currency` through in `api_server.py` endpoints**

In `analyze_quick` and `analyze` endpoints, add to the `shared` dict:

```python
    shared = {
        "offers": offers,
        "user_preferences": req.user_preferences or {},
        "comparison_currency": req.comparison_currency,
    }
```

- [ ] **Step 6: Run existing tests**

Run: `pytest tests/ -v --timeout=30`
Expected: All PASS (existing offers are USD, so conversion is identity)

- [ ] **Step 7: Commit**

```bash
git add nodes.py api_server.py
git commit -m "feat: currency-aware financial analysis with local/normalized dual amounts"
```

---

## Task 6: Expand International Tax Rates

**Files:**
- Modify: `utils/tax_calculator.py:8-61`

- [ ] **Step 1: Write a test for new cities**

Add to `tests/test_utils.py` or create a focused test:

```python
# In tests/test_utils.py — add to the tax calculator section
def test_international_tax_rates():
    """Verify new international cities have reasonable tax rates."""
    from utils.tax_calculator import estimate_tax_rate
    # India (30% slab + 4% cess ≈ 31.2%)
    rate = estimate_tax_rate("Bangalore, India")
    assert 0.25 <= rate <= 0.35
    # UAE (0% income tax)
    rate = estimate_tax_rate("Dubai, UAE")
    assert rate == 0.0
    # Seoul
    rate = estimate_tax_rate("Seoul, South Korea")
    assert 0.25 <= rate <= 0.40
```

- [ ] **Step 2: Run test to verify it fails (new cities not yet in TAX_RATES)**

Run: `pytest tests/test_utils.py::test_international_tax_rates -v`
Expected: FAIL (cities return default rate, not expected range)

- [ ] **Step 3: Add ~30 new international cities to `TAX_RATES`**

Append to the `TAX_RATES` dict in `utils/tax_calculator.py`:

```python
    # India (30% slab + 4% cess ≈ 31.2% effective for high earners)
    "Bangalore": 0.312, "Bengaluru": 0.312,
    "Mumbai": 0.312, "Hyderabad": 0.312,
    "Delhi": 0.312, "New Delhi": 0.312,
    "Pune": 0.312, "Chennai": 0.312,
    "Gurgaon": 0.312, "Noida": 0.312,
    # UAE (0% income tax)
    "Abu Dhabi": 0.0,
    # Middle East (0% income tax)
    "Riyadh": 0.0, "Doha": 0.0,
    # Southeast Asia
    "Jakarta": 0.30, "Bangkok": 0.25, "Ho Chi Minh City": 0.25,
    "Kuala Lumpur": 0.25, "Manila": 0.25,
    # East Asia
    "Seoul": 0.33, "Taipei": 0.20, "Shanghai": 0.35, "Beijing": 0.35,
    "Shenzhen": 0.35, "Hong Kong": 0.15, "Tokyo": 0.33,
    # More Europe
    "Lisbon": 0.35, "Barcelona": 0.37, "Madrid": 0.37,
    "Warsaw": 0.32, "Prague": 0.23, "Helsinki": 0.35,
    "Stockholm": 0.35, "Oslo": 0.34, "Copenhagen": 0.35,
    "Munich": 0.35, "Frankfurt": 0.35, "Hamburg": 0.35,
    "Zurich": 0.25, "Geneva": 0.28, "Milan": 0.38,
    "Dublin": 0.32, "Edinburgh": 0.33, "Manchester": 0.33,
    "Cambridge": 0.33, "Bristol": 0.33,
    # Oceania
    "Sydney": 0.37, "Melbourne": 0.37, "Auckland": 0.33,
    # Americas
    "Montreal": 0.33, "São Paulo": 0.275, "Mexico City": 0.30,
    # Israel
    "Tel Aviv": 0.35,
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_utils.py::test_international_tax_rates -v`
Expected: PASS

- [ ] **Step 5: Run full test suite**

Run: `pytest tests/ -v --timeout=30`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add utils/tax_calculator.py tests/test_utils.py
git commit -m "feat: expand tax calculator with ~30 international cities"
```

---

## Task 7: Expand COL Calculator with International Cities and Country Baselines

**Files:**
- Modify: `utils/col_calculator.py:9-95,160`

- [ ] **Step 1: Write a test for new COL cities and country baselines**

```python
def test_international_col_cities():
    """Verify new international cities have COL indices."""
    from utils.col_calculator import get_cost_index
    assert get_cost_index("Bangalore, India") > 0
    assert get_cost_index("Dubai, UAE") > 0
    assert get_cost_index("Doha, Qatar") > 0
    # Dubai should be more expensive than Bangalore
    assert get_cost_index("Dubai, UAE") > get_cost_index("Bangalore, India")
```

- [ ] **Step 2: Run test to verify it fails or returns default**

Run: `pytest tests/test_utils.py::test_international_col_cities -v`
Expected: Some may use default 75.0; Dubai > Bangalore assertion may fail

- [ ] **Step 3: Add missing cities to `COST_OF_LIVING_DATA` and add `BASELINE_EXPENSES_BY_COUNTRY`**

Add any missing cities. Also add after `BASELINE_ANNUAL_EXPENSES`:

```python
BASELINE_EXPENSES_BY_COUNTRY = {
    "United States": 60000,
    "India": 6000,
    "UAE": 30000,
    "United Kingdom": 42000,
    "Germany": 30000,
    "Singapore": 36000,
    "Canada": 36000,
    "Australia": 40000,
    "Japan": 36000,
    "Netherlands": 33000,
    "Switzerland": 55000,
    "Ireland": 36000,
    "South Korea": 24000,
    "Saudi Arabia": 24000,
    "Qatar": 28000,
    "Israel": 36000,
}
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_utils.py -v --timeout=30`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add utils/col_calculator.py tests/test_utils.py
git commit -m "feat: expand COL calculator with international cities and country baselines"
```

---

## Task 8: Currency-Aware Net Savings Scoring

**Files:**
- Modify: `utils/scoring.py:265-269`

- [ ] **Step 1: Write a test for currency-aware scoring**

```python
def test_net_savings_scoring_currency_aware():
    """Net savings scored relative to comparison-currency-appropriate reference."""
    from utils.scoring import calculate_offer_score
    # After financial analysis, net_savings is in comparison currency.
    # If comparison_currency is USD, $100k reference is correct.
    # If comparison_currency is INR, reference should be scaled by FX.
    usd_offer = {
        "id": "1", "company": "A", "position": "SWE", "location": "SF, CA",
        "base_salary": 200000, "equity": 0, "bonus": 0,
        "total_compensation": 200000, "net_savings": 50000,
        "comparison_currency": "USD",
    }
    score = calculate_offer_score(usd_offer, {}, {})
    assert score["total_score"] > 0
    # With comparison_currency=INR and net_savings already in INR
    inr_offer = {
        "id": "2", "company": "B", "position": "SWE", "location": "Bangalore, India",
        "base_salary": 5000000, "equity": 0, "bonus": 0,
        "total_compensation": 5000000, "net_savings": 4_166_667,
        "comparison_currency": "INR",
    }
    score_inr = calculate_offer_score(inr_offer, {}, {})
    # ~₹41.7L net savings ≈ $50k USD equivalent → should score similarly to $50k USD offer
    assert score_inr["total_score"] > 0
    assert abs(score["factor_scores"]["net_savings"] - score_inr["factor_scores"]["net_savings"]) < 15
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_utils.py::test_net_savings_scoring_currency_aware -v`
Expected: FAIL — scoring ignores `comparison_currency` and uses raw number against $100k

- [ ] **Step 3: Update scoring to scale reference by comparison currency**

In `utils/scoring.py`, update the net savings scoring block (around line 265-269):

```python
    # 9. Net Savings Score — scale reference to comparison currency
    net_savings = offer_data.get("net_savings", 0)
    comparison_currency = offer_data.get("comparison_currency", "USD")
    savings_reference = 100000  # USD baseline
    if comparison_currency != "USD":
        from utils.currency import convert_from_usd
        savings_reference = convert_from_usd(100000, comparison_currency)
    savings_score = min(100, max(0, (net_savings / savings_reference) * 100))
    factor_scores["net_savings"] = round(savings_score, 1)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_utils.py::test_net_savings_scoring_currency_aware -v`
Expected: PASS

- [ ] **Step 5: Run full test suite**

Run: `pytest tests/ -v --timeout=30`
Expected: All PASS (existing offers default to USD, so behavior unchanged)

- [ ] **Step 6: Commit**

```bash
git add utils/scoring.py tests/test_utils.py
git commit -m "feat: currency-aware net savings scoring with scaled reference"
```

---

## Task 9: Add Relocation Analysis to LLM Prompt (Cross-Country Detection)

**Files:**
- Modify: `nodes.py:1584-2027` (`QuickAIAnalysisNode`)

- [ ] **Step 1: Update `prep_async` to detect cross-country offers**

In `QuickAIAnalysisNode.prep_async`, after reading offers, add:

```python
        # Detect cross-country comparison
        countries = set()
        for offer in offers:
            country = offer.get("country") or infer_country(offer.get("location", ""))
            if country:
                countries.add(country)

        is_cross_country = len(countries) > 1
        current_country = user_preferences.get("current_country")

        return {
            "offers": offers,
            "user_preferences": user_preferences,
            "scoring_weights": weights,
            "is_cross_country": is_cross_country,
            "countries_involved": list(countries),
            "current_country": current_country,
        }
```

- [ ] **Step 2: Extend `_build_quick_analysis_prompt` with relocation section**

At the end of `_build_quick_analysis_prompt` (before the closing `"""`), add a conditional relocation block. Update the method signature to accept `is_cross_country`, `countries_involved`, and `current_country` parameters:

```python
    def _build_quick_analysis_prompt(self, offers, user_preferences, weights,
                                      is_cross_country=False, countries_involved=None,
                                      current_country=None):
```

Before the closing `"""`, add:

```python
        if is_cross_country:
            countries_str = ", ".join(countries_involved or [])
            prompt += f"""

7. Relocation Analysis: The user is comparing offers across different countries.
   Current country: {current_country or 'Not specified'}
   Offer countries: {countries_str}

   For EACH country transition, analyze:
   - Visa/work permit requirements and timeline
   - Tax regime comparison (effective rate, deductions, social security)
   - Healthcare system (public vs private, quality, cost)
   - Quality of life factors (safety, infrastructure, climate, culture)
   - Career ecosystem (tech community, startup scene, job market depth)
   - Financial considerations (retirement systems, currency stability, remittance)
   - Pros (top 3-5 reasons to move)
   - Cons (top 3-5 reasons to stay)

Add to your JSON response:
"relocation_analysis": {{
    "is_cross_country": true,
    "transitions": [
        {{
            "from_country": "Country A",
            "to_country": "Country B",
            "visa_requirements": "summary",
            "tax_comparison": "summary",
            "healthcare": "summary",
            "quality_of_life": "summary",
            "career_ecosystem": "summary",
            "financial_considerations": "summary",
            "pros": ["pro1", "pro2", "pro3"],
            "cons": ["con1", "con2", "con3"],
            "overall_recommendation": "summary"
        }}
    ]
}}
"""
```

- [ ] **Step 3: Update `exec_async` to pass cross-country params to prompt builder**

In `exec_async`, update the prompt builder call:

```python
        prompt = self._build_quick_analysis_prompt(
            offers, user_preferences, weights,
            is_cross_country=prep_data.get("is_cross_country", False),
            countries_involved=prep_data.get("countries_involved"),
            current_country=prep_data.get("current_country"),
        )
```

- [ ] **Step 4: Update `post_async` to store relocation_analysis**

In `post_async`, after storing existing results, add:

```python
        # Store relocation analysis if present
        if shared.get("is_cross_country") or prep_data.get("is_cross_country"):
            relocation = analysis_result.get("relocation_analysis", {})
            shared["relocation_analysis"] = relocation
            final_report["relocation_analysis"] = relocation
```

- [ ] **Step 5: Run existing tests**

Run: `pytest tests/ -v --timeout=30`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add nodes.py
git commit -m "feat: add cross-country relocation analysis to LLM prompt"
```

---

## Task 10: Update `_build_quick_analysis_prompt` for Multi-Currency Display

**Files:**
- Modify: `nodes.py:1860-1894` (prompt offer data section)

- [ ] **Step 1: Update offer data section in prompt to show local + normalized amounts**

Replace the per-offer prompt section (~lines 1876-1894) with currency-aware formatting:

```python
            local_cur = offer.get('local_currency')
            if local_cur and local_cur != 'USD':
                local_total = offer.get('local_total_compensation', 0)
                local_base = offer.get('local_base_salary', 0)
                fx_rate = offer.get('fx_rate_to_usd', 0)
                prompt += f"""
Offer {i}:
- Company: {offer.get('company', 'Unknown')}
- Position: {offer.get('position', 'Unknown')}
- Location: {offer.get('location', 'Unknown')}
- Currency: {local_cur} (FX: 1 {local_cur} = {fx_rate:.4f} USD)
- Base Salary: {local_base:,.0f} {local_cur} (≈ ${offer.get('base_salary', 0):,} USD)
- Total Compensation: {local_total:,.0f} {local_cur} (≈ ${offer.get('total_compensation', 0):,} USD)
- Estimated Tax Rate: {tax_rate_pct}
- Net Pay (USD equivalent): ${net_pay:,}
- Cost of Living: ${annual_expenses:,}/year
- Net Savings: ${net_savings:,}
- Market Percentile: {offer.get('market_analysis', {}).get('market_percentile', 'N/A')}
- WLB Score: {offer.get('wlb_score', 'N/A')}
- Growth Score: {offer.get('growth_score', 'N/A')}
"""
            else:
                prompt += f"""
Offer {i}:
- Company: {offer.get('company', 'Unknown')}
- Position: {offer.get('position', 'Unknown')}
- Location: {offer.get('location', 'Unknown')}
- Base Salary: ${offer.get('base_salary', 0):,}
- Equity/Year: ${offer.get('equity', 0):,}
- Bonus: ${offer.get('bonus', 0):,}
- Gross Total: ${offer.get('total_compensation', 0):,}
- Estimated Tax Rate: {tax_rate_pct}
- Estimated Tax: ${offer.get('net_pay_analysis', {}).get('estimated_tax_amount', 0):,}
- Net Pay: ${net_pay:,}
- Cost of Living: ${annual_expenses:,}/year
- Net Savings: ${net_savings:,}
- Market Percentile: {offer.get('market_analysis', {}).get('market_percentile', 'N/A')}
- WLB Score: {offer.get('wlb_score', 'N/A')}
- Growth Score: {offer.get('growth_score', 'N/A')}
"""
```

- [ ] **Step 2: Run tests**

Run: `pytest tests/ -v --timeout=30`
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add nodes.py
git commit -m "feat: multi-currency display in LLM analysis prompt"
```

---

## Task 11: Create Frontend Currency Formatting Library

**Files:**
- Create: `frontend/lib/currency.ts`

- [ ] **Step 1: Create `frontend/lib/currency.ts`**

```typescript
// frontend/lib/currency.ts

const CURRENCY_SYMBOLS: Record<string, string> = {
  USD: "$", INR: "₹", AED: "د.إ", GBP: "£", EUR: "€",
  SGD: "S$", CAD: "C$", AUD: "A$", JPY: "¥", CHF: "CHF",
  SEK: "kr", NOK: "kr", DKK: "kr", PLN: "zł", CZK: "Kč",
  ILS: "₪", KRW: "₩", TWD: "NT$", CNY: "¥", BRL: "R$",
  MXN: "$", SAR: "﷼", QAR: "﷼", THB: "฿", VND: "₫",
  IDR: "Rp", MYR: "RM", PHP: "₱", NZD: "NZ$", HKD: "HK$",
}

const CURRENCY_LOCALES: Record<string, string> = {
  USD: "en-US", INR: "en-IN", AED: "ar-AE", GBP: "en-GB", EUR: "de-DE",
  SGD: "en-SG", CAD: "en-CA", AUD: "en-AU", JPY: "ja-JP", CHF: "de-CH",
  KRW: "ko-KR", BRL: "pt-BR", MXN: "es-MX",
}

export function getCurrencySymbol(currency: string): string {
  return CURRENCY_SYMBOLS[currency] || currency
}

export function formatCurrency(amount: number, currency: string): string {
  const locale = CURRENCY_LOCALES[currency] || "en-US"
  try {
    return new Intl.NumberFormat(locale, {
      style: "currency",
      currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  } catch {
    const symbol = getCurrencySymbol(currency)
    return `${symbol}${amount.toLocaleString()}`
  }
}

export function formatCurrencyPair(
  localAmount: number,
  localCurrency: string,
  normalizedAmount: number,
  comparisonCurrency: string
): string {
  if (localCurrency === comparisonCurrency) {
    return formatCurrency(localAmount, localCurrency)
  }
  const local = formatCurrency(localAmount, localCurrency)
  const normalized = formatCurrency(normalizedAmount, comparisonCurrency)
  return `${local} (≈ ${normalized})`
}

export function inferCurrencyFromLocation(
  location: string,
  locationCurrencyMap: Record<string, string>
): string {
  if (!location) return "USD"
  const lower = location.toLowerCase().trim()
  for (const [loc, currency] of Object.entries(locationCurrencyMap)) {
    if (loc.toLowerCase() === lower) return currency
  }
  return "USD"
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/lib/currency.ts
git commit -m "feat: add frontend currency formatting utility"
```

---

## Task 12: Update `AdvancedOfferForm.tsx` — Currency Selector

**Files:**
- Modify: `frontend/components/AdvancedOfferForm.tsx`

- [ ] **Step 1: Add currency state and fetch currencies on mount**

Add to the component's state:

```typescript
const [currencies, setCurrencies] = useState<Array<{code: string, symbol: string, name: string}>>([])
```

Add a `useEffect` to fetch currencies from `/api/currencies`:

```typescript
useEffect(() => {
  fetch(`${getApiBase()}/api/currencies`)
    .then(res => res.json())
    .then(data => setCurrencies(data))
    .catch(() => {})
}, [])
```

- [ ] **Step 2: Add currency dropdown next to location**

After the location field, add a currency selector:

```tsx
<select
  value={formData.currency || 'USD'}
  onChange={(e) => setFormData(prev => ({ ...prev, currency: e.target.value }))}
  className="..."
>
  {currencies.map(c => (
    <option key={c.code} value={c.code}>
      {c.symbol} {c.code} — {c.name}
    </option>
  ))}
</select>
```

- [ ] **Step 3: Update salary labels to use dynamic currency symbol**

Replace hardcoded `"Base Salary ($)"` with:

```typescript
const symbol = getCurrencySymbol(formData.currency || 'USD')
// Then in label: `Base Salary (${symbol})`
```

Import `getCurrencySymbol` from `@/lib/currency`.

- [ ] **Step 4: Update `handleSubmit` to include currency in offer data**

Ensure the submitted offer includes `currency`:

```typescript
const offer: Offer = {
  // ... existing fields
  currency: formData.currency || 'USD',
}
```

- [ ] **Step 5: Visual check — run dev server and verify form renders**

Run: `cd frontend && npm run dev` (or check existing dev server)
Expected: Form shows currency dropdown, labels update dynamically

- [ ] **Step 6: Commit**

```bash
git add frontend/components/AdvancedOfferForm.tsx
git commit -m "feat: add currency selector to offer form with dynamic labels"
```

---

## Task 13: Update `OfferCards.tsx` — Dual-Currency Display

**Files:**
- Modify: `frontend/components/OfferCards.tsx`

- [ ] **Step 1: Add `comparisonCurrency` prop and import currency formatting**

Update `OfferCardsProps` to accept `comparisonCurrency`:

```typescript
import { formatCurrency, formatCurrencyPair } from '@/lib/currency'

interface OfferCardsProps {
  // ... existing props
  comparisonCurrency?: string
}
```

- [ ] **Step 2: Replace `$` prefix with currency-aware formatting**

For each compensation display line, use the `comparisonCurrency` prop (defaulting to 'USD'):

```typescript
const cc = comparisonCurrency || 'USD'

// For each amount field:
{offer.currency && offer.currency !== cc
  ? formatCurrencyPair(
      offer.base_salary,
      offer.currency,
      (offer as any).normalized_base_salary || offer.base_salary,
      cc
    )
  : formatCurrency(offer.base_salary, cc)}
```

Apply similar changes to `equity`, `bonus`, `total_compensation`.

- [ ] **Step 3: Commit**

```bash
git add frontend/components/OfferCards.tsx
git commit -m "feat: dual-currency display in offer cards"
```

---

## Task 14: Update `AnalysisResults.tsx` — Dual Currency in Tables + Relocation Section

**Files:**
- Modify: `frontend/components/AnalysisResults.tsx`
- Modify: `frontend/types/index.ts` (add `relocation_analysis` type)

- [ ] **Step 1: Add `relocation_analysis` type to `AnalysisResults` in `frontend/types/index.ts`**

Add to the `AnalysisResults` interface:

```typescript
  relocation_analysis?: {
    is_cross_country: boolean
    transitions: Array<{
      from_country: string
      to_country: string
      visa_requirements: string
      tax_comparison: string
      healthcare: string
      quality_of_life: string
      career_ecosystem: string
      financial_considerations: string
      pros: string[]
      cons: string[]
      overall_recommendation: string
    }>
  }
```

- [ ] **Step 2: Add `comparisonCurrency` prop and replace hardcoded `$`/`USD`**

Add `comparisonCurrency` to the component props:

```typescript
interface AnalysisResultsProps {
  results: AnalysisResults
  comparisonCurrency?: string
}
```

Replace all `Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })` calls and `'$' + ...` with:

```typescript
import { formatCurrency } from '@/lib/currency'

const cc = comparisonCurrency || 'USD'
// Replace:
// new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
// With:
formatCurrency(amount, cc)
```

Also update chart tooltip callbacks to use `formatCurrency` instead of `'$' + ...`.

- [ ] **Step 3: Add Relocation Analysis section**

Add a new tab or collapsible section that renders when `relocation_analysis?.is_cross_country` is true:

```tsx
{results.relocation_analysis?.is_cross_country && (
  <div className="mt-8">
    <h3 className="text-xl font-bold mb-4">Relocation Analysis</h3>
    {results.relocation_analysis.transitions.map((t, i) => (
      <div key={i} className="bg-white rounded-lg p-6 mb-4 shadow-sm border">
        <h4 className="font-semibold text-lg mb-3">
          {t.from_country} → {t.to_country}
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div><strong>Visa:</strong> {t.visa_requirements}</div>
          <div><strong>Tax:</strong> {t.tax_comparison}</div>
          <div><strong>Healthcare:</strong> {t.healthcare}</div>
          <div><strong>Quality of Life:</strong> {t.quality_of_life}</div>
          <div><strong>Career:</strong> {t.career_ecosystem}</div>
          <div><strong>Financial:</strong> {t.financial_considerations}</div>
        </div>
        <div className="grid grid-cols-2 gap-4 mt-4">
          <div>
            <h5 className="font-semibold text-green-600">Pros</h5>
            <ul className="list-disc pl-4">
              {t.pros.map((p, j) => <li key={j}>{p}</li>)}
            </ul>
          </div>
          <div>
            <h5 className="font-semibold text-red-600">Cons</h5>
            <ul className="list-disc pl-4">
              {t.cons.map((c, j) => <li key={j}>{c}</li>)}
            </ul>
          </div>
        </div>
        <p className="mt-3 italic text-gray-600">{t.overall_recommendation}</p>
      </div>
    ))}
  </div>
)}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/components/AnalysisResults.tsx frontend/types/index.ts
git commit -m "feat: dual-currency display and relocation analysis section in results"
```

---

## Task 15: Update `page.tsx` — Comparison Currency State and Dropdown

**Files:**
- Modify: `frontend/app/page.tsx`

- [ ] **Step 1: Add `comparisonCurrency` state**

```typescript
const [comparisonCurrency, setComparisonCurrency] = useState<string>('USD')
```

- [ ] **Step 2: Include `comparison_currency` in API request body**

In `runAnalysis`, add to the request body:

```typescript
const response = await axios.post(`${apiBase}/api/analyze/quick`, {
  offers: selectedOfferData,
  user_preferences: preferences,
  comparison_currency: comparisonCurrency,
})
```

- [ ] **Step 3: Add a "Compare in" currency selector near the analyze button**

```tsx
<select
  value={comparisonCurrency}
  onChange={(e) => setComparisonCurrency(e.target.value)}
  className="text-sm border rounded px-2 py-1"
>
  <option value="USD">Compare in USD ($)</option>
  <option value="INR">Compare in INR (₹)</option>
  <option value="GBP">Compare in GBP (£)</option>
  <option value="EUR">Compare in EUR (€)</option>
</select>
```

- [ ] **Step 4: Pass `comparisonCurrency` to `AnalysisResults` and `OfferCards`**

```tsx
<OfferCards offers={offers} comparisonCurrency={comparisonCurrency} ... />
<AnalysisResults results={analysisResults} comparisonCurrency={comparisonCurrency} />
```

- [ ] **Step 5: Commit**

```bash
git add frontend/app/page.tsx
git commit -m "feat: add comparison currency selector and pass to API"
```

---

## Task 16: Add "Current Country" Preference Control

**Files:**
- Modify: `frontend/app/page.tsx` or `frontend/components/PreferencesPanel.tsx` (wherever user preferences are managed)

- [ ] **Step 1: Add `currentCountry` state**

```typescript
const [currentCountry, setCurrentCountry] = useState<string>('')
```

- [ ] **Step 2: Add a "Your Current Country" selector**

Add a dropdown near the comparison currency selector (or in the preferences panel):

```tsx
<label className="text-sm font-medium">Your Current Country</label>
<select
  value={currentCountry}
  onChange={(e) => setCurrentCountry(e.target.value)}
  className="text-sm border rounded px-2 py-1"
>
  <option value="">Not specified</option>
  <option value="United States">United States</option>
  <option value="India">India</option>
  <option value="UAE">UAE</option>
  <option value="United Kingdom">United Kingdom</option>
  <option value="Germany">Germany</option>
  <option value="Singapore">Singapore</option>
  <option value="Canada">Canada</option>
  {/* Add more countries from /api/countries */}
</select>
```

- [ ] **Step 3: Include `current_country` in `user_preferences` when calling API**

```typescript
const response = await axios.post(`${apiBase}/api/analyze/quick`, {
  offers: selectedOfferData,
  user_preferences: { ...preferences, current_country: currentCountry || undefined },
  comparison_currency: comparisonCurrency,
})
```

- [ ] **Step 4: Commit**

```bash
git add frontend/app/page.tsx
git commit -m "feat: add current country preference for relocation analysis"
```

---

## Task 17: Add More International City Multipliers to Market Data

**Files:**
- Modify: `utils/market_data.py:105-144`

- [ ] **Step 1: Add missing international multipliers**

Append to `LOCATION_SALARY_MULTIPLIERS` in `utils/market_data.py`:

```python
    # More international cities (USD equivalent multiplier from SF baseline)
    "Bangalore": 0.30, "Bengaluru": 0.30,
    "Hyderabad": 0.28, "Pune": 0.28,
    "Mumbai": 0.32, "Delhi": 0.30, "Chennai": 0.28,
    "Gurgaon": 0.30, "Noida": 0.28,
    "Abu Dhabi": 0.70,
    "Riyadh": 0.55, "Doha": 0.60,
    "Jakarta": 0.25, "Bangkok": 0.28,
    "Ho Chi Minh City": 0.22, "Kuala Lumpur": 0.30,
    "Manila": 0.22,
    "Seoul": 0.55, "Taipei": 0.40,
    "Shanghai": 0.45, "Beijing": 0.45, "Shenzhen": 0.45,
    "Hong Kong": 0.70,
    "São Paulo": 0.35, "Mexico City": 0.30,
    "Tel Aviv": 0.65,
    "Prague": 0.40, "Warsaw": 0.35,
    "Lisbon": 0.40, "Barcelona": 0.45, "Madrid": 0.45,
    "Helsinki": 0.55, "Stockholm": 0.60,
    "Oslo": 0.60, "Copenhagen": 0.60,
    "Milan": 0.50,
    "Zurich": 1.10, "Geneva": 1.05,
    "Edinburgh": 0.65, "Manchester": 0.60,
    "Cambridge": 0.70, "Bristol": 0.60,
    "Auckland": 0.55,
    "Montreal": 0.65,
```

- [ ] **Step 2: Run tests**

Run: `pytest tests/test_utils.py -v --timeout=30`
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add utils/market_data.py
git commit -m "feat: add ~40 international city salary multipliers to market data"
```

---

## Task 18: End-to-End Verification

- [ ] **Step 1: Run the full backend test suite**

Run: `pytest tests/ -v --timeout=60`
Expected: All PASS

- [ ] **Step 2: Start backend server and test new endpoints**

Run: `python api_server.py` (or use existing server)

Test with curl:

```bash
curl http://localhost:8001/api/currencies | python -m json.tool | head -20
curl http://localhost:8001/api/countries | python -m json.tool | head -20
```

Expected: JSON arrays of currencies and countries

- [ ] **Step 3: Test quick analysis with a multi-currency payload**

```bash
curl -X POST http://localhost:8001/api/analyze/quick \
  -H "Content-Type: application/json" \
  -d '{
    "offers": [
      {"company": "Google", "position": "SWE", "location": "San Francisco, CA", "base_salary": 200000, "equity": 50000, "bonus": 30000, "currency": "USD"},
      {"company": "Flipkart", "position": "SWE", "location": "Bangalore, India", "base_salary": 5000000, "equity": 500000, "bonus": 200000, "currency": "INR"}
    ],
    "comparison_currency": "USD"
  }'
```

Expected: Successful response with normalized USD amounts and relocation analysis section.

- [ ] **Step 4: Final commit with any fixes**

```bash
git add -A
git commit -m "feat: worldwide currency support — end-to-end integration"
```

---

## Scope Notes

The following spec items are **deferred** from this plan (can be added in a follow-up):
- `fetch_live_rates()` — live FX rate refresh via external API
- `TAX_REGIME_INFO` — detailed per-location tax notes dict
- Cross-market percentile annotation (e.g., "P65 in India tech market")
- Country flag emoji in OfferCards

---

## Implementation Order Summary

```
Task 1:  utils/currency.py (data + conversion)
Task 2:  utils/country_data.py (profiles + relocation)
Task 3:  Offer model fields (backend + frontend)
Task 4:  API endpoints (/currencies, /countries)
Task 5:  Backend normalization (QuickFinancialAnalysisNode)
Task 6:  Expand tax rates (international)
Task 7:  Expand COL data (international + country baselines)
Task 8:  Currency-aware scoring
Task 9:  Relocation LLM prompt extension
Task 10: Multi-currency prompt formatting
Task 11: Frontend currency lib
Task 12: Form currency selector
Task 13: Offer cards dual-currency
Task 14: Analysis results dual-currency + relocation UI
Task 15: Page-level comparison currency state
Task 16: Current country preference control
Task 17: Market data international multipliers
Task 18: End-to-end verification
```

Tasks 1-2 are independent and can be parallelized.
Tasks 6-7-8-17 are independent data expansions that can be parallelized.
Tasks 11-12-13-14-15-16 are frontend tasks that should be sequential.
