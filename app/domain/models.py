from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Client(BaseModel):
    id: int
    name: str
    client_type: str
    status: str
    start_date: date
    notes: str | None = None


class Service(BaseModel):
    id: int
    code: str
    name: str
    description: str
    service_line: str


class PricingPlan(BaseModel):
    id: int
    name: str
    setup_fee: Decimal = Decimal("0")
    annual_fee: Decimal = Decimal("0")
    monthly_fixed_fee: Decimal = Decimal("0")
    included_documents: int = 0
    included_validations: int = 0
    included_graph_queries: int = 0
    included_blockchain_transactions: int = 0
    price_per_document: Decimal = Decimal("0")
    price_per_validation: Decimal = Decimal("0")
    price_per_graph_query: Decimal = Decimal("0")
    price_per_blockchain_transaction: Decimal = Decimal("0")
    price_per_property_mint: Decimal = Decimal("0")
    revenue_share_percentage: Decimal = Decimal("0")


class ClientSubscription(BaseModel):
    id: int
    client_id: int
    pricing_plan_id: int
    start_date: date
    end_date: date | None = None
    status: str = "active"
    notes: str | None = None


class UsageEvent(BaseModel):
    id: int
    client_id: int
    service_code: str
    event_type: str
    quantity: Decimal
    unit: str
    event_timestamp: datetime
    source_system: str
    external_reference_id: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class CostItem(BaseModel):
    id: int
    name: str
    category: str
    service_line: str | None = None
    cost_type: str
    monthly_amount: Decimal = Decimal("0")
    one_time_amount: Decimal = Decimal("0")
    start_date: date | None = None
    unit_cost: Decimal = Decimal("0")
    unit: str | None = None
    currency: str = "MXN"
    active: bool = True


class RevenueEvent(BaseModel):
    id: int
    client_id: int
    service_code: str
    revenue_type: str
    amount: Decimal
    currency: str
    event_timestamp: datetime
    description: str | None = None


class ScenarioAssumption(BaseModel):
    id: int
    scenario_name: str
    assumption_key: str
    assumption_value: Decimal
    unit: str
    description: str | None = None


class ClientProfitability(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    client_id: int
    revenue: Decimal
    variable_cost: Decimal
    gross_margin: Decimal
    gross_margin_percentage: Decimal
