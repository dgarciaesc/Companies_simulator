from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Company:
    id: int
    name: str
    created_at: Optional[datetime] = None


@dataclass
class Product:
    id: int
    company_id: int
    name: str
    sku: Optional[str]
    marginal_cost: Decimal
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
    created_at: Optional[datetime] = None
