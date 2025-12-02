from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class User:
    id: int
    email: str
    password_hash: str
    company_id: Optional[int] = None
    is_admin: bool = False
    created_at: Optional[datetime] = None


@dataclass
class Company:
    id: int
    name: str
    current_turn: int = 1
    created_at: Optional[datetime] = None


@dataclass
class Product:
    id: int
    company_id: int
    name: str
    sku: Optional[str]
    marginal_cost: Decimal
    market_perception: Optional[str] = None
    additional_info: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class PricingState:
    id: Optional[int]
    product_id: int
    current_price: Decimal
    current_demand: Optional[Decimal]
    current_market_share: Optional[Decimal]
    price_elasticity: Decimal
    last_update_at: Optional[datetime] = None


@dataclass
class AnnualMetrics:
    id: Optional[int]
    product_id: int
    year: int
    revenue: Decimal
    market_share: Optional[Decimal]
    demand: Optional[Decimal]
    price: Optional[Decimal] = None
    items_sold: Optional[int] = None
    marginal_cost: Optional[Decimal] = None
    created_at: Optional[datetime] = None


@dataclass
class MarketingState:
    id: Optional[int]
    company_id: int
    current_budget_spent: Decimal
    current_brand_perception: Decimal
    last_update_at: Optional[datetime] = None


@dataclass
class MarketingAnnual:
    id: Optional[int]
    company_id: int
    year: int
    budget_spent: Decimal
    brand_perception: Decimal
    created_at: Optional[datetime] = None


@dataclass
class FinanceAnnual:
    id: Optional[int]
    company_id: int
    fiscal_year: int
    revenue: Decimal
    operational_costs: Decimal
    fabrication_costs: Decimal
    inventory_value: Decimal
    other_assets: Decimal
    total_assets: Decimal
    total_debt: Decimal
    amortization: Decimal
    ebit: Decimal
    ebitda: Decimal
    free_cash_flow: Decimal
    created_at: Optional[datetime] = None

