from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from app.domain.models import PricingPlan, UsageEvent
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


def calculate_client_revenue(client_usage: Iterable[UsageEvent], pricing_plan: PricingPlan) -> Decimal:
    """Calculate recurring and usage-based revenue for one client and period."""

    revenue = money(pricing_plan.monthly_fixed_fee)
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
