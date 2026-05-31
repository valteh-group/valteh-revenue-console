from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import pandas as pd

from app.config import BASE_DIR, get_settings
from app.domain.cost_engine import calculate_fixed_costs, calculate_variable_cost
from app.domain.models import (
    Client,
    ClientProfitability,
    ClientSubscription,
    CostItem,
    PricingPlan,
    RevenueEvent,
    Service,
    UsageEvent,
)
from app.domain.revenue_engine import calculate_client_revenue
from app.domain.unit_economics import calculate_gross_margin, calculate_gross_margin_percentage


@dataclass
class SeedRepository:
    """CSV-backed repository used by the first app version."""

    data_dir: str | None = None

    def __post_init__(self) -> None:
        settings = get_settings()
        self.data_path = settings.seed_data_dir if self.data_dir is None else BASE_DIR / self.data_dir

    def clients(self) -> list[Client]:
        df = pd.read_csv(self.data_path / "seed_clients.csv", parse_dates=["start_date"])
        return [Client(**_date_record(record, ["start_date"])) for record in df.to_dict("records")]

    def services(self) -> list[Service]:
        return [
            Service(
                id=1,
                code="saremi",
                name="SAREMI",
                description="Document validation and AI review service.",
                service_line="SAREMI",
            ),
            Service(
                id=2,
                code="graphos",
                name="Graphos",
                description="Ownership and counterparty graph analytics.",
                service_line="Graphos",
            ),
            Service(
                id=3,
                code="blockchain",
                name="Blockchain / BaaS",
                description="Registry events, certificates, and chaincode execution.",
                service_line="Blockchain / BaaS",
            ),
            Service(
                id=4,
                code="sigen",
                name="SIGEN / Notarial Platform",
                description="Client-facing notarial platform.",
                service_line="SIGEN",
            ),
        ]

    def pricing_plans(self) -> list[PricingPlan]:
        df = pd.read_csv(self.data_path / "seed_pricing_plans.csv")
        return [PricingPlan(**record) for record in df.to_dict("records")]

    def subscriptions(self) -> list[ClientSubscription]:
        return [
            ClientSubscription(id=1, client_id=1, pricing_plan_id=1, start_date=date(2026, 4, 1)),
            ClientSubscription(id=2, client_id=2, pricing_plan_id=2, start_date=date(2026, 6, 1)),
            ClientSubscription(id=3, client_id=3, pricing_plan_id=2, start_date=date(2026, 6, 1)),
        ]

    def usage_events(self) -> list[UsageEvent]:
        df = pd.read_csv(self.data_path / "seed_usage.csv", parse_dates=["event_timestamp"])
        records = []
        for record in df.to_dict("records"):
            metadata = record.get("metadata_json")
            record["metadata_json"] = json.loads(metadata) if isinstance(metadata, str) and metadata else {}
            records.append(record)
        return [UsageEvent(**record) for record in records]

    def cost_items(self) -> list[CostItem]:
        df = pd.read_csv(self.data_path / "seed_costs.csv")
        records = df.fillna("").to_dict("records")
        return [CostItem(**record) for record in records]

    def revenue_events(self) -> list[RevenueEvent]:
        events: list[RevenueEvent] = []
        event_id = 1
        for month in self.available_months():
            for client in self.active_clients(month):
                plan = self.active_plan_for_client_month(client.id, month)
                usage = self.usage_for_client_month(client.id, month)
                amount = calculate_client_revenue(usage, plan)
                events.append(
                    RevenueEvent(
                        id=event_id,
                        client_id=client.id,
                        service_code="sigen",
                        revenue_type="subscription_and_usage",
                        amount=amount,
                        currency="MXN",
                        event_timestamp=pd.Timestamp(f"{month}-28").to_pydatetime(),
                        description=f"{plan.name} plan revenue for {month}",
                    )
                )
                event_id += 1
        return events

    def active_clients(self, month: str) -> list[Client]:
        month_start = pd.Timestamp(f"{month}-01").date()
        active_client_ids = {
            subscription.client_id
            for subscription in self.subscriptions()
            if subscription.start_date <= month_start
            and (subscription.end_date is None or subscription.end_date >= month_start)
        }
        return [client for client in self.clients() if client.id in active_client_ids]

    def active_plan_for_client(self, client_id: int) -> PricingPlan:
        return self.active_plan_for_client_month(client_id, self.available_months()[-1])

    def active_plan_for_client_month(self, client_id: int, month: str) -> PricingPlan:
        subscription = self._active_subscription_for_client_month(client_id, month)
        if subscription is None:
            raise ValueError(f"Client {client_id} has no active subscription in {month}")
        return next(plan for plan in self.pricing_plans() if plan.id == subscription.pricing_plan_id)

    def _active_subscription_for_client_month(self, client_id: int, month: str) -> ClientSubscription | None:
        month_start = pd.Timestamp(f"{month}-01").date()
        return next(
            (
                sub
                for sub in self.subscriptions()
                if sub.client_id == client_id
                and sub.status == "active"
                and sub.start_date <= month_start
                and (sub.end_date is None or sub.end_date >= month_start)
            ),
            None,
        )

    def available_months(self) -> list[str]:
        return sorted({event.event_timestamp.strftime("%Y-%m") for event in self.usage_events()})

    def usage_for_month(self, month: str) -> list[UsageEvent]:
        return [event for event in self.usage_events() if event.event_timestamp.strftime("%Y-%m") == month]

    def usage_for_client_month(self, client_id: int, month: str) -> list[UsageEvent]:
        return [event for event in self.usage_for_month(month) if event.client_id == client_id]

    def cost_rates(self) -> dict[str, Decimal]:
        rates: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        for item in self.cost_items():
            if item.active and item.cost_type == "variable":
                rates[item.unit or item.name] += Decimal(str(item.unit_cost))
        return dict(rates)

    def client_profitability(self, client_id: int, month: str) -> ClientProfitability:
        usage = self.usage_for_client_month(client_id, month)
        subscription = self._active_subscription_for_client_month(client_id, month)
        if subscription is None:
            revenue = Decimal("0")
        else:
            plan = next(plan for plan in self.pricing_plans() if plan.id == subscription.pricing_plan_id)
            revenue = calculate_client_revenue(usage, plan)
        variable_cost = calculate_variable_cost(usage, self.cost_rates())
        return ClientProfitability(
            client_id=client_id,
            revenue=revenue,
            variable_cost=variable_cost,
            gross_margin=calculate_gross_margin(revenue, variable_cost),
            gross_margin_percentage=calculate_gross_margin_percentage(revenue, variable_cost),
        )

    def monthly_summary(self, month: str) -> dict[str, Decimal]:
        usage = self.usage_for_month(month)
        revenue = sum(
            (self.client_profitability(client.id, month).revenue for client in self.active_clients(month)),
            Decimal("0"),
        )
        variable_cost = calculate_variable_cost(usage, self.cost_rates())
        fixed_cost = calculate_fixed_costs(self.cost_items())
        gross_margin = calculate_gross_margin(revenue, variable_cost)
        operating_margin = gross_margin - fixed_cost
        return {
            "revenue": revenue,
            "variable_cost": variable_cost,
            "fixed_cost": fixed_cost,
            "gross_margin": gross_margin,
            "operating_margin": operating_margin,
            "burn_rate": abs(min(operating_margin, Decimal("0"))),
        }

    def revenue_by_service(self, month: str) -> dict[str, Decimal]:
        totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        for client in self.active_clients(month):
            plan = self.active_plan_for_client_month(client.id, month)
            totals["SIGEN"] += Decimal(str(plan.monthly_fixed_fee))
        for client in self.active_clients(month):
            plan = self.active_plan_for_client_month(client.id, month)
            for event in self.usage_for_client_month(client.id, month):
                if event.event_type.startswith("saremi"):
                    totals["SAREMI"] += _event_revenue(event.event_type, event.quantity, plan)
                elif event.event_type.startswith("graphos"):
                    totals["Graphos"] += _event_revenue(event.event_type, event.quantity, plan)
                elif event.event_type.startswith("blockchain"):
                    totals["Blockchain / BaaS"] += _event_revenue(event.event_type, event.quantity, plan)
        return dict(totals)

    def cost_by_service(self, month: str) -> dict[str, Decimal]:
        totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        rates = self.cost_rates()
        for event in self.usage_for_month(month):
            service = _service_label(event.service_code)
            totals[service] += Decimal(str(event.quantity)) * rates.get(event.event_type, Decimal("0"))
        return dict(totals)


def _date_record(record: dict, keys: list[str]) -> dict:
    for key in keys:
        if hasattr(record[key], "date"):
            record[key] = record[key].date()
    return record


def _service_label(service_code: str) -> str:
    labels = {"saremi": "SAREMI", "graphos": "Graphos", "blockchain": "Blockchain / BaaS", "sigen": "SIGEN"}
    return labels.get(service_code, service_code)


def _event_revenue(event_type: str, quantity: Decimal, plan: PricingPlan) -> Decimal:
    price_map = {
        "saremi.document_validation": plan.price_per_document,
        "saremi.ine_validation": plan.price_per_validation,
        "graphos.query": plan.price_per_graph_query,
        "graphos.case_analysis": plan.price_per_graph_query,
        "blockchain.asiento_registration": plan.price_per_blockchain_transaction,
        "blockchain.folio_mint": plan.price_per_property_mint,
    }
    return Decimal(str(quantity)) * Decimal(str(price_map.get(event_type, Decimal("0"))))
