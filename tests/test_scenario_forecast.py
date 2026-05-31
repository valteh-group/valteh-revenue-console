from decimal import Decimal

from app.domain.scenario_forecast import (
    ClientEconomicsProfile,
    ScenarioConfig,
    forecast_months,
    month_forecast,
    scenario_client_profiles,
)


def test_forecast_months_starts_from_base_month() -> None:
    assert forecast_months("2026-06", 6) == ["2026-06", "2026-07", "2026-08", "2026-09", "2026-10", "2026-11"]


def test_pessimistic_drops_largest_client_and_increases_costs() -> None:
    profiles = [
        ClientEconomicsProfile(client_id=1, revenue=Decimal("10000"), variable_cost=Decimal("1000")),
        ClientEconomicsProfile(client_id=2, revenue=Decimal("4000"), variable_cost=Decimal("500")),
    ]
    config = ScenarioConfig(
        name="Pessimistic",
        fixed_cost_multiplier=Decimal("1.10"),
        variable_cost_multiplier=Decimal("1.20"),
        drop_largest_client=True,
    )

    forecast = month_forecast(config, "2026-06", 1, profiles, Decimal("1000"))

    assert forecast.clients == 1
    assert forecast.revenue == Decimal("4000")
    assert forecast.fixed_cost == Decimal("1100.00")
    assert forecast.variable_cost == Decimal("600.00")


def test_optimistic_adds_average_client_from_join_month() -> None:
    profiles = [
        ClientEconomicsProfile(client_id=1, revenue=Decimal("10000"), variable_cost=Decimal("1000")),
        ClientEconomicsProfile(client_id=2, revenue=Decimal("4000"), variable_cost=Decimal("500")),
    ]
    config = ScenarioConfig(name="Optimistic", add_new_client=True, new_client_join_month=4)

    before_join = scenario_client_profiles(config, 3, profiles)
    after_join = scenario_client_profiles(config, 4, profiles)

    assert len(before_join) == 2
    assert len(after_join) == 3
    assert after_join[-1].revenue == Decimal("7000")
    assert after_join[-1].variable_cost == Decimal("750")
