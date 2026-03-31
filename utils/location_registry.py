"""
Canonical location registry — single source of truth for all city metadata.

Every city is defined once with a canonical key in "City, Region" format.
Aliases (bare city names, abbreviations) resolve to canonical keys via _ALIAS_INDEX.
"""

from __future__ import annotations

from typing import Dict, List, Optional


class LocationEntry:
    """Typed container for per-location metadata."""
    __slots__ = ("country", "currency", "tax_rate", "col_index", "salary_multiplier", "aliases")

    def __init__(
        self,
        country: str,
        currency: str,
        tax_rate: float,
        col_index: float,
        salary_multiplier: float,
        aliases: Optional[List[str]] = None,
    ):
        self.country = country
        self.currency = currency
        self.tax_rate = tax_rate
        self.col_index = col_index
        self.salary_multiplier = salary_multiplier
        self.aliases = aliases or []


# Default fallback values (match current behavior across modules)
_DEFAULT_TAX_RATE = 0.30
_DEFAULT_COL_INDEX = 75.0
_DEFAULT_SALARY_MULTIPLIER = 0.85

LOCATION_REGISTRY: Dict[str, LocationEntry] = {
    # ── US Major Tech Hubs ──────────────────────────────────────────────
    "San Francisco, CA": LocationEntry("United States", "USD", 0.38, 100.0, 1.0, ["sf", "bay area"]),
    "San Jose, CA": LocationEntry("United States", "USD", 0.38, 95.0, 0.98, ["silicon valley", "sunnyvale", "santa clara", "cupertino"]),
    "Palo Alto, CA": LocationEntry("United States", "USD", 0.38, 110.0, 1.02, ["menlo park"]),
    "Mountain View, CA": LocationEntry("United States", "USD", 0.38, 105.0, 1.02),
    "New York, NY": LocationEntry("United States", "USD", 0.39, 85.0, 0.95, ["nyc", "ny"]),
    "Manhattan, NY": LocationEntry("United States", "USD", 0.39, 90.0, 0.95),
    "Brooklyn, NY": LocationEntry("United States", "USD", 0.39, 75.0, 0.90),
    "Seattle, WA": LocationEntry("United States", "USD", 0.26, 78.0, 0.90),
    "Redmond, WA": LocationEntry("United States", "USD", 0.26, 78.0, 0.88, ["kirkland"]),
    "Bellevue, WA": LocationEntry("United States", "USD", 0.26, 78.0, 0.88),
    "Los Angeles, CA": LocationEntry("United States", "USD", 0.38, 70.0, 0.85, ["la", "santa monica"]),
    "San Diego, CA": LocationEntry("United States", "USD", 0.38, 65.0, 0.83),
    "Boston, MA": LocationEntry("United States", "USD", 0.32, 72.0, 0.88),
    "Cambridge, MA": LocationEntry("United States", "USD", 0.32, 75.0, 0.88),
    "Washington, DC": LocationEntry("United States", "USD", 0.32, 68.0, 0.85, ["dc"]),
    "Arlington, VA": LocationEntry("United States", "USD", 0.32, 68.0, 0.85),
    "Chicago, IL": LocationEntry("United States", "USD", 0.32, 55.0, 0.75),
    "Denver, CO": LocationEntry("United States", "USD", 0.30, 58.0, 0.78),
    "Boulder, CO": LocationEntry("United States", "USD", 0.30, 58.0, 0.78),
    "Portland, OR": LocationEntry("United States", "USD", 0.35, 60.0, 0.82),
    "Austin, TX": LocationEntry("United States", "USD", 0.26, 52.0, 0.80),
    "Dallas, TX": LocationEntry("United States", "USD", 0.26, 48.0, 0.72),
    "Houston, TX": LocationEntry("United States", "USD", 0.26, 45.0, 0.72),
    "Atlanta, GA": LocationEntry("United States", "USD", 0.32, 45.0, 0.70),
    "Miami, FL": LocationEntry("United States", "USD", 0.26, 50.0, 0.70),
    "Orlando, FL": LocationEntry("United States", "USD", 0.26, 45.0, 0.68),
    "Phoenix, AZ": LocationEntry("United States", "USD", 0.29, 42.0, 0.68, ["scottsdale"]),
    "Las Vegas, NV": LocationEntry("United States", "USD", 0.26, 40.0, 0.68, ["vegas"]),
    "Salt Lake City, UT": LocationEntry("United States", "USD", 0.31, 45.0, 0.72, ["slc"]),
    "Minneapolis, MN": LocationEntry("United States", "USD", 0.34, 50.0, 0.75),
    "Detroit, MI": LocationEntry("United States", "USD", 0.33, 35.0, 0.65),
    "Pittsburgh, PA": LocationEntry("United States", "USD", 0.31, 38.0, 0.72),
    "Philadelphia, PA": LocationEntry("United States", "USD", 0.33, 55.0, 0.78, ["philly"]),
    "Raleigh, NC": LocationEntry("United States", "USD", 0.31, 40.0, 0.72, ["rtp"]),
    "Durham, NC": LocationEntry("United States", "USD", 0.31, 40.0, 0.72),
    "Nashville, TN": LocationEntry("United States", "USD", 0.26, 42.0, 0.70),
    "Charlotte, NC": LocationEntry("United States", "USD", 0.31, 42.0, 0.70),
    "Columbus, OH": LocationEntry("United States", "USD", 0.30, 42.0, 0.68),
    "Indianapolis, IN": LocationEntry("United States", "USD", 0.30, 40.0, 0.65),
    "Kansas City, MO": LocationEntry("United States", "USD", 0.30, 40.0, 0.65),
    "St. Louis, MO": LocationEntry("United States", "USD", 0.30, 40.0, 0.65),
    "Tampa, FL": LocationEntry("United States", "USD", 0.26, 45.0, 0.68),

    # ── UK ──────────────────────────────────────────────────────────────
    "London, UK": LocationEntry("United Kingdom", "GBP", 0.40, 85.0, 0.80),
    "Edinburgh, UK": LocationEntry("United Kingdom", "GBP", 0.33, 60.0, 0.65),
    "Manchester, UK": LocationEntry("United Kingdom", "GBP", 0.33, 55.0, 0.60),
    "Cambridge, UK": LocationEntry("United Kingdom", "GBP", 0.33, 65.0, 0.70),
    "Bristol, UK": LocationEntry("United Kingdom", "GBP", 0.33, 55.0, 0.60),
    "Birmingham, UK": LocationEntry("United Kingdom", "GBP", 0.33, 50.0, 0.55),

    # ── Ireland ─────────────────────────────────────────────────────────
    "Dublin, Ireland": LocationEntry("Ireland", "EUR", 0.32, 75.0, 0.65),
    "Cork, Ireland": LocationEntry("Ireland", "EUR", 0.32, 55.0, 0.55),

    # ── Germany ─────────────────────────────────────────────────────────
    "Berlin, Germany": LocationEntry("Germany", "EUR", 0.42, 65.0, 0.60),
    "Munich, Germany": LocationEntry("Germany", "EUR", 0.35, 70.0, 0.65),
    "Frankfurt, Germany": LocationEntry("Germany", "EUR", 0.35, 65.0, 0.60),
    "Hamburg, Germany": LocationEntry("Germany", "EUR", 0.35, 62.0, 0.58),

    # ── Netherlands ─────────────────────────────────────────────────────
    "Amsterdam, Netherlands": LocationEntry("Netherlands", "EUR", 0.40, 78.0, 0.70),
    "Eindhoven, Netherlands": LocationEntry("Netherlands", "EUR", 0.40, 55.0, 0.55),
    "Rotterdam, Netherlands": LocationEntry("Netherlands", "EUR", 0.40, 58.0, 0.58),

    # ── France ──────────────────────────────────────────────────────────
    "Paris, France": LocationEntry("France", "EUR", 0.40, 80.0, 0.68),
    "Lyon, France": LocationEntry("France", "EUR", 0.40, 55.0, 0.55),

    # ── Spain ───────────────────────────────────────────────────────────
    "Barcelona, Spain": LocationEntry("Spain", "EUR", 0.37, 60.0, 0.45),
    "Madrid, Spain": LocationEntry("Spain", "EUR", 0.37, 62.0, 0.45),

    # ── Italy ───────────────────────────────────────────────────────────
    "Milan, Italy": LocationEntry("Italy", "EUR", 0.38, 68.0, 0.50),
    "Rome, Italy": LocationEntry("Italy", "EUR", 0.38, 65.0, 0.48),

    # ── Nordics ─────────────────────────────────────────────────────────
    "Stockholm, Sweden": LocationEntry("Sweden", "SEK", 0.35, 75.0, 0.60),
    "Gothenburg, Sweden": LocationEntry("Sweden", "SEK", 0.35, 60.0, 0.52),
    "Copenhagen, Denmark": LocationEntry("Denmark", "DKK", 0.35, 85.0, 0.60),
    "Aarhus, Denmark": LocationEntry("Denmark", "DKK", 0.35, 60.0, 0.52),
    "Oslo, Norway": LocationEntry("Norway", "NOK", 0.34, 90.0, 0.60),
    "Bergen, Norway": LocationEntry("Norway", "NOK", 0.34, 65.0, 0.52),
    "Helsinki, Finland": LocationEntry("Finland", "EUR", 0.35, 70.0, 0.55),

    # ── Switzerland ─────────────────────────────────────────────────────
    "Zurich, Switzerland": LocationEntry("Switzerland", "CHF", 0.25, 120.0, 1.10),
    "Geneva, Switzerland": LocationEntry("Switzerland", "CHF", 0.28, 125.0, 1.05),
    "Lausanne, Switzerland": LocationEntry("Switzerland", "CHF", 0.26, 115.0, 1.0),

    # ── Austria / CEE ───────────────────────────────────────────────────
    "Vienna, Austria": LocationEntry("Austria", "EUR", 0.38, 65.0, 0.55),
    "Prague, Czech Republic": LocationEntry("Czech Republic", "CZK", 0.23, 45.0, 0.40),
    "Warsaw, Poland": LocationEntry("Poland", "PLN", 0.32, 40.0, 0.35),
    "Budapest, Hungary": LocationEntry("Hungary", "EUR", 0.30, 38.0, 0.35),

    # ── Portugal ────────────────────────────────────────────────────────
    "Lisbon, Portugal": LocationEntry("Portugal", "EUR", 0.35, 50.0, 0.40),
    "Porto, Portugal": LocationEntry("Portugal", "EUR", 0.35, 42.0, 0.38),

    # ── Japan ───────────────────────────────────────────────────────────
    "Tokyo, Japan": LocationEntry("Japan", "JPY", 0.33, 85.0, 0.70),
    "Osaka, Japan": LocationEntry("Japan", "JPY", 0.33, 70.0, 0.60),

    # ── Singapore / Hong Kong ───────────────────────────────────────────
    "Singapore": LocationEntry("Singapore", "SGD", 0.15, 95.0, 0.85),
    "Hong Kong": LocationEntry("Hong Kong", "HKD", 0.15, 110.0, 0.70),

    # ── South Korea ─────────────────────────────────────────────────────
    "Seoul, South Korea": LocationEntry("South Korea", "KRW", 0.33, 70.0, 0.55),
    "Busan, South Korea": LocationEntry("South Korea", "KRW", 0.33, 50.0, 0.45),

    # ── Taiwan ──────────────────────────────────────────────────────────
    "Taipei, Taiwan": LocationEntry("Taiwan", "TWD", 0.20, 50.0, 0.40),

    # ── China ───────────────────────────────────────────────────────────
    "Shanghai, China": LocationEntry("China", "CNY", 0.35, 55.0, 0.45),
    "Beijing, China": LocationEntry("China", "CNY", 0.35, 60.0, 0.45),
    "Shenzhen, China": LocationEntry("China", "CNY", 0.35, 58.0, 0.45),

    # ── Australia ───────────────────────────────────────────────────────
    "Sydney, Australia": LocationEntry("Australia", "AUD", 0.37, 80.0, 0.75),
    "Melbourne, Australia": LocationEntry("Australia", "AUD", 0.37, 75.0, 0.70),
    "Brisbane, Australia": LocationEntry("Australia", "AUD", 0.37, 60.0, 0.60),
    "Perth, Australia": LocationEntry("Australia", "AUD", 0.37, 62.0, 0.60),

    # ── New Zealand ─────────────────────────────────────────────────────
    "Auckland, New Zealand": LocationEntry("New Zealand", "NZD", 0.33, 55.0, 0.55),
    "Wellington, New Zealand": LocationEntry("New Zealand", "NZD", 0.33, 52.0, 0.50),
    "Christchurch, New Zealand": LocationEntry("New Zealand", "NZD", 0.33, 45.0, 0.45),

    # ── Canada ──────────────────────────────────────────────────────────
    "Toronto, Canada": LocationEntry("Canada", "CAD", 0.35, 65.0, 0.65, ["toronto, on"]),
    "Vancouver, Canada": LocationEntry("Canada", "CAD", 0.35, 70.0, 0.68, ["vancouver, bc"]),
    "Montreal, Canada": LocationEntry("Canada", "CAD", 0.33, 55.0, 0.65, ["montreal, qc"]),
    "Calgary, Canada": LocationEntry("Canada", "CAD", 0.33, 55.0, 0.60, ["calgary, ab"]),
    "Waterloo, Canada": LocationEntry("Canada", "CAD", 0.33, 48.0, 0.55, ["waterloo, on"]),
    "Ottawa, Canada": LocationEntry("Canada", "CAD", 0.33, 50.0, 0.55, ["ottawa, on"]),

    # ── Israel ──────────────────────────────────────────────────────────
    "Tel Aviv, Israel": LocationEntry("Israel", "ILS", 0.35, 72.0, 0.75),
    "Haifa, Israel": LocationEntry("Israel", "ILS", 0.35, 50.0, 0.55),

    # ── India ───────────────────────────────────────────────────────────
    "Bangalore, India": LocationEntry(
        "India", "INR", 0.312, 25.0, 0.25, ["bengaluru", "blr", "bengaluru, india"]
    ),
    "Mumbai, India": LocationEntry("India", "INR", 0.312, 35.0, 0.30),
    "Hyderabad, India": LocationEntry("India", "INR", 0.312, 22.0, 0.28, ["hyd"]),
    "Delhi, India": LocationEntry("India", "INR", 0.312, 30.0, 0.28, ["new delhi"]),
    "Pune, India": LocationEntry("India", "INR", 0.312, 20.0, 0.28),
    "Chennai, India": LocationEntry("India", "INR", 0.312, 22.0, 0.28),
    "Kolkata, India": LocationEntry("India", "INR", 0.312, 20.0, 0.25),
    "Gurgaon, India": LocationEntry("India", "INR", 0.312, 28.0, 0.30, ["gurugram"]),
    "Noida, India": LocationEntry("India", "INR", 0.312, 22.0, 0.28),

    # ── UAE / Middle East ───────────────────────────────────────────────
    "Dubai, UAE": LocationEntry("UAE", "AED", 0.0, 65.0, 0.70),
    "Abu Dhabi, UAE": LocationEntry("UAE", "AED", 0.0, 62.0, 0.70),
    "Sharjah, UAE": LocationEntry("UAE", "AED", 0.0, 45.0, 0.55),
    "Riyadh, Saudi Arabia": LocationEntry("Saudi Arabia", "SAR", 0.0, 40.0, 0.55),
    "Jeddah, Saudi Arabia": LocationEntry("Saudi Arabia", "SAR", 0.0, 38.0, 0.50),
    "Doha, Qatar": LocationEntry("Qatar", "QAR", 0.0, 58.0, 0.60),

    # ── Southeast Asia ──────────────────────────────────────────────────
    "Jakarta, Indonesia": LocationEntry("Indonesia", "IDR", 0.30, 32.0, 0.25),
    "Bangkok, Thailand": LocationEntry("Thailand", "THB", 0.25, 35.0, 0.28),
    "Ho Chi Minh City, Vietnam": LocationEntry("Vietnam", "VND", 0.25, 28.0, 0.22, ["ho chi minh"]),
    "Hanoi, Vietnam": LocationEntry("Vietnam", "VND", 0.25, 24.0, 0.20),
    "Kuala Lumpur, Malaysia": LocationEntry("Malaysia", "MYR", 0.25, 30.0, 0.30),
    "Manila, Philippines": LocationEntry("Philippines", "PHP", 0.25, 25.0, 0.22),

    # ── Latin America ───────────────────────────────────────────────────
    "Mexico City, Mexico": LocationEntry("Mexico", "MXN", 0.30, 30.0, 0.30),
    "Guadalajara, Mexico": LocationEntry("Mexico", "MXN", 0.30, 25.0, 0.25),
    "Monterrey, Mexico": LocationEntry("Mexico", "MXN", 0.30, 28.0, 0.28),
    "Sao Paulo, Brazil": LocationEntry("Brazil", "BRL", 0.275, 35.0, 0.35, ["são paulo", "são paulo, brazil"]),
    "Rio de Janeiro, Brazil": LocationEntry("Brazil", "BRL", 0.275, 32.0, 0.30),
    "Buenos Aires, Argentina": LocationEntry("Argentina", "USD", 0.30, 25.0, 0.25),
    "Santiago, Chile": LocationEntry("Chile", "USD", 0.30, 30.0, 0.30),
    "Bogota, Colombia": LocationEntry("Colombia", "USD", 0.30, 25.0, 0.22, ["bogotá", "bogotá, colombia"]),
    "Lima, Peru": LocationEntry("Peru", "USD", 0.30, 22.0, 0.20),

    # ── Africa ──────────────────────────────────────────────────────────
    "Cape Town, South Africa": LocationEntry("South Africa", "USD", 0.30, 28.0, 0.25),
    "Johannesburg, South Africa": LocationEntry("South Africa", "USD", 0.30, 30.0, 0.28),
    "Cairo, Egypt": LocationEntry("Egypt", "USD", 0.25, 18.0, 0.18),

    # ── Other ───────────────────────────────────────────────────────────
    "Istanbul, Turkey": LocationEntry("Turkey", "USD", 0.30, 30.0, 0.28),
    "Moscow, Russia": LocationEntry("Russia", "USD", 0.30, 35.0, 0.30),
    "Brussels, Belgium": LocationEntry("Belgium", "EUR", 0.40, 65.0, 0.55),

    # ── Remote ──────────────────────────────────────────────────────────
    "Remote": LocationEntry("", "USD", _DEFAULT_TAX_RATE, 50.0, 0.85),
}

