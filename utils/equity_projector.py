"""
Equity Risk Projection Engine.

Computes scenario-based equity projections, year-by-year compensation
breakdowns, cash-vs-risk ratios, and risk-adjusted equity values.
No external stock APIs -- uses company stage + stability as volatility proxies.
"""

VESTING_SCHEDULES = {
    "standard": [0.0, 0.25, 0.25, 0.25, 0.25],       # 1yr cliff, then 25%/yr
    "frontloaded": [0.05, 0.15, 0.40, 0.40],           # Amazon-style
    "backloaded": [0.10, 0.10, 0.20, 0.60],            # Backloaded
    "monthly": [1/48] * 48,                             # Monthly, no cliff (summed per year later)
}

SCENARIO_STOCK_CHANGES = [
    {"label": "Bear (-50%)", "stock_change": -0.50},
    {"label": "Down (-25%)", "stock_change": -0.25},
    {"label": "Flat (0%)", "stock_change": 0.00},
    {"label": "Up (+25%)", "stock_change": 0.25},
    {"label": "Bull (+50%)", "stock_change": 0.50},
]

STAGE_VOLATILITY = {
    "startup": 0.60,
    "series_a": 0.50,
    "series_b": 0.40,
    "series_c": 0.30,
    "growth": 0.25,
    "pre_ipo": 0.20,
    "public": 0.15,
    "established": 0.10,
}


def project_equity_scenarios(
    equity_annual,
    company_stage="growth",
    stability=7,
    equity_type="rsu",
    vesting_years=4,
    vesting_schedule="standard",
    strike_price=None,
    current_price=None,
):
    """
    Project equity value under 5 stock-price scenarios.

    Returns:
        dict with "scenarios" list and "volatility_estimate".
    """
    volatility = STAGE_VOLATILITY.get(company_stage.lower(), 0.25)
    stability_factor = max(0.5, min(1.5, stability / 10.0))
    volatility *= (2.0 - stability_factor)

    scenarios = []
    for sc in SCENARIO_STOCK_CHANGES:
        change = sc["stock_change"]

        if equity_type == "cash":
            adjusted = equity_annual
        elif equity_type == "options":
            if strike_price and current_price and current_price > 0:
                new_price = current_price * (1 + change)
                intrinsic = max(0, new_price - strike_price)
                ratio = intrinsic / current_price if current_price else 0
                adjusted = equity_annual * ratio
            else:
                adjusted = equity_annual * max(0, 1 + change)
        else:  # rsu
            adjusted = equity_annual * (1 + change)

        scenarios.append({
            "label": sc["label"],
            "stock_change": change,
            "adjusted_annual_equity": round(adjusted, 2),
        })

    return {
        "scenarios": scenarios,
        "volatility_estimate": round(volatility, 3),
        "equity_type": equity_type,
    }


def _get_yearly_vest_fractions(vesting_schedule, vesting_years):
    """Return per-year vest fractions, length == vesting_years."""
    raw = VESTING_SCHEDULES.get(vesting_schedule, VESTING_SCHEDULES["standard"])

    if vesting_schedule == "monthly":
        months_per_year = 12
        fractions = []
        for yr in range(vesting_years):
            start = yr * months_per_year
            end = min(start + months_per_year, len(raw))
            fractions.append(sum(raw[start:end]) if start < len(raw) else 0.0)
        return fractions

    if len(raw) - 1 >= vesting_years:
        return raw[: vesting_years]

    padded = list(raw) + [0.0] * max(0, vesting_years - len(raw))
    return padded[: vesting_years]


def calculate_yearly_comp(
    base,
    equity_annual,
    bonus,
    signing_bonus,
    vesting_schedule="standard",
    scenarios=None,
    vesting_years=4,
):
    """
    Build year-by-year compensation breakdown for each scenario.

    Returns:
        dict with "years" list, each entry having base, bonus, signing_bonus,
        equity_by_scenario (list of 5 values), total_by_scenario (list of 5 values).
    """
    if scenarios is None:
        scenarios = project_equity_scenarios(equity_annual)["scenarios"]

    vest_fracs = _get_yearly_vest_fractions(vesting_schedule, vesting_years)
    years = []

    for yr_idx in range(vesting_years):
        frac = vest_fracs[yr_idx] if yr_idx < len(vest_fracs) else 0.0
        signing = signing_bonus if yr_idx == 0 else 0

        equity_by_scenario = []
        total_by_scenario = []
        for sc in scenarios:
            eq = round(sc["adjusted_annual_equity"] * frac * vesting_years, 2)
            equity_by_scenario.append(eq)
            total_by_scenario.append(round(base + bonus + signing + eq, 2))

        years.append({
            "year": yr_idx + 1,
            "base": base,
            "bonus": bonus,
            "signing_bonus": signing,
            "vest_fraction": round(frac, 4),
            "equity_by_scenario": equity_by_scenario,
            "total_by_scenario": total_by_scenario,
        })

    return {"years": years, "vesting_schedule": vesting_schedule}


def calculate_cash_risk_ratio(base, bonus, signing_bonus, equity_annual):
    """
    Compute guaranteed-cash vs at-risk-equity ratio.

    Returns:
        dict with cash_ratio, at_risk_ratio, cash_total, at_risk_total, total.
    """
    cash_total = base + bonus + signing_bonus
    total = cash_total + equity_annual
    if total == 0:
        return {"cash_ratio": 1.0, "at_risk_ratio": 0.0,
                "cash_total": 0, "at_risk_total": 0, "total": 0}
    return {
        "cash_ratio": round(cash_total / total, 4),
        "at_risk_ratio": round(equity_annual / total, 4),
        "cash_total": cash_total,
        "at_risk_total": equity_annual,
        "total": total,
    }


STAGE_DISCOUNT = {
    "startup": 0.40,
    "series_a": 0.50,
    "series_b": 0.60,
    "series_c": 0.70,
    "growth": 0.80,
    "pre_ipo": 0.85,
    "public": 0.90,
    "established": 0.95,
}


def calculate_risk_adjusted_value(equity_annual, company_stage="growth",
                                   stability=7, equity_type="rsu"):
    """
    Discount equity by stage and stability to approximate real expected value.
    Cash-equivalent equity is returned at face value.
    """
    if equity_annual <= 0 or equity_type == "cash":
        return equity_annual

    stage_discount = STAGE_DISCOUNT.get(company_stage.lower(), 0.80)
    stability_factor = max(0.5, min(1.0, stability / 10.0))
    return round(equity_annual * stage_discount * stability_factor, 2)
