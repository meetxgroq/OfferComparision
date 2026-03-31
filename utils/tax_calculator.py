"""
Tax Calculator - Estimates effective tax rates based on location.
Includes Federal, State, and FICA estimates for major tech hubs.
"""

from utils.location_registry import (
    LOCATION_REGISTRY,
    normalize_location,
    get_tax_rate,
)

DEFAULT_TAX_RATE = 0.30

# Backward-compatible view for any external consumers
TAX_RATES = {k: e.tax_rate for k, e in LOCATION_REGISTRY.items() if k != "Remote"}
# Also include bare-city keys for international locations (backward compat)
for _k, _e in LOCATION_REGISTRY.items():
    _city = _k.split(",")[0].strip()
    if _city and _city != _k and _city not in TAX_RATES:
        TAX_RATES[_city] = _e.tax_rate
    for _alias in _e.aliases:
        _title_alias = _alias.strip().title()
        if _title_alias and _title_alias not in TAX_RATES:
            TAX_RATES[_title_alias] = _e.tax_rate

CITY_TO_STATE_MAPPING = {}


def normalize_location_for_tax(location):
    """Normalize location for tax lookup — delegates to registry."""
    return normalize_location(location)


def estimate_tax_rate(location):
    """Estimate effective tax rate for a location."""
    return get_tax_rate(location)


def calculate_net_pay(total_compensation, location):
    """
    Calculate estimated net pay.

    Args:
        total_compensation (float): Total annual compensation
        location (str): Location name

    Returns:
        dict: Net pay analysis
    """
    rate = estimate_tax_rate(location)
    net_pay = total_compensation * (1 - rate)
    tax_amount = total_compensation * rate

    return {
        "gross_pay": total_compensation,
        "estimated_tax_rate": rate,
        "estimated_tax_amount": round(tax_amount, 2),
        "estimated_net_pay": round(net_pay, 2),
        "location": location,
    }
