"""
Tests for utils.currency — currency data, FX conversion, and location inference.
"""

import pytest

from utils.currency import (
    CURRENCY_DATA,
    FX_RATES_TO_USD,
    convert_to_usd,
    convert_from_usd,
    get_fx_rate,
    infer_currency,
    get_all_currencies,
)


REQUIRED_CURRENCY_KEYS = ("symbol", "name", "locale")


class TestCurrencyData:
    def test_currency_data_has_required_keys(self):
        for code, meta in CURRENCY_DATA.items():
            assert isinstance(code, str) and len(code) == 3
            for key in REQUIRED_CURRENCY_KEYS:
                assert key in meta, f"{code} missing {key}"
                assert isinstance(meta[key], str) and meta[key].strip()

    def test_locale_tags_are_bcp47(self):
        for code, meta in CURRENCY_DATA.items():
            loc = meta["locale"]
            assert "_" not in loc, f"{code} locale should use hyphens (BCP 47): {loc!r}"

    def test_usd_inr_symbols(self):
        assert CURRENCY_DATA["USD"]["symbol"] == "$"
        assert CURRENCY_DATA["INR"]["symbol"] == "₹"


class TestFxRates:
    def test_all_non_usd_have_fx_rates(self):
        for code in CURRENCY_DATA:
            if code == "USD":
                continue
            assert code in FX_RATES_TO_USD
            assert isinstance(FX_RATES_TO_USD[code], (int, float))
            assert FX_RATES_TO_USD[code] > 0

    def test_usd_not_in_fx_rates(self):
        assert "USD" not in FX_RATES_TO_USD


class TestConvertToUsd:
    def test_usd_identity(self):
        assert convert_to_usd(100, "USD") == 100.0

    def test_inr_less_than_amount(self):
        usd = convert_to_usd(100_000, "INR")
        assert usd > 0
        assert usd < 100_000

    def test_unknown_raises(self):
        with pytest.raises(KeyError):
            convert_to_usd(1, "XXX")


class TestConvertFromUsd:
    def test_inr_greater_than_amount(self):
        out = convert_from_usd(1000, "INR")
        assert out > 1000

    def test_unknown_raises(self):
        with pytest.raises(KeyError):
            convert_from_usd(1, "XXX")


class TestRoundTrip:
    def test_gbp_round_trip(self):
        start = 250.5
        usd = convert_to_usd(start, "GBP")
        back = convert_from_usd(usd, "GBP")
        assert abs(back - start) < 0.01


class TestGetFxRate:
    def test_same_currency_usd(self):
        assert get_fx_rate("USD", "USD") == 1.0

    def test_cross_positive(self):
        r = get_fx_rate("EUR", "GBP")
        assert r > 0

    def test_unknown_raises(self):
        with pytest.raises(KeyError):
            get_fx_rate("USD", "ZZZ")


class TestInferCurrency:
    def test_bangalore_india(self):
        assert infer_currency("Bangalore, India") == "INR"

    def test_dubai_uae(self):
        assert infer_currency("Dubai, UAE") == "AED"

    def test_san_francisco_ca(self):
        assert infer_currency("San Francisco, CA") == "USD"

    def test_bangalore_iso_country_suffix_in(self):
        assert infer_currency("Bangalore, IN") == "INR"

    def test_toronto_iso_country_suffix_ca(self):
        assert infer_currency("Toronto, CA") == "CAD"

    def test_london_uk(self):
        assert infer_currency("London, UK") == "GBP"

    def test_unknown_defaults_usd(self):
        assert infer_currency("Atlantis, Underwater") == "USD"

    def test_remote_usd(self):
        assert infer_currency("Remote") == "USD"

    def test_case_insensitive(self):
        assert infer_currency("bangalore, india") == "INR"
        assert infer_currency("LONDON, uk") == "GBP"


class TestGetAllCurrencies:
    def test_structure(self):
        rows = get_all_currencies()
        assert isinstance(rows, list)
        assert len(rows) == len(CURRENCY_DATA)
        codes = set()
        for row in rows:
            assert isinstance(row, dict)
            assert set(row.keys()) >= {"code", "symbol", "name", "rate_to_usd"}
            assert row["code"] in CURRENCY_DATA
            codes.add(row["code"])
            assert row["symbol"] == CURRENCY_DATA[row["code"]]["symbol"]
            assert row["name"] == CURRENCY_DATA[row["code"]]["name"]
            assert isinstance(row["rate_to_usd"], float)
            if row["code"] == "USD":
                assert row["rate_to_usd"] == 1.0
            else:
                assert row["rate_to_usd"] == FX_RATES_TO_USD[row["code"]]
        assert codes == set(CURRENCY_DATA.keys())
