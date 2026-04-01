import pytest
from utils.equity_projector import (
    VESTING_SCHEDULES,
    project_equity_scenarios,
    calculate_yearly_comp,
    calculate_cash_risk_ratio,
    calculate_risk_adjusted_value,
)


class TestVestingSchedules:
    def test_standard_sums_to_one(self):
        assert sum(VESTING_SCHEDULES["standard"]) == pytest.approx(1.0)

    def test_frontloaded_sums_to_one(self):
        assert sum(VESTING_SCHEDULES["frontloaded"]) == pytest.approx(1.0)

    def test_backloaded_sums_to_one(self):
        assert sum(VESTING_SCHEDULES["backloaded"]) == pytest.approx(1.0)

    def test_monthly_sums_to_one(self):
        assert sum(VESTING_SCHEDULES["monthly"]) == pytest.approx(1.0)

    def test_standard_has_cliff(self):
        """Standard schedule: 0% year 1 (cliff), 25% each year 2-4."""
        assert VESTING_SCHEDULES["standard"][0] == 0.0
        assert VESTING_SCHEDULES["standard"][1] == pytest.approx(0.25)


class TestProjectEquityScenarios:
    def test_returns_five_scenarios(self):
        result = project_equity_scenarios(50000, "growth", 7)
        assert len(result["scenarios"]) == 5

    def test_scenario_keys(self):
        result = project_equity_scenarios(50000, "growth", 7)
        scenario = result["scenarios"][0]
        assert "label" in scenario
        assert "stock_change" in scenario
        assert "adjusted_annual_equity" in scenario

    def test_zero_equity(self):
        result = project_equity_scenarios(0, "growth", 7)
        for s in result["scenarios"]:
            assert s["adjusted_annual_equity"] == 0

    def test_options_with_strike(self):
        result = project_equity_scenarios(
            50000, "startup", 8,
            equity_type="options", strike_price=10.0, current_price=20.0
        )
        assert result["scenarios"][0]["adjusted_annual_equity"] >= 0

    def test_cash_equivalent_ignores_scenarios(self):
        result = project_equity_scenarios(50000, "growth", 7, equity_type="cash")
        for s in result["scenarios"]:
            assert s["adjusted_annual_equity"] == 50000


class TestCalculateYearlyComp:
    def test_standard_vesting_year1_no_equity(self):
        scenarios = project_equity_scenarios(40000, "growth", 7)
        result = calculate_yearly_comp(
            base=150000, equity_annual=40000, bonus=20000,
            signing_bonus=10000, vesting_schedule="standard",
            scenarios=scenarios["scenarios"], vesting_years=4,
        )
        year1 = result["years"][0]
        assert year1["base"] == 150000
        assert year1["equity_by_scenario"][2] == 0  # flat scenario, cliff year

    def test_signing_bonus_only_year1(self):
        scenarios = project_equity_scenarios(40000, "growth", 7)
        result = calculate_yearly_comp(
            base=150000, equity_annual=40000, bonus=20000,
            signing_bonus=10000, vesting_schedule="standard",
            scenarios=scenarios["scenarios"], vesting_years=4,
        )
        assert result["years"][0]["signing_bonus"] == 10000
        assert result["years"][1]["signing_bonus"] == 0

    def test_returns_correct_year_count(self):
        scenarios = project_equity_scenarios(40000, "growth", 7)
        result = calculate_yearly_comp(
            base=150000, equity_annual=40000, bonus=20000,
            signing_bonus=0, vesting_schedule="standard",
            scenarios=scenarios["scenarios"], vesting_years=4,
        )
        assert len(result["years"]) == 4


class TestCashRiskRatio:
    def test_all_cash_ratio_is_one(self):
        result = calculate_cash_risk_ratio(150000, 20000, 10000, 0)
        assert result["cash_ratio"] == pytest.approx(1.0)

    def test_half_equity(self):
        result = calculate_cash_risk_ratio(100000, 0, 0, 100000)
        assert result["cash_ratio"] == pytest.approx(0.5)
        assert result["at_risk_ratio"] == pytest.approx(0.5)

    def test_zero_total(self):
        result = calculate_cash_risk_ratio(0, 0, 0, 0)
        assert result["cash_ratio"] == 1.0


class TestRiskAdjustedValue:
    def test_public_company_discount(self):
        val = calculate_risk_adjusted_value(50000, "public", 9)
        assert val < 50000

    def test_startup_heavy_discount(self):
        val = calculate_risk_adjusted_value(50000, "startup", 5)
        assert val < calculate_risk_adjusted_value(50000, "public", 9)

    def test_zero_equity(self):
        assert calculate_risk_adjusted_value(0, "growth", 7) == 0

    def test_cash_type_no_discount(self):
        val = calculate_risk_adjusted_value(50000, "growth", 7, equity_type="cash")
        assert val == 50000
