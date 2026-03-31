"""
Country profiles, city → country mapping, and relocation comparison helpers.
"""

from __future__ import annotations

_US_STATE_CODES: tuple[str, ...] = (
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
)

_CA_PROVINCE_CODES: tuple[str, ...] = (
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
)

# Canonical country name → profile (currency aligns with utils.currency where applicable).
COUNTRY_PROFILES: dict[str, dict] = {
    "United States": {
        "currency": "USD",
        "tax_regime": "Federal + state income tax; FICA; no VAT",
        "max_marginal_rate": 0.50,
        "major_tech_hubs": [
            "San Francisco Bay Area",
            "Seattle",
            "New York City",
            "Austin",
            "Boston",
        ],
        "social_security": "FICA (OASDI + Medicare); wage caps on Social Security",
        "healthcare": "Employer-sponsored insurance common; ACA marketplace; Medicare at 65",
        "visa_for_work": "H-1B, L-1, O-1, TN, Green Card paths; PERM labor certification",
        "retirement_system": "401(k)/403(b), IRAs, Social Security benefits",
        "quality_of_life_index": 72,
        "safety_index": 68,
        "typical_benefits": [
            "Medical, dental, vision",
            "401(k) match",
            "PTO and parental leave",
        ],
        "considerations": [
            "High healthcare complexity and cost without employer coverage",
            "State tax variation",
            "Immigration caps and lottery for H-1B",
        ],
    },
    "India": {
        "currency": "INR",
        "tax_regime": "New / old regime options; surcharge on high income",
        "max_marginal_rate": 0.42,
        "major_tech_hubs": [
            "Bengaluru",
            "Hyderabad",
            "Pune",
            "Chennai",
            "NCR",
        ],
        "social_security": "EPF, EPS, ESI where applicable",
        "healthcare": "Mixed public/private; employer group cover common in tech",
        "visa_for_work": "Domestic; expats use employment / business visas",
        "retirement_system": "EPF, NPS, employer superannuation",
        "quality_of_life_index": 58,
        "safety_index": 62,
        "typical_benefits": [
            "Health insurance",
            "PF contribution",
            "Gratuity",
        ],
        "considerations": [
            "Traffic and air quality in major hubs",
            "Monsoon and heat in some regions",
            "Rapid COL change across cities",
        ],
    },
    "UAE": {
        "currency": "AED",
        "tax_regime": "No personal income tax; corporate tax for businesses",
        "max_marginal_rate": 0.0,
        "major_tech_hubs": ["Dubai", "Abu Dhabi"],
        "social_security": "GPSSA for nationals; limited mandatory for expats",
        "healthcare": "Mandatory health insurance; private providers dominant",
        "visa_for_work": "Employment visa / work permit sponsored by employer",
        "retirement_system": "End-of-service gratuity; private savings for expats",
        "quality_of_life_index": 78,
        "safety_index": 85,
        "typical_benefits": [
            "Health insurance",
            "Housing allowance",
            "Annual flight home",
        ],
        "considerations": [
            "Heat in summer",
            "Sponsorship tied to employer",
            "Cultural and legal differences vs Western norms",
        ],
    },
    "United Kingdom": {
        "currency": "GBP",
        "tax_regime": "Income tax + National Insurance; progressive bands",
        "max_marginal_rate": 0.47,
        "major_tech_hubs": ["London", "Manchester", "Edinburgh", "Cambridge"],
        "social_security": "National Insurance contributions",
        "healthcare": "NHS residency-based; private supplemental common",
        "visa_for_work": "Skilled Worker visa; Global Talent; ICT routes",
        "retirement_system": "Workplace pensions, auto-enrolment, State Pension",
        "quality_of_life_index": 76,
        "safety_index": 72,
        "typical_benefits": [
            "Pension auto-enrolment",
            "Private medical cash plan",
            "Cycle to work",
        ],
        "considerations": [
            "High London COL",
            "Right-to-work tied to visa",
            "Weather and daylight winter",
        ],
    },
    "Germany": {
        "currency": "EUR",
        "tax_regime": "Progressive Einkommensteuer; Solidaritätszuschlag; church tax optional",
        "max_marginal_rate": 0.45,
        "major_tech_hubs": ["Berlin", "Munich", "Hamburg", "Frankfurt"],
        "social_security": "Health, pension, unemployment, care — shared employer/employee",
        "healthcare": "Statutory (GKV) or private (PKV) systems",
        "visa_for_work": "EU Blue Card; skilled worker residence permit",
        "retirement_system": "Public pension (DRV) plus company and private plans",
        "quality_of_life_index": 80,
        "safety_index": 78,
        "typical_benefits": [
            "30+ vacation days norm",
            "Employer pension (bAV)",
            "Public transit subsidy",
        ],
        "considerations": [
            "German language for daily life outside tech bubbles",
            "Registration (Anmeldung) bureaucracy",
            "Tax class (Steuerklasse) affects net pay",
        ],
    },
    "Singapore": {
        "currency": "SGD",
        "tax_regime": "Territorial; progressive resident rates; no CGT on capital generally",
        "max_marginal_rate": 0.24,
        "major_tech_hubs": ["Singapore"],
        "social_security": "CPF for PRs and citizens; limited for EP holders",
        "healthcare": "Medisave/Medishield; employer medical common",
        "visa_for_work": "Employment Pass, S Pass; COMPASS framework",
        "retirement_system": "CPF for locals; SRS voluntary; private for expats",
        "quality_of_life_index": 82,
        "safety_index": 88,
        "typical_benefits": [
            "Medical and dental",
            "Relocation allowance",
            "CPF for eligible employees",
        ],
        "considerations": [
            "High rent",
            "EP criteria changes",
            "Humidity",
        ],
    },
    "Canada": {
        "currency": "CAD",
        "tax_regime": "Federal + provincial income tax; progressive",
        "max_marginal_rate": 0.54,
        "major_tech_hubs": ["Toronto", "Vancouver", "Montreal", "Calgary", "Waterloo"],
        "social_security": "CPP/QPP, EI contributions",
        "healthcare": "Provincial medicare; supplemental private for drugs/dental",
        "visa_for_work": "Work permit; Express Entry PR paths",
        "retirement_system": "CPP/OAS, RRSP, TFSA, workplace pensions",
        "quality_of_life_index": 79,
        "safety_index": 80,
        "typical_benefits": [
            "Health benefits",
            "RRSP matching",
            "Parental leave top-up",
        ],
        "considerations": [
            "Provincial tax variation",
            "Housing affordability in Toronto/Vancouver",
            "Winter climate",
        ],
    },
    "Australia": {
        "currency": "AUD",
        "tax_regime": "Federal income tax + Medicare levy; no state income tax",
        "max_marginal_rate": 0.47,
        "major_tech_hubs": ["Sydney", "Melbourne", "Brisbane", "Perth"],
        "social_security": "Superannuation guarantee; no US-style Social Security",
        "healthcare": "Medicare + private health common",
        "visa_for_work": "TSS 482; skilled PR (189/190/491)",
        "retirement_system": "Superannuation (employer contributions)",
        "quality_of_life_index": 81,
        "safety_index": 76,
        "typical_benefits": [
            "Superannuation above minimum",
            "Income protection",
            "Flexible work",
        ],
        "considerations": [
            "Distance from other regions",
            "Housing costs in Sydney",
            "Wildfire/flood risk by region",
        ],
    },
    "Japan": {
        "currency": "JPY",
        "tax_regime": "National + local inhabitant tax; progressive",
        "max_marginal_rate": 0.55,
        "major_tech_hubs": ["Tokyo", "Osaka", "Fukuoka"],
        "social_security": "Health, pension, employment insurance",
        "healthcare": "National Health Insurance / SHAKAI HOKEN",
        "visa_for_work": "Engineer/Specialist in Humanities; highly skilled visa",
        "retirement_system": "National pension, employee pension, iDeCo",
        "quality_of_life_index": 83,
        "safety_index": 90,
        "typical_benefits": [
            "Commuter pass",
            "Health insurance society",
            "Bonus payments",
        ],
        "considerations": [
            "Language barrier",
            "Long hours culture in some firms",
            "Earthquake preparedness",
        ],
    },
    "Netherlands": {
        "currency": "EUR",
        "tax_regime": "Progressive box system; 30% ruling for eligible expats",
        "max_marginal_rate": 0.49,
        "major_tech_hubs": ["Amsterdam", "Eindhoven", "Rotterdam"],
        "social_security": "Employee insurances (WW, WIA, Zvw)",
        "healthcare": "Mandatory basic insurance (zorgverzekering)",
        "visa_for_work": "Highly skilled migrant; EU Blue Card",
        "retirement_system": "State AOW, workplace pension (second pillar)",
        "quality_of_life_index": 84,
        "safety_index": 79,
        "typical_benefits": [
            "13th month",
            "Pension",
            "Travel allowance",
        ],
        "considerations": [
            "Housing shortage in Amsterdam",
            "30% ruling eligibility changes",
            "Bicycle-centric logistics",
        ],
    },
    "Switzerland": {
        "currency": "CHF",
        "tax_regime": "Federal + cantonal + municipal; varies by canton",
        "max_marginal_rate": 0.42,
        "major_tech_hubs": ["Zurich", "Geneva", "Lausanne"],
        "social_security": "AHV/IV, unemployment, occupational pension (BVG)",
        "healthcare": "Mandatory basic insurance (KVG/LAMal)",
        "visa_for_work": "L / B permits; quotas for non-EU",
        "retirement_system": "Pillar 1–3; strong occupational pensions",
        "quality_of_life_index": 88,
        "safety_index": 86,
        "typical_benefits": [
            "Above-legal pension contributions",
            "Transport discounts",
            "Bonus",
        ],
        "considerations": [
            "Very high COL",
            "Language (DE/FR/IT) by region",
            "Non-EU permit quotas",
        ],
    },
    "Ireland": {
        "currency": "EUR",
        "tax_regime": "USC + PAYE; progressive bands",
        "max_marginal_rate": 0.52,
        "major_tech_hubs": ["Dublin", "Cork", "Galway"],
        "social_security": "PRSI classes",
        "healthcare": "Public HSE with private supplemental",
        "visa_for_work": "Critical Skills Employment Permit; EU free movement",
        "retirement_system": "State pension, occupational DC schemes, PRSA",
        "quality_of_life_index": 81,
        "safety_index": 74,
        "typical_benefits": [
            "Health insurance",
            "Pension",
            "Stock purchase plans",
        ],
        "considerations": [
            "Dublin housing shortage",
            "Weather",
            "Brexit-related trade context for UK commuters",
        ],
    },
    "South Korea": {
        "currency": "KRW",
        "tax_regime": "National + local income tax; progressive",
        "max_marginal_rate": 0.46,
        "major_tech_hubs": ["Seoul", "Pangyo", "Busan"],
        "social_security": "NPS, NHIS, employment insurance",
        "healthcare": "NHI single-payer with low copays",
        "visa_for_work": "E-7 professional; F-2 points; employer sponsorship",
        "retirement_system": "NPS, severance (retirement allowance), IRP",
        "quality_of_life_index": 77,
        "safety_index": 82,
        "typical_benefits": [
            "Meal allowance",
            "Shuttle",
            "Severance accrual",
        ],
        "considerations": [
            "Language for non-tech life",
            "Air quality episodes",
            "Work culture variance by company",
        ],
    },
    "Saudi Arabia": {
        "currency": "SAR",
        "tax_regime": "No personal income tax for individuals",
        "max_marginal_rate": 0.0,
        "major_tech_hubs": ["Riyadh", "Jeddah", "Dhahran"],
        "social_security": "GOSI for eligible workers",
        "healthcare": "Employer-provided insurance mandatory",
        "visa_for_work": "Iqama via employer sponsorship",
        "retirement_system": "End-of-service benefit; private savings",
        "quality_of_life_index": 70,
        "safety_index": 78,
        "typical_benefits": [
            "Housing or allowance",
            "Annual leave tickets",
            "Education allowance",
        ],
        "considerations": [
            "Climate",
            "Cultural and legal framework",
            "Sponsorship dependence",
        ],
    },
    "Qatar": {
        "currency": "QAR",
        "tax_regime": "No personal income tax",
        "max_marginal_rate": 0.0,
        "major_tech_hubs": ["Doha"],
        "social_security": "Limited mandatory social for nationals",
        "healthcare": "Employer-sponsored insurance",
        "visa_for_work": "Work residence permit via employer",
        "retirement_system": "End-of-service gratuity; private savings",
        "quality_of_life_index": 79,
        "safety_index": 84,
        "typical_benefits": [
            "Family housing",
            "Annual flight",
            "Education support",
        ],
        "considerations": [
            "Summer heat",
            "Kafala-style sponsorship legacy reforms ongoing",
            "Small expat bubble",
        ],
    },
    "Israel": {
        "currency": "ILS",
        "tax_regime": "Progressive income tax; national insurance",
        "max_marginal_rate": 0.50,
        "major_tech_hubs": ["Tel Aviv", "Herzliya", "Jerusalem", "Haifa"],
        "social_security": "Bituach Leumi (NI)",
        "healthcare": "Mandatory health funds (kupot holim)",
        "visa_for_work": "B-1 work visa; expert routes; tech visa categories",
        "retirement_system": "Pension funds, severance (pitzuim), continuing education funds",
        "quality_of_life_index": 75,
        "safety_index": 65,
        "typical_benefits": [
            "Stock options RSUs",
            "Keren hishtalmut",
            "Meal cards",
        ],
        "considerations": [
            "Security situation awareness",
            "High VAT and COL",
            "Friday–Saturday weekend",
        ],
    },
    "France": {
        "currency": "EUR",
        "tax_regime": "Progressive IR; CSG/CRDS on earned income",
        "max_marginal_rate": 0.45,
        "major_tech_hubs": ["Paris", "Lyon", "Toulouse"],
        "social_security": "URSSAF cotisations; unemployment, health, retirement slices",
        "healthcare": "Assurance Maladie with mutuelle top-up",
        "visa_for_work": "Passeport Talent; salarié visa",
        "retirement_system": "Régimes de base et complémentaires, PER",
        "quality_of_life_index": 82,
        "safety_index": 70,
        "typical_benefits": [
            "Restaurant tickets",
            "Complementary health (mutuelle)",
            "RTT days",
        ],
        "considerations": [
            "Labor code rigidity vs US",
            "Paris housing costs",
            "French language expectations",
        ],
    },
    "Spain": {
        "currency": "EUR",
        "tax_regime": "IRPF national + regional; Beckham Law option for eligible inbound",
        "max_marginal_rate": 0.47,
        "major_tech_hubs": ["Barcelona", "Madrid", "Valencia", "Malaga"],
        "social_security": "TGSS contributions",
        "healthcare": "NHS-style SNS; private supplemental",
        "visa_for_work": "EU Blue Card; highly qualified permit",
        "retirement_system": "Public pension system, occupational plans, private pension",
        "quality_of_life_index": 80,
        "safety_index": 73,
        "typical_benefits": [
            "Flexible summer hours",
            "Health insurance",
            "Meal allowance",
        ],
        "considerations": [
            "Regional language (Catalan, etc.) in some hubs",
            "Youth unemployment context",
            "Slower bureaucracy",
        ],
    },
    "Sweden": {
        "currency": "SEK",
        "tax_regime": "Municipal + national tax; high overall wedge",
        "max_marginal_rate": 0.55,
        "major_tech_hubs": ["Stockholm", "Gothenburg", "Malmö"],
        "social_security": "Employer payroll taxes finance benefits",
        "healthcare": "Tax-funded universal care",
        "visa_for_work": "Work permit; EU free movement",
        "retirement_system": "Allmän pension (inkomstpension + premiepension), tjänstepension",
        "quality_of_life_index": 86,
        "safety_index": 81,
        "typical_benefits": [
            "Parental leave culture",
            "Wellness stipend",
            "Occupational pension",
        ],
        "considerations": [
            "Dark winters in north",
            "Housing queue in Stockholm",
            "High taxes fund services",
        ],
    },
    "Norway": {
        "currency": "NOK",
        "tax_regime": "Progressive bracket tax + social contributions",
        "max_marginal_rate": 0.47,
        "major_tech_hubs": ["Oslo", "Bergen", "Trondheim"],
        "social_security": "National Insurance (trygdeavgift)",
        "healthcare": "Publicly funded",
        "visa_for_work": "Skilled worker residence; EU/EEA free movement",
        "retirement_system": "Folketrygden + occupational pension",
        "quality_of_life_index": 87,
        "safety_index": 88,
        "typical_benefits": [
            "Pension",
            "Training budget",
            "Extra vacation",
        ],
        "considerations": [
            "High COL",
            "Weather",
            "Language outside tech",
        ],
    },
    "Denmark": {
        "currency": "DKK",
        "tax_regime": "High income and municipal taxes; church tax optional",
        "max_marginal_rate": 0.56,
        "major_tech_hubs": ["Copenhagen", "Aarhus", "Odense"],
        "social_security": "ATP, AM-bidrag, labor market contributions",
        "healthcare": "Tax-funded universal",
        "visa_for_work": "Pay Limit Scheme; Fast Track; EU free movement",
        "retirement_system": "Folkepension, ATP, private pensions",
        "quality_of_life_index": 85,
        "safety_index": 83,
        "typical_benefits": [
            "Six weeks vacation norm",
            "Pension",
            "Lunch scheme",
        ],
        "considerations": [
            "Weather and daylight",
            "Housing in Copenhagen",
            "Danish language for integration",
        ],
    },
    "Portugal": {
        "currency": "EUR",
        "tax_regime": "Progressive IRS; NHR regime phased out for new entrants",
        "max_marginal_rate": 0.48,
        "major_tech_hubs": ["Lisbon", "Porto", "Braga"],
        "social_security": "Segurança Social contributions",
        "healthcare": "SNS with private supplemental",
        "visa_for_work": "D-type visa + residence; EU Blue Card",
        "retirement_system": "Public pension pillars, PPR private retirement",
        "quality_of_life_index": 78,
        "safety_index": 77,
        "typical_benefits": [
            "Health insurance",
            "Remote work flexibility",
            "Meal card",
        ],
        "considerations": [
            "Lower salaries vs Northern Europe",
            "Rising Lisbon rents",
            "Portuguese language for services",
        ],
    },
    "New Zealand": {
        "currency": "NZD",
        "tax_regime": "Progressive PAYE; ACC levy",
        "max_marginal_rate": 0.39,
        "major_tech_hubs": ["Auckland", "Wellington", "Christchurch"],
        "social_security": "No separate social security tax; ACC covers injuries",
        "healthcare": "Public health funded by taxes; private optional",
        "visa_for_work": "Accredited Employer Work Visa; Skilled Migrant paths",
        "retirement_system": "KiwiSaver with employer contributions",
        "quality_of_life_index": 83,
        "safety_index": 79,
        "typical_benefits": [
            "KiwiSaver match",
            "Wellness",
            "Additional leave",
        ],
        "considerations": [
            "Distance / time zones",
            "Auckland housing costs",
            "Quake risk awareness",
        ],
    },
}

