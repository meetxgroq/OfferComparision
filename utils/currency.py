"""
Currency metadata, approximate FX rates (USD pivot), conversion helpers, and
location → currency inference for BenchMarked.
"""

from __future__ import annotations

from typing import Dict, List, Union

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

# Lowercase "City, Region" → ISO currency (explicit overrides)
LOCATION_TO_CURRENCY: Dict[str, str] = {
    "remote": "USD",
    "san francisco, ca": "USD",
    "new york, ny": "USD",
    "bangalore, india": "INR",
    "bengaluru, india": "INR",
    "mumbai, india": "INR",
    "delhi, india": "INR",
    "hyderabad, india": "INR",
    "chennai, india": "INR",
    "pune, india": "INR",
    "kolkata, india": "INR",
    "dubai, uae": "AED",
    "abu dhabi, uae": "AED",
    "sharjah, uae": "AED",
    "london, uk": "GBP",
    "manchester, uk": "GBP",
    "edinburgh, uk": "GBP",
    "birmingham, uk": "GBP",
    "los angeles, ca": "USD",
    "seattle, wa": "USD",
    "austin, tx": "USD",
    "boston, ma": "USD",
    "chicago, il": "USD",
    "denver, co": "USD",
    "atlanta, ga": "USD",
    "miami, fl": "USD",
    "dallas, tx": "USD",
    "phoenix, az": "USD",
    "philadelphia, pa": "USD",
    "houston, tx": "USD",
    "san diego, ca": "USD",
    "san jose, ca": "USD",
    "portland, or": "USD",
    "detroit, mi": "USD",
    "minneapolis, mn": "USD",
    "charlotte, nc": "USD",
    "nashville, tn": "USD",
    "salt lake city, ut": "USD",
    "raleigh, nc": "USD",
    "pittsburgh, pa": "USD",
    "columbus, oh": "USD",
    "indianapolis, in": "USD",
    "kansas city, mo": "USD",
    "st. louis, mo": "USD",
    "tampa, fl": "USD",
    "orlando, fl": "USD",
    "las vegas, nv": "USD",
    "paris, france": "EUR",
    "berlin, germany": "EUR",
    "munich, germany": "EUR",
    "amsterdam, netherlands": "EUR",
    "dublin, ireland": "EUR",
    "madrid, spain": "EUR",
    "barcelona, spain": "EUR",
    "rome, italy": "EUR",
    "milan, italy": "EUR",
    "brussels, belgium": "EUR",
    "vienna, austria": "EUR",
    "warsaw, poland": "PLN",
    "prague, czech republic": "CZK",
    "stockholm, sweden": "SEK",
    "oslo, norway": "NOK",
    "copenhagen, denmark": "DKK",
    "zurich, switzerland": "CHF",
    "tel aviv, israel": "ILS",
    "singapore": "SGD",
    "tokyo, japan": "JPY",
    "osaka, japan": "JPY",
    "seoul, south korea": "KRW",
    "taipei, taiwan": "TWD",
    "shanghai, china": "CNY",
    "beijing, china": "CNY",
    "shenzhen, china": "CNY",
    "hong kong": "HKD",
    "sydney, australia": "AUD",
    "melbourne, australia": "AUD",
    "brisbane, australia": "AUD",
    "perth, australia": "AUD",
    "auckland, new zealand": "NZD",
    "wellington, new zealand": "NZD",
    "toronto, canada": "CAD",
    "vancouver, canada": "CAD",
    "montreal, canada": "CAD",
    "calgary, canada": "CAD",
    "mexico city, mexico": "MXN",
    "guadalajara, mexico": "MXN",
    "monterrey, mexico": "MXN",
    "são paulo, brazil": "BRL",
    "rio de janeiro, brazil": "BRL",
    "buenos aires, argentina": "USD",
    "santiago, chile": "USD",
    "bogotá, colombia": "USD",
    "lima, peru": "USD",
    "riyadh, saudi arabia": "SAR",
    "jeddah, saudi arabia": "SAR",
    "doha, qatar": "QAR",
    "bangkok, thailand": "THB",
    "ho chi minh city, vietnam": "VND",
    "hanoi, vietnam": "VND",
    "jakarta, indonesia": "IDR",
    "kuala lumpur, malaysia": "MYR",
    "manila, philippines": "PHP",
    "cairo, egypt": "USD",
    "johannesburg, south africa": "USD",
    "cape town, south africa": "USD",
    "istanbul, turkey": "USD",
    "moscow, russia": "USD",
}

# Trailing segment (lowercase) → currency when not matched as full location.
# US city+state pairs live in LOCATION_TO_CURRENCY; ambiguous 2-letter US state
# codes (CA, NY, …) are omitted so ISO country codes IN and CA map correctly.
_COUNTRY_SUFFIX_TO_CURRENCY: Dict[str, str] = {
    "india": "INR",
    "in": "INR",
    "uae": "AED",
    "united arab emirates": "AED",
    "uk": "GBP",
    "united kingdom": "GBP",
    "usa": "USD",
    "us": "USD",
    "united states": "USD",
    "america": "USD",
    "ca": "CAD",
    "mi": "USD",
    "tn": "USD",
    "ut": "USD",
    "oh": "USD",
    "mo": "USD",
    "nv": "USD",
    "france": "EUR",
    "germany": "EUR",
    "netherlands": "EUR",
    "ireland": "EUR",
    "spain": "EUR",
    "italy": "EUR",
    "belgium": "EUR",
    "austria": "EUR",
    "portugal": "EUR",
    "finland": "EUR",
    "greece": "EUR",
    "poland": "PLN",
    "czech republic": "CZK",
    "czechia": "CZK",
    "sweden": "SEK",
    "norway": "NOK",
    "denmark": "DKK",
    "switzerland": "CHF",
    "israel": "ILS",
    "japan": "JPY",
    "south korea": "KRW",
    "korea": "KRW",
    "taiwan": "TWD",
    "china": "CNY",
    "australia": "AUD",
    "new zealand": "NZD",
    "canada": "CAD",
    "mexico": "MXN",
    "brazil": "BRL",
    "saudi arabia": "SAR",
    "qatar": "QAR",
    "thailand": "THB",
    "vietnam": "VND",
    "indonesia": "IDR",
    "malaysia": "MYR",
    "philippines": "PHP",
    "singapore": "SGD",
    "hong kong": "HKD",
}


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
    if not location or not str(location).strip():
        return "USD"
    normalized = " ".join(str(location).strip().split()).lower()
    if normalized in LOCATION_TO_CURRENCY:
        return LOCATION_TO_CURRENCY[normalized]
    if normalized in _COUNTRY_SUFFIX_TO_CURRENCY:
        return _COUNTRY_SUFFIX_TO_CURRENCY[normalized]
    parts = [p.strip() for p in normalized.split(",") if p.strip()]
    for segment in reversed(parts):
        if segment in _COUNTRY_SUFFIX_TO_CURRENCY:
            return _COUNTRY_SUFFIX_TO_CURRENCY[segment]
    return "USD"


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
