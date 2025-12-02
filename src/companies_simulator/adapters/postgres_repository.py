import os
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Row
from companies_simulator.domain.models import Company, Product, PricingState, AnnualMetrics, User, MarketingState, MarketingAnnual, FinanceAnnual
from companies_simulator.domain.ports import RepositoryPort


class PostgresRepository(RepositoryPort):
    def __init__(self, db_url: Optional[str] = None):
        db_url = db_url or os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL not set")
        self.engine: Engine = create_engine(db_url, future=True)

    def _row_to_company(self, row: Row) -> Company:
        return Company(
            id=row._mapping["id"],
            name=row._mapping["name"],
            current_turn=row._mapping.get("current_turn", 1),
            created_at=row._mapping.get("created_at")
        )

    def _row_to_product(self, row: Row) -> Product:
        return Product(
            id=row._mapping["id"],
            company_id=row._mapping["company_id"],
            name=row._mapping["name"],
            sku=row._mapping.get("sku"),
            marginal_cost=Decimal(row._mapping["marginal_cost"]),
            market_perception=row._mapping.get("market_perception"),
            additional_info=row._mapping.get("additional_info"),
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
            price=Decimal(row._mapping["price"]) if row._mapping.get("price") else None,
            items_sold=row._mapping.get("items_sold"),
            marginal_cost=Decimal(row._mapping["marginal_cost"]) if row._mapping.get("marginal_cost") else None,
            created_at=row._mapping.get("created_at"),
        )

    def list_companies(self) -> List[Company]:
        q = text("SELECT id, name, current_turn, created_at FROM company ORDER BY id")
        with self.engine.connect() as conn:
            res = conn.execute(q)
            return [self._row_to_company(r) for r in res]

    def get_company(self, company_id: int) -> Optional[Company]:
        q = text("SELECT id, name, current_turn, created_at FROM company WHERE id = :id")
        with self.engine.connect() as conn:
            r = conn.execute(q, {"id": company_id}).first()
            return self._row_to_company(r) if r else None

    def list_products(self, company_id: int) -> List[Product]:
        q = text("SELECT id, company_id, name, sku, marginal_cost, market_perception, additional_info, created_at FROM product WHERE company_id = :cid ORDER BY id")
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

    def update_product_price(self, product_id: int, price: Decimal) -> None:
        with self.engine.begin() as conn:
            # Update or insert pricing state with new price
            existing = conn.execute(
                text("SELECT id FROM product_pricing_state WHERE product_id = :pid"),
                {"pid": product_id}
            ).first()
            
            if existing:
                conn.execute(
                    text("UPDATE product_pricing_state SET current_price = :price WHERE product_id = :pid"),
                    {"price": price, "pid": product_id}
                )
            else:
                # If no pricing state exists, create one with default values
                conn.execute(
                    text(
                        """
                        INSERT INTO product_pricing_state (product_id, current_price, price_elasticity)
                        VALUES (:pid, :price, 1.0)
                        """
                    ),
                    {"pid": product_id, "price": price}
                )

    def update_product_name(self, product_id: int, name: str) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text("UPDATE product SET name = :name WHERE id = :pid"),
                {"name": name, "pid": product_id}
            )

    def update_company_name(self, company_id: int, name: str) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text("UPDATE company SET name = :name WHERE id = :cid"),
                {"name": name, "cid": company_id}
            )

    def get_annual_metrics(self, product_id: int, year: int) -> Optional[AnnualMetrics]:
        q = text("SELECT id, product_id, year, revenue, market_share, demand, created_at FROM product_annual_metrics WHERE product_id = :pid AND year = :year")
        with self.engine.connect() as conn:
            r = conn.execute(q, {"pid": product_id, "year": year}).first()
            return self._row_to_annual_metrics(r) if r else None

    def list_annual_metrics(self, product_id: int) -> List[AnnualMetrics]:
        q = text("SELECT id, product_id, year, revenue, market_share, demand, price, items_sold, marginal_cost, created_at FROM product_annual_metrics WHERE product_id = :pid ORDER BY year")
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

    def _row_to_user(self, row: Row) -> User:
        return User(
            id=row._mapping["id"],
            email=row._mapping["email"],
            password_hash=row._mapping["password_hash"],
            company_id=row._mapping.get("company_id"),
            is_admin=row._mapping.get("is_admin", False),
            created_at=row._mapping.get("created_at"),
        )

    def _row_to_marketing_state(self, row: Row) -> MarketingState:
        return MarketingState(
            id=row._mapping["id"],
            company_id=row._mapping["company_id"],
            current_budget_spent=Decimal(row._mapping["current_budget_spent"]),
            current_brand_perception=Decimal(row._mapping["current_brand_perception"]),
            last_update_at=row._mapping.get("last_update_at"),
        )

    def _row_to_marketing_annual(self, row: Row) -> MarketingAnnual:
        return MarketingAnnual(
            id=row._mapping["id"],
            company_id=row._mapping["company_id"],
            year=row._mapping["year"],
            budget_spent=Decimal(row._mapping["budget_spent"]),
            brand_perception=Decimal(row._mapping["brand_perception"]),
            created_at=row._mapping.get("created_at"),
        )

    def get_user_by_email(self, email: str) -> Optional[User]:
        q = text("SELECT id, email, password_hash, company_id, is_admin, created_at FROM users WHERE email = :email")
        with self.engine.connect() as conn:
            r = conn.execute(q, {"email": email}).first()
            return self._row_to_user(r) if r else None

    def create_user(self, email: str, password_hash: str, company_id: Optional[int] = None, is_admin: bool = False) -> User:
        with self.engine.begin() as conn:
            r = conn.execute(
                text(
                    """
                    INSERT INTO users (email, password_hash, company_id, is_admin)
                    VALUES (:email, :password_hash, :company_id, :is_admin)
                    RETURNING id, email, password_hash, company_id, is_admin, created_at
                    """
                ),
                {"email": email, "password_hash": password_hash, "company_id": company_id, "is_admin": is_admin},
            ).first()
            return self._row_to_user(r)

    def get_marketing_state(self, company_id: int) -> Optional[MarketingState]:
        q = text("SELECT id, company_id, current_budget_spent, current_brand_perception, last_update_at FROM company_marketing_state WHERE company_id = :cid")
        with self.engine.connect() as conn:
            r = conn.execute(q, {"cid": company_id}).first()
            return self._row_to_marketing_state(r) if r else None

    def list_marketing_annual(self, company_id: int) -> list[MarketingAnnual]:
        q = text("SELECT id, company_id, year, budget_spent, brand_perception, created_at FROM company_marketing_annual WHERE company_id = :cid ORDER BY year DESC LIMIT 3")
        with self.engine.connect() as conn:
            res = conn.execute(q, {"cid": company_id})
            return [self._row_to_marketing_annual(r) for r in res]

    def update_marketing_budget(self, company_id: int, budget_spent: Decimal) -> MarketingState:
        with self.engine.begin() as conn:
            # Update or insert marketing state
            existing = conn.execute(
                text("SELECT id FROM company_marketing_state WHERE company_id = :cid"),
                {"cid": company_id}
            ).first()
            
            if existing:
                conn.execute(
                    text("UPDATE company_marketing_state SET current_budget_spent = :budget WHERE company_id = :cid"),
                    {"budget": budget_spent, "cid": company_id}
                )
            else:
                conn.execute(
                    text(
                        """
                        INSERT INTO company_marketing_state (company_id, current_budget_spent, current_brand_perception)
                        VALUES (:cid, :budget, 0.5)
                        """
                    ),
                    {"cid": company_id, "budget": budget_spent}
                )
            
            return self.get_marketing_state(company_id)

    def update_marketing_perception(self, company_id: int, perception: Decimal) -> MarketingState:
        with self.engine.begin() as conn:
            existing = conn.execute(
                text("SELECT id FROM company_marketing_state WHERE company_id = :cid"),
                {"cid": company_id}
            ).first()
            
            if existing:
                conn.execute(
                    text("UPDATE company_marketing_state SET current_brand_perception = :perception WHERE company_id = :cid"),
                    {"perception": perception, "cid": company_id}
                )
            else:
                conn.execute(
                    text(
                        """
                        INSERT INTO company_marketing_state (company_id, current_budget_spent, current_brand_perception)
                        VALUES (:cid, 0, :perception)
                        """
                    ),
                    {"cid": company_id, "perception": perception}
                )
            
            return self.get_marketing_state(company_id)

    def create_product(self, company_id: int, name: str, marginal_cost: Decimal, production_cost: Decimal) -> Product:
        """Create a new product for a company."""
        with self.engine.begin() as conn:
            # Insert product
            r = conn.execute(
                text(
                    """
                    INSERT INTO product (company_id, name, marginal_cost)
                    VALUES (:company_id, :name, :marginal_cost)
                    RETURNING id, company_id, name, sku, marginal_cost, market_perception, additional_info, created_at
                    """
                ),
                {"company_id": company_id, "name": name, "marginal_cost": marginal_cost},
            ).first()
            
            product = self._row_to_product(r)
            
            # Insert pricing state with production cost as initial price
            conn.execute(
                text(
                    """
                    INSERT INTO product_pricing_state (product_id, current_price, price_elasticity)
                    VALUES (:product_id, :current_price, 1.0)
                    """
                ),
                {"product_id": product.id, "current_price": production_cost},
            )
            
            return product


    def _row_to_finance_annual(self, row: Row) -> FinanceAnnual:
        return FinanceAnnual(
            id=row._mapping["id"],
            company_id=row._mapping["company_id"],
            fiscal_year=row._mapping["fiscal_year"],
            revenue=Decimal(row._mapping["revenue"]),
            operational_costs=Decimal(row._mapping["operational_costs"]),
            fabrication_costs=Decimal(row._mapping["fabrication_costs"]),
            inventory_value=Decimal(row._mapping["inventory_value"]),
            other_assets=Decimal(row._mapping["other_assets"]),
            total_assets=Decimal(row._mapping["total_assets"]),
            total_debt=Decimal(row._mapping["total_debt"]),
            amortization=Decimal(row._mapping["amortization"]),
            ebit=Decimal(row._mapping["ebit"]),
            ebitda=Decimal(row._mapping["ebitda"]),
            free_cash_flow=Decimal(row._mapping["free_cash_flow"]),
            created_at=row._mapping.get("created_at"),
        )

    def get_finance_annual(self, company_id: int, fiscal_year: int) -> Optional[FinanceAnnual]:
        """Get finance metrics for a specific company and fiscal year."""
        q = text("""
            SELECT id, company_id, fiscal_year, revenue, operational_costs, fabrication_costs,
                   inventory_value, other_assets, total_assets, total_debt, amortization,
                   ebit, ebitda, free_cash_flow, created_at
            FROM company_finance_annual
            WHERE company_id = :cid AND fiscal_year = :fy
        """)
        with self.engine.connect() as conn:
            r = conn.execute(q, {"cid": company_id, "fy": fiscal_year}).first()
            return self._row_to_finance_annual(r) if r else None

    def list_finance_annual(self, company_id: int) -> List[FinanceAnnual]:
        """Get all finance metrics for a company across all fiscal years."""
        q = text("""
            SELECT id, company_id, fiscal_year, revenue, operational_costs, fabrication_costs,
                   inventory_value, other_assets, total_assets, total_debt, amortization,
                   ebit, ebitda, free_cash_flow, created_at
            FROM company_finance_annual
            WHERE company_id = :cid
            ORDER BY fiscal_year DESC
        """)
        with self.engine.connect() as conn:
            res = conn.execute(q, {"cid": company_id})
            return [self._row_to_finance_annual(r) for r in res]

    def upsert_finance_annual(self, finance: FinanceAnnual) -> FinanceAnnual:
        """Insert or update finance metrics for a company and fiscal year."""
        with self.engine.begin() as conn:
            existing = conn.execute(
                text("SELECT id FROM company_finance_annual WHERE company_id = :cid AND fiscal_year = :fy"),
                {"cid": finance.company_id, "fy": finance.fiscal_year}
            ).first()
            
            if existing:
                conn.execute(
                    text("""
                        UPDATE company_finance_annual
                        SET revenue = :revenue,
                            operational_costs = :op_costs,
                            fabrication_costs = :fab_costs,
                            inventory_value = :inventory,
                            other_assets = :other_assets,
                            total_assets = :total_assets,
                            total_debt = :debt,
                            amortization = :amort,
                            ebit = :ebit,
                            ebitda = :ebitda,
                            free_cash_flow = :fcf
                        WHERE company_id = :cid AND fiscal_year = :fy
                    """),
                    {
                        "revenue": finance.revenue,
                        "op_costs": finance.operational_costs,
                        "fab_costs": finance.fabrication_costs,
                        "inventory": finance.inventory_value,
                        "other_assets": finance.other_assets,
                        "total_assets": finance.total_assets,
                        "debt": finance.total_debt,
                        "amort": finance.amortization,
                        "ebit": finance.ebit,
                        "ebitda": finance.ebitda,
                        "fcf": finance.free_cash_flow,
                        "cid": finance.company_id,
                        "fy": finance.fiscal_year
                    }
                )
            else:
                conn.execute(
                    text("""
                        INSERT INTO company_finance_annual 
                        (company_id, fiscal_year, revenue, operational_costs, fabrication_costs,
                         inventory_value, other_assets, total_assets, total_debt, amortization,
                         ebit, ebitda, free_cash_flow)
                        VALUES (:cid, :fy, :revenue, :op_costs, :fab_costs, :inventory, :other_assets,
                                :total_assets, :debt, :amort, :ebit, :ebitda, :fcf)
                    """),
                    {
                        "cid": finance.company_id,
                        "fy": finance.fiscal_year,
                        "revenue": finance.revenue,
                        "op_costs": finance.operational_costs,
                        "fab_costs": finance.fabrication_costs,
                        "inventory": finance.inventory_value,
                        "other_assets": finance.other_assets,
                        "total_assets": finance.total_assets,
                        "debt": finance.total_debt,
                        "amort": finance.amortization,
                        "ebit": finance.ebit,
                        "ebitda": finance.ebitda,
                        "fcf": finance.free_cash_flow
                    }
                )
            
            return self.get_finance_annual(finance.company_id, finance.fiscal_year)

