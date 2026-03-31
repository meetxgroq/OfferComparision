"""
Currency metadata, approximate FX rates (USD pivot), conversion helpers, and
location → currency inference for BenchMarked.
"""

from __future__ import annotations

from typing import Dict, List, Union

from utils.location_registry import (
    LOCATION_REGISTRY,
    _ALIAS_INDEX,
    infer_currency as _registry_infer_currency,
)

# ISO 4217 code → display and locale hints
CURRENCY_DATA: Dict[str, Dict[str, str]] = {
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
    "TWD": {"symbol": "NT$", "name": "Taiwan Dollar", "locale": "zh-TW"},
    "CNY": {"symbol": "¥", "name": "Chinese Yuan", "locale": "zh-CN"},
    "BRL": {"symbol": "R$", "name": "Brazilian Real", "locale": "pt-BR"},
    "MXN": {"symbol": "MX$", "name": "Mexican Peso", "locale": "es-MX"},
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

# 1 unit of currency → USD (approximate mid-market, early 2026). USD omitted.
FX_RATES_TO_USD: Dict[str, float] = {
    "INR": 0.0119,
    "AED": 0.272,
    "GBP": 1.27,
    "EUR": 1.08,
    "SGD": 0.74,
    "CAD": 0.71,
    "AUD": 0.65,
    "JPY": 0.00665,
    "CHF": 1.12,
    "SEK": 0.095,
    "NOK": 0.091,
    "DKK": 0.145,
    "PLN": 0.25,
    "CZK": 0.043,
    "ILS": 0.27,
    "KRW": 0.00068,
    "TWD": 0.031,
    "CNY": 0.138,
    "BRL": 0.18,
    "MXN": 0.055,
    "SAR": 0.267,
    "QAR": 0.275,
    "THB": 0.028,
    "VND": 0.000038,
    "IDR": 0.000062,
    "MYR": 0.22,
    "PHP": 0.017,
    "NZD": 0.59,
    "HKD": 0.128,
}

# Backward-compatible view — includes canonical keys AND alias keys (lowered)
LOCATION_TO_CURRENCY: Dict[str, str] = {
    k.lower(): e.currency for k, e in LOCATION_REGISTRY.items()
}
for _alias_lower, _canonical in _ALIAS_INDEX.items():
    _entry = LOCATION_REGISTRY.get(_canonical)
    if _entry and _alias_lower not in LOCATION_TO_CURRENCY:
        LOCATION_TO_CURRENCY[_alias_lower] = _entry.currency


def convert_to_usd(amount: float, from_currency: str) -> float:
    code = from_currency.upper()
    if code == "USD":
        return float(amount)
    if code not in FX_RATES_TO_USD:
        raise KeyError(from_currency)
    return float(amount) * FX_RATES_TO_USD[code]


def convert_from_usd(amount: float, to_currency: str) -> float:
    code = to_currency.upper()
    if code == "USD":
        return float(amount)
    if code not in FX_RATES_TO_USD:
        raise KeyError(to_currency)
    return float(amount) / FX_RATES_TO_USD[code]


def get_fx_rate(from_currency: str, to_currency: str) -> float:
    f = from_currency.upper()
    t = to_currency.upper()
    if f == t:
        return 1.0
    usd_per_from = 1.0 if f == "USD" else FX_RATES_TO_USD[f]
    usd_per_to = 1.0 if t == "USD" else FX_RATES_TO_USD[t]
    return usd_per_from / usd_per_to


def infer_currency(location: str) -> str:
    return _registry_infer_currency(location)


def get_all_currencies() -> List[Dict[str, Union[str, float]]]:
    return [
        {
            "code": code,
            "symbol": meta["symbol"],
            "name": meta["name"],
            "rate_to_usd": 1.0 if code == "USD" else FX_RATES_TO_USD[code],
        }
        for code, meta in sorted(CURRENCY_DATA.items())
    ]


if __name__ == "__main__":
    print("Smoke:", convert_to_usd(100, "USD"), infer_currency("Dubai, UAE"))
    assert convert_to_usd(1, "EUR") > 0
    assert get_fx_rate("USD", "EUR") > 0