# ── Alias Index ─────────────────────────────────────────────────────────
# Built once at import time. Maps lowercase alias/name → canonical key.
_ALIAS_INDEX: Dict[str, str] = {}


def _build_alias_index() -> None:
    for canonical, entry in LOCATION_REGISTRY.items():
        lower_canonical = canonical.lower()
        _ALIAS_INDEX[lower_canonical] = canonical
        # bare city name (first part before comma)
        city_part = canonical.split(",")[0].strip().lower()
        if city_part and city_part not in _ALIAS_INDEX:
            _ALIAS_INDEX[city_part] = canonical
        for alias in entry.aliases:
            alias_lower = alias.strip().lower()
            if alias_lower:
                _ALIAS_INDEX[alias_lower] = canonical


_build_alias_index()


# ── Country/Region Suffix Fallback Tables ───────────────────────────────
# Used when a location like "SomeCity, India" isn't in the registry but the
# suffix "india" can still infer currency/country.

_COUNTRY_SUFFIX_TO_CURRENCY: Dict[str, str] = {
    "india": "INR", "in": "INR",
    "uae": "AED", "united arab emirates": "AED",
    "uk": "GBP", "united kingdom": "GBP",
    "usa": "USD", "us": "USD", "united states": "USD", "america": "USD",
    "france": "EUR", "germany": "EUR", "netherlands": "EUR", "ireland": "EUR",
    "spain": "EUR", "italy": "EUR", "belgium": "EUR", "austria": "EUR",
    "portugal": "EUR", "finland": "EUR", "greece": "EUR",
    "poland": "PLN", "czech republic": "CZK", "czechia": "CZK",
    "sweden": "SEK", "norway": "NOK", "denmark": "DKK",
    "switzerland": "CHF", "israel": "ILS",
    "japan": "JPY", "south korea": "KRW", "korea": "KRW",
    "taiwan": "TWD", "china": "CNY",
    "australia": "AUD", "new zealand": "NZD",
    "canada": "CAD", "ca": "CAD",
    "mexico": "MXN", "brazil": "BRL",
    "saudi arabia": "SAR", "qatar": "QAR",
    "thailand": "THB", "vietnam": "VND",
    "indonesia": "IDR", "malaysia": "MYR", "philippines": "PHP",
    "singapore": "SGD", "hong kong": "HKD",
    # US state codes that might appear as suffixes
    "mi": "USD", "tn": "USD", "ut": "USD", "oh": "USD", "mo": "USD", "nv": "USD",
}

