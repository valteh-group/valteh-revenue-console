from decimal import Decimal

from app.domain.models import PricingPlan
from app.domain.pricing_simulator import (
    PricingSimulationInput,
    billable_units,
    cost_sensitivity_series,
    simulate_pricing,
)


def test_billable_units_respects_included_usage() -> None:
    assert billable_units(Decimal("600"), 500) == Decimal("100")
    assert billable_units(Decimal("400"), 500) == Decimal("0")


def test_simulate_pricing_includes_subscription_setup_usage_and_costs() -> None:
    plan = PricingPlan(
        id=1,
        name="Test",
        setup_fee=Decimal("10000"),
        monthly_fixed_fee=Decimal("4000"),
        included_documents=500,
        price_per_document=Decimal("3"),
    )
    result = simulate_pricing(
        PricingSimulationInput(
            pricing_plan=plan,
            clients=2,
            onboarding_clients=1,
            documents_per_client=Decimal("600"),
            validations_per_client=Decimal("0"),
            graph_queries_per_client=Decimal("0"),
            blockchain_transactions_per_client=Decimal("0"),
            folios_per_client=Decimal("0"),
            fixed_costs=Decimal("1000"),
            document_unit_cost=Decimal("1"),
            validation_unit_cost=Decimal("0"),
            graph_query_unit_cost=Decimal("0"),
            blockchain_transaction_unit_cost=Decimal("0"),
            folio_unit_cost=Decimal("0"),
        )
    )

    assert result.subscription_revenue == Decimal("8000")
    assert result.setup_revenue == Decimal("10000")
    assert result.usage_revenue == Decimal("600")
    assert result.variable_cost == Decimal("1200")
    assert result.operating_margin == Decimal("16400")


def test_cost_sensitivity_series_varies_selected_cost() -> None:
    plan = PricingPlan(id=1, name="Test", monthly_fixed_fee=Decimal("4000"))
    base_input = PricingSimulationInput(
        pricing_plan=plan,
        clients=1,
        onboarding_clients=0,
        documents_per_client=Decimal("100"),
        validations_per_client=Decimal("0"),
        graph_queries_per_client=Decimal("0"),
        blockchain_transactions_per_client=Decimal("0"),
        folios_per_client=Decimal("0"),
        fixed_costs=Decimal("0"),
        document_unit_cost=Decimal("1"),
        validation_unit_cost=Decimal("0"),
        graph_query_unit_cost=Decimal("0"),
        blockchain_transaction_unit_cost=Decimal("0"),
        folio_unit_cost=Decimal("0"),
    )

    rows = cost_sensitivity_series(
        base_input,
        "document_unit_cost",
        [Decimal("1"), Decimal("2")],
    )

    assert rows[0]["operating_margin"] == Decimal("3900")
    assert rows[1]["operating_margin"] == Decimal("3800")
