from decimal import Decimal

import dash_bootstrap_components as dbc
from dash import html

from app.components.forms import numeric_input
from app.components.tables import data_table
from app.data.repositories import SeedRepository
from app.domain.pricing_engine import pricing_summary, recommended_unit_price
from app.utils.currency import format_mxn


def layout():
    repo = SeedRepository()
    rows = [
        {
            "plan": plan.name,
            "setup_fee": format_mxn(plan.setup_fee),
            "annual_fee": format_mxn(plan.annual_fee),
            "monthly_fixed_fee": format_mxn(plan.monthly_fixed_fee),
            "included_documents": plan.included_documents,
            "included_validations": plan.included_validations,
            "included_graph_queries": plan.included_graph_queries,
            "included_blockchain_transactions": plan.included_blockchain_transactions,
            "price_per_document": format_mxn(plan.price_per_document),
            "price_per_validation": format_mxn(plan.price_per_validation),
            "price_per_graph_query": format_mxn(plan.price_per_graph_query),
            "price_per_blockchain_transaction": format_mxn(plan.price_per_blockchain_transaction),
            "price_per_property_mint": format_mxn(plan.price_per_property_mint),
            "revenue_share_percentage": f"{float(plan.revenue_share_percentage) * 100:.1f}%",
        }
        for plan in repo.pricing_plans()
    ]
    minimum_price = recommended_unit_price(Decimal("1.10"), Decimal("0.60"))
    summary = pricing_summary(Decimal("570"), Decimal("3000"), Decimal("6"), Decimal("1.10"))
    return html.Div(
        [
            html.H1("Pricing", className="h3"),
            html.P("Compare plans and simulate target unit economics.", className="text-muted"),
            dbc.Row(
                [
                    numeric_input("Monthly fixed fee", "monthly-fixed-fee", 4000),
                    numeric_input("Variable fee per document", "price-document", 6),
                    numeric_input("Variable fee per ID validation", "price-id", 2),
                    numeric_input("Variable fee per graph query", "price-graph", 1),
                    numeric_input("Variable fee per blockchain transaction", "price-chain", 0.5),
                    numeric_input("Variable fee per folio/property mint", "price-mint", 0),
                    numeric_input("Revenue share percentage", "revenue-share", 0, 0.1),
                    numeric_input("Target gross margin", "target-margin", 0.6, 0.05),
                ],
                className="g-3 mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Alert(f"Recommended minimum unit price: {format_mxn(minimum_price)}", color="success"), md=4
                    ),
                    dbc.Col(dbc.Alert(f"Break-even clients: {summary['break_even_clients']}", color="primary"), md=4),
                    dbc.Col(
                        dbc.Alert(f"Break-even usage: {summary['break_even_usage']:,} units", color="primary"), md=4
                    ),
                ]
            ),
            html.H2("Pricing Plans", className="h5 mt-3"),
            data_table("pricing-table", rows, 10),
        ]
    )