_US_STATE_CODES = [
    "al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", "hi", "id", "il", "in", "ia",
    "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", "nj",
    "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "vt",
    "va", "wa", "wv", "wi", "wy", "dc",
]
_CA_PROVINCE_CODES = ["ab", "bc", "mb", "nb", "nl", "ns", "nt", "nu", "on", "pe", "qc", "sk", "yt"]

_COUNTRY_SUFFIX_TO_COUNTRY: Dict[str, str] = {
    "india": "India", "uae": "UAE", "united arab emirates": "UAE",
    "united kingdom": "United Kingdom", "uk": "United Kingdom", "great britain": "United Kingdom",
    "usa": "United States", "us": "United States", "united states": "United States",
    "united states of america": "United States", "america": "United States",
    "germany": "Germany", "france": "France", "spain": "Spain",
    "sweden": "Sweden", "norway": "Norway", "denmark": "Denmark",
    "portugal": "Portugal", "netherlands": "Netherlands", "holland": "Netherlands",
    "ireland": "Ireland", "switzerland": "Switzerland",
    "singapore": "Singapore", "japan": "Japan",
    "south korea": "South Korea", "korea": "South Korea",
    "saudi arabia": "Saudi Arabia", "qatar": "Qatar", "israel": "Israel",
    "australia": "Australia", "new zealand": "New Zealand", "canada": "Canada",
    "mexico": "Mexico", "brazil": "Brazil", "thailand": "Thailand",
    "vietnam": "Vietnam", "indonesia": "Indonesia", "malaysia": "Malaysia",
    "philippines": "Philippines", "china": "China", "taiwan": "Taiwan",
    "hong kong": "Hong Kong",
}
for _code in _US_STATE_CODES:
    _COUNTRY_SUFFIX_TO_COUNTRY.setdefault(_code, "United States")
