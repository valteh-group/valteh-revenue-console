from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

import pandas as pd

from app.domain.unit_economics import calculate_operating_margin, money

if TYPE_CHECKING:
    from app.data.repositories import SeedRepository


@dataclass(frozen=True)
class ScenarioConfig:
    name: str
    fixed_cost_multiplier: Decimal = Decimal("1")
    variable_cost_multiplier: Decimal = Decimal("1")
    drop_largest_client: bool = False
    largest_client_drop_month: int = 2
    add_new_client: bool = False
    new_client_join_month: int = 4


@dataclass(frozen=True)
class ClientEconomicsProfile:
    client_id: int
    revenue: Decimal
    variable_cost: Decimal


@dataclass(frozen=True)
class ScenarioMonth:
    scenario: str
    month: str
    clients: int
    revenue: Decimal
    fixed_cost: Decimal
    variable_cost: Decimal
    operating_margin: Decimal


SCENARIO_CONFIGS = [
    ScenarioConfig(name="Base"),
    ScenarioConfig(
        name="Pessimistic",
        fixed_cost_multiplier=Decimal("1.10"),
        variable_cost_multiplier=Decimal("1.20"),
        drop_largest_client=True,
    ),
    ScenarioConfig(
        name="Optimistic",
        variable_cost_multiplier=Decimal("0.90"),
        add_new_client=True,
        new_client_join_month=4,
    ),
]


def forecast_scenarios(
    repo: SeedRepository,
    horizon_months: int = 6,
    start_month: str | None = None,
    configs: list[ScenarioConfig] | None = None,
) -> list[ScenarioMonth]:
    """Build month-by-month scenario forecasts from the latest available actual month."""

    base_month = start_month or repo.available_months()[-1]
    months = forecast_months(base_month, horizon_months)
    profiles = current_client_profiles(repo, base_month)
    fixed_cost = repo.monthly_summary(base_month)["fixed_cost"]
    scenario_configs = configs or SCENARIO_CONFIGS
    return [
        month_forecast(config, month, month_index, profiles, fixed_cost)
        for config in scenario_configs
        for month_index, month in enumerate(months, start=1)
    ]


def forecast_months(start_month: str, horizon_months: int) -> list[str]:
    """Return month labels beginning with the latest actual month."""

    period = pd.Period(start_month, freq="M")
    return [str(period + offset) for offset in range(horizon_months)]


def current_client_profiles(repo: SeedRepository, month: str) -> list[ClientEconomicsProfile]:
    """Capture actual current-month client revenue and variable cost as reusable profiles."""

    return [
        ClientEconomicsProfile(
            client_id=client.id,
            revenue=repo.client_profitability(client.id, month).revenue,
            variable_cost=repo.client_profitability(client.id, month).variable_cost,
        )
        for client in repo.active_clients(month)
    ]


def month_forecast(
    config: ScenarioConfig,
    month: str,
    month_index: int,
    base_profiles: list[ClientEconomicsProfile],
    base_fixed_cost: Decimal,
) -> ScenarioMonth:
    """Apply one scenario configuration to one forecast month."""

    profiles = scenario_client_profiles(config, month_index, base_profiles)
    revenue = sum((profile.revenue for profile in profiles), Decimal("0"))
    variable_cost = sum((profile.variable_cost for profile in profiles), Decimal("0")) * money(
        config.variable_cost_multiplier
    )
    fixed_cost = money(base_fixed_cost) * money(config.fixed_cost_multiplier)
    operating_margin = calculate_operating_margin(revenue, variable_cost, fixed_cost)
    return ScenarioMonth(
        scenario=config.name,
        month=month,
        clients=len(profiles),
        revenue=revenue,
        fixed_cost=fixed_cost,
        variable_cost=variable_cost,
        operating_margin=operating_margin,
    )


def scenario_client_profiles(
    config: ScenarioConfig,
    month_index: int,
    base_profiles: list[ClientEconomicsProfile],
) -> list[ClientEconomicsProfile]:
    profiles = list(base_profiles)
    if config.drop_largest_client and month_index >= config.largest_client_drop_month and profiles:
        largest_client = max(profiles, key=lambda profile: profile.revenue)
        profiles = [profile for profile in profiles if profile.client_id != largest_client.client_id]
    if config.add_new_client and month_index >= config.new_client_join_month and profiles:
        profiles.append(average_client_profile(profiles, client_id=0))
    return profiles


def average_client_profile(
    profiles: list[ClientEconomicsProfile],
    client_id: int,
) -> ClientEconomicsProfile:
    if not profiles:
        return ClientEconomicsProfile(client_id=client_id, revenue=Decimal("0"), variable_cost=Decimal("0"))
    profile_count = Decimal(len(profiles))
    return ClientEconomicsProfile(
        client_id=client_id,
        revenue=sum((profile.revenue for profile in profiles), Decimal("0")) / profile_count,
        variable_cost=sum((profile.variable_cost for profile in profiles), Decimal("0")) / profile_count,
    )