from utils.location_registry import (
    infer_country as _registry_infer_country,
    LOCATION_REGISTRY,
    _COUNTRY_SUFFIX_TO_COUNTRY,
)

# Backward-compatible view
_LOCATION_TO_COUNTRY = {k.lower(): e.country for k, e in LOCATION_REGISTRY.items() if e.country}


def infer_country(location: str) -> str | None:
    return _registry_infer_country(location)


def get_relocation_factors(from_country: str, to_country: str) -> dict | None:
    if from_country == to_country:
        return None
    origin = COUNTRY_PROFILES.get(from_country)
    dest = COUNTRY_PROFILES.get(to_country)
    if origin is None or dest is None:
        return None
    qol_delta = int(dest["quality_of_life_index"]) - int(origin["quality_of_life_index"])
    safety_delta = int(dest["safety_index"]) - int(origin["safety_index"])
    return {
        "from_country": from_country,
        "to_country": to_country,
        "visa_notes": (
            f"Relocation from {from_country} to {to_country}: verify work authorization, "
            "sponsorship, and any cooling-off or quota rules before accepting an offer."
        ),
        "tax_delta_description": (
            f"Tax context shifts from {origin['tax_regime']} (top marginal ~"
            f"{origin['max_marginal_rate']:.0%}) to {dest['tax_regime']} (top marginal ~"
            f"{dest['max_marginal_rate']:.0%}). Consult a cross-border tax advisor."
        ),
        "from_tax_regime": origin["tax_regime"],
        "to_tax_regime": dest["tax_regime"],
        "healthcare_comparison": (
            f"Origin ({from_country}): {origin['healthcare']} | "
            f"Destination ({to_country}): {dest['healthcare']}"
        ),
        "qol_delta": qol_delta,
        "safety_delta": safety_delta,
        "to_considerations": list(dest["considerations"]),
        "to_typical_benefits": list(dest["typical_benefits"]),
    }


def get_all_countries() -> list[dict]:
    return [
        {
            "name": name,
            "currency": profile["currency"],
            "tax_regime": profile["tax_regime"],
            "major_tech_hubs": list(profile["major_tech_hubs"]),
            "quality_of_life_index": profile["quality_of_life_index"],
        }
        for name, profile in sorted(COUNTRY_PROFILES.items())
    ]


if __name__ == "__main__":
    assert infer_country("Paris, France") == "France"
    assert infer_country("Barcelona, Spain") == "Spain"
    assert infer_country("Auckland, New Zealand") == "New Zealand"
    assert infer_country("Remote") is None
    assert get_relocation_factors("India", "India") is None
    rf = get_relocation_factors("India", "United States")
    assert rf and rf["qol_delta"] is not None
    print("Smoke OK:", infer_country("Dubai, UAE"), len(get_all_countries()))