for _code in _CA_PROVINCE_CODES:
    _COUNTRY_SUFFIX_TO_COUNTRY.setdefault(_code, "Canada")


# ── Public Helper Functions ─────────────────────────────────────────────

def normalize_location(location: str) -> str:
    """Resolve aliases/bare names/abbreviations to canonical registry key."""
    if not location or not str(location).strip():
        return ""
    cleaned = " ".join(str(location).strip().split())
    lower = cleaned.lower()
    if lower in _ALIAS_INDEX:
        return _ALIAS_INDEX[lower]
    return cleaned


def get_tax_rate(location: str) -> float:
    canonical = normalize_location(location)
    entry = LOCATION_REGISTRY.get(canonical)
    if entry:
        return entry.tax_rate
    return _DEFAULT_TAX_RATE


def get_col_index(location: str) -> float:
    canonical = normalize_location(location)
    if canonical == "Remote":
        return 50.0
    entry = LOCATION_REGISTRY.get(canonical)
    if entry:
        return entry.col_index
    return _DEFAULT_COL_INDEX


def get_salary_multiplier(location: str) -> float:
    canonical = normalize_location(location)
    entry = LOCATION_REGISTRY.get(canonical)
    if entry:
        return entry.salary_multiplier
    return _DEFAULT_SALARY_MULTIPLIER


