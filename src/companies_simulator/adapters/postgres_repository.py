import os
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Row
from companies_simulator.domain.models import Company, Product, PricingState, AnnualMetrics
from companies_simulator.domain.ports import RepositoryPort


class PostgresRepository(RepositoryPort):
    def __init__(self, db_url: Optional[str] = None):
        db_url = db_url or os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL not set")
        self.engine: Engine = create_engine(db_url, future=True)

    def _row_to_company(self, row: Row) -> Company:
        return Company(id=row._mapping["id"], name=row._mapping["name"], created_at=row._mapping.get("created_at"))

    def _row_to_product(self, row: Row) -> Product:
        return Product(
            id=row._mapping["id"],
            company_id=row._mapping["company_id"],
            name=row._mapping["name"],
            sku=row._mapping.get("sku"),
            marginal_cost=Decimal(row._mapping["marginal_cost"]),
            created_at=row._mapping.get("created_at"),
        )

    def _row_to_pricing(self, row: Row) -> PricingState:
        return PricingState(
            id=row._mapping["id"],
            product_id=row._mapping["product_id"],
            current_price=Decimal(row._mapping["current_price"]),
            current_demand=row._mapping.get("current_demand"),
            current_market_share=row._mapping.get("current_market_share"),
            price_elasticity=Decimal(row._mapping["price_elasticity"]),
            last_update_at=row._mapping.get("last_update_at"),
        )

    def _row_to_annual_metrics(self, row: Row) -> AnnualMetrics:
        return AnnualMetrics(
            id=row._mapping["id"],
            product_id=row._mapping["product_id"],
            year=row._mapping["year"],
            revenue=Decimal(row._mapping["revenue"]),
            market_share=Decimal(row._mapping["market_share"]) if row._mapping.get("market_share") else None,
            demand=Decimal(row._mapping["demand"]) if row._mapping.get("demand") else None,
            created_at=row._mapping.get("created_at"),
        )

    def list_companies(self) -> List[Company]:
        q = text("SELECT id, name, created_at FROM company ORDER BY id")
        with self.engine.connect() as conn:
            res = conn.execute(q)
            return [self._row_to_company(r) for r in res]

    def get_company(self, company_id: int) -> Optional[Company]:
        q = text("SELECT id, name, created_at FROM company WHERE id = :id")
        with self.engine.connect() as conn:
            r = conn.execute(q, {"id": company_id}).first()
            return self._row_to_company(r) if r else None

    def list_products(self, company_id: int) -> List[Product]:
        q = text("SELECT id, company_id, name, sku, marginal_cost, created_at FROM product WHERE company_id = :cid ORDER BY id")
        with self.engine.connect() as conn:
            res = conn.execute(q, {"cid": company_id})
            return [self._row_to_product(r) for r in res]

    def get_pricing_state(self, product_id: int) -> Optional[PricingState]:
        q = text("SELECT id, product_id, current_price, current_demand, current_market_share, price_elasticity, last_update_at FROM product_pricing_state WHERE product_id = :pid")
        with self.engine.connect() as conn:
            r = conn.execute(q, {"pid": product_id}).first()
            return self._row_to_pricing(r) if r else None

    def upsert_pricing_state(self, pricing: PricingState) -> PricingState:
        # Try update, else insert
        with self.engine.begin() as conn:
            existing = conn.execute(text("SELECT id FROM product_pricing_state WHERE product_id = :pid"), {"pid": pricing.product_id}).first()
            if existing:
                conn.execute(
                    text(
                        """
                        UPDATE product_pricing_state
                        SET current_price = :price,
                            current_demand = :demand,
                            current_market_share = :mshare,
                            price_elasticity = :elasticity,
                            last_update_at = now()
                        WHERE product_id = :pid
                        RETURNING id, product_id, current_price, current_demand, current_market_share, price_elasticity, last_update_at
                        """
                    ),
                    {
                        "price": pricing.current_price,
                        "demand": pricing.current_demand,
                        "mshare": pricing.current_market_share,
                        "elasticity": pricing.price_elasticity,
                        "pid": pricing.product_id,
                    },
                )
                r = conn.execute(text("SELECT id, product_id, current_price, current_demand, current_market_share, price_elasticity, last_update_at FROM product_pricing_state WHERE product_id = :pid"), {"pid": pricing.product_id}).first()
                return self._row_to_pricing(r)
            else:
                r = conn.execute(
                    text(
                        """
                        INSERT INTO product_pricing_state (product_id, current_price, current_demand, current_market_share, price_elasticity)
                        VALUES (:pid, :price, :demand, :mshare, :elasticity)
                        RETURNING id, product_id, current_price, current_demand, current_market_share, price_elasticity, last_update_at
                        """
                    ),
                    {
                        "pid": pricing.product_id,
                        "price": pricing.current_price,
                        "demand": pricing.current_demand,
                        "mshare": pricing.current_market_share,
                        "elasticity": pricing.price_elasticity,
                    },
                ).first()
                return self._row_to_pricing(r)

    def get_annual_metrics(self, product_id: int, year: int) -> Optional[AnnualMetrics]:
        q = text("SELECT id, product_id, year, revenue, market_share, demand, created_at FROM product_annual_metrics WHERE product_id = :pid AND year = :year")
        with self.engine.connect() as conn:
            r = conn.execute(q, {"pid": product_id, "year": year}).first()
            return self._row_to_annual_metrics(r) if r else None

    def list_annual_metrics(self, product_id: int) -> List[AnnualMetrics]:
        q = text("SELECT id, product_id, year, revenue, market_share, demand, created_at FROM product_annual_metrics WHERE product_id = :pid ORDER BY year")
        with self.engine.connect() as conn:
            res = conn.execute(q, {"pid": product_id})
            return [self._row_to_annual_metrics(r) for r in res]

    def upsert_annual_metrics(self, metrics: AnnualMetrics) -> AnnualMetrics:
        with self.engine.begin() as conn:
            existing = conn.execute(
                text("SELECT id FROM product_annual_metrics WHERE product_id = :pid AND year = :year"),
                {"pid": metrics.product_id, "year": metrics.year}
            ).first()
            
            if existing:
                conn.execute(
                    text(
                        """
                        UPDATE product_annual_metrics
                        SET revenue = :revenue,
                            market_share = :mshare,
                            demand = :demand
                        WHERE product_id = :pid AND year = :year
                        """
                    ),
                    {
                        "revenue": metrics.revenue,
                        "mshare": metrics.market_share,
                        "demand": metrics.demand,
                        "pid": metrics.product_id,
                        "year": metrics.year,
                    },
                )
                r = conn.execute(
                    text("SELECT id, product_id, year, revenue, market_share, demand, created_at FROM product_annual_metrics WHERE product_id = :pid AND year = :year"),
                    {"pid": metrics.product_id, "year": metrics.year}
                ).first()
                return self._row_to_annual_metrics(r)
            else:
                r = conn.execute(
                    text(
                        """
                        INSERT INTO product_annual_metrics (product_id, year, revenue, market_share, demand)
                        VALUES (:pid, :year, :revenue, :mshare, :demand)
                        RETURNING id, product_id, year, revenue, market_share, demand, created_at
                        """
                    ),
                    {
                        "pid": metrics.product_id,
                        "year": metrics.year,
                        "revenue": metrics.revenue,
                        "mshare": metrics.market_share,
                        "demand": metrics.demand,
                    },
                ).first()
                return self._row_to_annual_metrics(r)
