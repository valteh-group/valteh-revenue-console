from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from decimal import Decimal

from app.domain.models import ClientSubscription, PricingPlan, UsageEvent
from app.domain.unit_economics import money

EVENT_PRICE_FIELDS = {
    "saremi.document_validation": "price_per_document",
    "saremi.ine_validation": "price_per_validation",
    "graphos.query": "price_per_graph_query",
    "graphos.case_analysis": "price_per_graph_query",
    "blockchain.asiento_registration": "price_per_blockchain_transaction",
    "blockchain.certificate_issued": "price_per_blockchain_transaction",
    "blockchain.folio_mint": "price_per_property_mint",
}


def calculate_client_revenue(
    client_usage: Iterable[UsageEvent],
    pricing_plan: PricingPlan,
    subscription: ClientSubscription | None = None,
    period_month: date | None = None,
) -> Decimal:
    """Calculate fixed subscription revenue plus usage revenue for one client and period."""

    return calculate_subscription_revenue(pricing_plan, subscription, period_month) + calculate_usage_revenue(
        client_usage, pricing_plan
    )


def calculate_subscription_revenue(
    pricing_plan: PricingPlan,
    subscription: ClientSubscription | None = None,
    period_month: date | None = None,
) -> Decimal:
    """Calculate setup, annual, and monthly fixed fees for one client and period."""

    revenue = money(pricing_plan.monthly_fixed_fee)
    if subscription and period_month:
        revenue += _setup_fee_for_month(pricing_plan, subscription, period_month)
        revenue += _annual_fee_for_month(pricing_plan, subscription, period_month)
    return revenue


def calculate_usage_revenue(client_usage: Iterable[UsageEvent], pricing_plan: PricingPlan) -> Decimal:
    """Calculate billable usage revenue after included quantities."""

    revenue = Decimal("0")
    included_remaining = {
        "saremi.document_validation": pricing_plan.included_documents,
        "saremi.ine_validation": pricing_plan.included_validations,
        "graphos.query": pricing_plan.included_graph_queries,
        "graphos.case_analysis": pricing_plan.included_graph_queries,
        "blockchain.asiento_registration": pricing_plan.included_blockchain_transactions,
        "blockchain.certificate_issued": pricing_plan.included_blockchain_transactions,
    }
    for event in client_usage:
        price_field = EVENT_PRICE_FIELDS.get(event.event_type)
        if not price_field:
            continue
        included = Decimal(str(included_remaining.get(event.event_type, 0)))
        billable_quantity = max(money(event.quantity) - included, Decimal("0"))
        included_remaining[event.event_type] = max(int(included - money(event.quantity)), 0)
        revenue += billable_quantity * money(getattr(pricing_plan, price_field))
    return revenue


def _setup_fee_for_month(
    pricing_plan: PricingPlan,
    subscription: ClientSubscription,
    period_month: date,
) -> Decimal:
    if subscription.start_date.year == period_month.year and subscription.start_date.month == period_month.month:
        return money(pricing_plan.setup_fee)
    return Decimal("0")


def _annual_fee_for_month(
    pricing_plan: PricingPlan,
    subscription: ClientSubscription,
    period_month: date,
) -> Decimal:
    if period_month < subscription.start_date:
        return Decimal("0")
    if subscription.start_date.month == period_month.month:
        return money(pricing_plan.annual_fee)
    return Decimal("0")
