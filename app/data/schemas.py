from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ClientORM(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    client_type: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class ServiceORM(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    service_line: Mapped[str] = mapped_column(String(80), nullable=False)


class PricingPlanORM(Base):
    __tablename__ = "pricing_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    setup_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    annual_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    monthly_fixed_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    included_documents: Mapped[int] = mapped_column(default=0)
    included_validations: Mapped[int] = mapped_column(default=0)
    included_graph_queries: Mapped[int] = mapped_column(default=0)
    included_blockchain_transactions: Mapped[int] = mapped_column(default=0)
    price_per_document: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    price_per_validation: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    price_per_graph_query: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    price_per_blockchain_transaction: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    price_per_property_mint: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    revenue_share_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=0)


class ClientSubscriptionORM(Base):
    __tablename__ = "client_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    pricing_plan_id: Mapped[int] = mapped_column(ForeignKey("pricing_plans.id"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(40), default="active")
    notes: Mapped[str | None] = mapped_column(Text)


class UsageEventORM(Base):
    __tablename__ = "usage_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    service_code: Mapped[str] = mapped_column(String(80), nullable=False)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(40), nullable=False)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    source_system: Mapped[str] = mapped_column(String(80), nullable=False)
    external_reference_id: Mapped[str | None] = mapped_column(String(120))
    metadata_json: Mapped[str | None] = mapped_column(Text)


class CostItemORM(Base):
    __tablename__ = "cost_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    service_line: Mapped[str | None] = mapped_column(String(80))
    cost_type: Mapped[str] = mapped_column(String(40), nullable=False)
    monthly_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    one_time_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    start_date: Mapped[date | None] = mapped_column(Date)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 6), default=0)
    unit: Mapped[str | None] = mapped_column(String(80))
    currency: Mapped[str] = mapped_column(String(3), default="MXN")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class RevenueEventORM(Base):
    __tablename__ = "revenue_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    service_code: Mapped[str] = mapped_column(String(80), nullable=False)
    revenue_type: Mapped[str] = mapped_column(String(80), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="MXN")
    event_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class ScenarioAssumptionORM(Base):
    __tablename__ = "scenario_assumptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_name: Mapped[str] = mapped_column(String(80), nullable=False)
    assumption_key: Mapped[str] = mapped_column(String(120), nullable=False)
    assumption_value: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