def infer_currency(location: str) -> str:
    if not location or not str(location).strip():
        return "USD"
    canonical = normalize_location(location)
    entry = LOCATION_REGISTRY.get(canonical)
    if entry:
        return entry.currency
    normalized = " ".join(str(location).strip().split()).lower()
    if normalized in _COUNTRY_SUFFIX_TO_CURRENCY:
        return _COUNTRY_SUFFIX_TO_CURRENCY[normalized]
    parts = [p.strip() for p in normalized.split(",") if p.strip()]
    for segment in reversed(parts):
        if segment in _COUNTRY_SUFFIX_TO_CURRENCY:
            return _COUNTRY_SUFFIX_TO_CURRENCY[segment]
    return "USD"


def infer_country(location: str) -> Optional[str]:
    if not location or not str(location).strip():
        return None
    canonical = normalize_location(location)
    if canonical == "Remote":
        return None
    entry = LOCATION_REGISTRY.get(canonical)
    if entry and entry.country:
        return entry.country
    normalized = " ".join(str(location).strip().split()).lower()
    if normalized in _COUNTRY_SUFFIX_TO_COUNTRY:
        return _COUNTRY_SUFFIX_TO_COUNTRY[normalized]
    parts = [p.strip() for p in normalized.split(",") if p.strip()]
    for segment in reversed(parts):
        if segment in _COUNTRY_SUFFIX_TO_COUNTRY:
            return _COUNTRY_SUFFIX_TO_COUNTRY[segment]
    return None


def get_all_locations() -> List[str]:
    """Return sorted list of all canonical location keys (excluding 'Remote')."""
    return sorted(k for k in LOCATION_REGISTRY if k != "Remote")
