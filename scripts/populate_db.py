"""
Populate database with sample data for development.
Usage: python scripts/populate_db.py
"""
import os
import hashlib
from decimal import Decimal
from pathlib import Path
from sqlalchemy import text

from companies_simulator.adapters.postgres_repository import PostgresRepository

def hash_password(password: str) -> str:
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    db_url = os.getenv("DATABASE_URL", "postgresql://test:test1234@localhost:5432/companies_test")
    print(f"Connecting to: {db_url}")
    
    repo = PostgresRepository(db_url=db_url)
    
    # Check if data already exists
    with repo.engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM company")).scalar()
        if result > 0:
            print(f"Database already has {result} companies. Clearing...")
            # Clear existing data
            conn.execute(text("TRUNCATE TABLE company_finance_annual, company_marketing_annual, company_marketing_state, product_annual_metrics, product_pricing_state, product, users, company RESTART IDENTITY CASCADE"))
            conn.commit()
    
    print("Creating test users...")
    
    # Create test users
    test_users = [
        ("user1@test.com", "password1", None, False),
        ("user2@test.com", "password2", None, False),
        ("admin@test.com", "admin123", None, True),
    ]
    
    user_ids = []
    with repo.engine.begin() as conn:
        for email, password, company_id, is_admin in test_users:
            password_hash = hash_password(password)
            res = conn.execute(
                text("INSERT INTO users (email, password_hash, company_id, is_admin) VALUES (:email, :pwd, :cid, :admin) RETURNING id"),
                {"email": email, "pwd": password_hash, "cid": company_id, "admin": is_admin}
            )
            user_id = res.scalar()
            user_ids.append(user_id)
            user_type = "ADMIN" if is_admin else "USER"
            print(f"  [{user_type}] Created: {email} (password: {password})")
    
    print("\nInserting 5 companies with 2 products each...")
    
    # Insert companies and products
    for company_num in range(1, 6):
        company_name = f"Company {company_num}"
        print(f"  Creating {company_name}...")
        
        with repo.engine.begin() as conn:
            # Insert company with current_turn = 1
            res = conn.execute(
                text("INSERT INTO company (name, current_turn) VALUES (:name, 1) RETURNING id"),
                {"name": company_name}
            )
            company_id = res.scalar()
            
            # Insert 2 products for this company
            for product_num in range(1, 3):
                product_name = f"Product {company_num}-{product_num}"
                sku = f"C{company_num}-P{product_num}"
                marginal_cost = Decimal("10.00") * company_num + product_num
                
                res = conn.execute(
                    text("""
                        INSERT INTO product (company_id, name, sku, marginal_cost, market_perception, additional_info)
                        VALUES (:cid, :name, :sku, :mc, :mp, :ai)
                        RETURNING id
                    """),
                    {
                        "cid": company_id,
                        "name": product_name,
                        "sku": sku,
                        "mc": marginal_cost,
                        "mp": f"This product has an excellent reputation in the market and is highly valued by our customers.",
                        "ai": f"SKU: {sku} | Category: Premium | Warranty: 2 years"
                    }
                )
                product_id = res.scalar()
                
                # Insert pricing state
                conn.execute(
                    text("""
                        INSERT INTO product_pricing_state (product_id, current_price, price_elasticity, current_demand, current_market_share)
                        VALUES (:pid, :price, :elasticity, :demand, :share)
                    """),
                    {
                        "pid": product_id,
                        "price": marginal_cost * Decimal("2.5"),  # Price is 2.5x cost
                        "elasticity": Decimal("1.2"),
                        "demand": 1000 + (company_num * 100) + (product_num * 10),
                        "share": Decimal("0.15") + (Decimal("0.05") * company_num)
                    }
                )
                
                # Insert annual metrics for years 2000 and 2001 (fiscal years 1 and 2)
                for idx, year in enumerate([2000, 2001], start=1):
                    price = marginal_cost * Decimal("2.5")  # Price is 2.5x cost
                    items_sold = 800 + (company_num * 100) + (product_num * 50) + (idx * 100)
                    revenue = price * items_sold
                    
                    conn.execute(
                        text("""
                            INSERT INTO product_annual_metrics 
                            (product_id, year, revenue, market_share, demand, price, items_sold, marginal_cost)
                            VALUES (:pid, :year, :revenue, :share, :demand, :price, :items, :mc)
                        """),
                        {
                            "pid": product_id,
                            "year": year,
                            "revenue": revenue,
                            "share": Decimal("0.15") + (Decimal("0.05") * company_num) + (Decimal("0.02") * (idx - 1)),
                            "demand": Decimal(1000 + company_num * 100 + (idx - 1) * 200),
                            "price": price,
                            "items": items_sold,
                            "mc": marginal_cost
                        }
                    )
                
                print(f"    - {product_name} (SKU: {sku})")
    
    # Populate marketing data for each company
    print("\nPopulating marketing data...")
    with repo.engine.begin() as conn:
        for company_id in range(1, 6):
            # Current marketing state
            conn.execute(
                text("""
                    INSERT INTO company_marketing_state (company_id, current_budget_spent, current_brand_perception)
                    VALUES (:cid, :budget, :perception)
                """),
                {
                    "cid": company_id,
                    "budget": Decimal("50000") + (Decimal("10000") * company_id),
                    "perception": Decimal("0.5") + (Decimal("0.1") * company_id)
                }
            )
            
            # Historical marketing metrics for years 2000 and 2001
            for idx, year in enumerate([2000, 2001], start=1):
                conn.execute(
                    text("""
                        INSERT INTO company_marketing_annual (company_id, year, budget_spent, brand_perception)
                        VALUES (:cid, :year, :budget, :perception)
                    """),
                    {
                        "cid": company_id,
                        "year": year,
                        "budget": Decimal("30000") + (Decimal("8000") * company_id) + (Decimal("5000") * (idx - 1)),
                        "perception": Decimal("0.3") + (Decimal("0.08") * company_id) + (Decimal("0.05") * (idx - 1))
                    }
                )
    print("  ✓ Marketing data populated")
    
    # Populate finance data for each company
    print("\nPopulating finance data...")
    with repo.engine.begin() as conn:
        for company_id in range(1, 6):
            # Generate finance data for fiscal years 1 and 2 (years 2000 and 2001)
            for fy in [1, 2]:
                # Calculate metrics based on company and fiscal year
                base_revenue = Decimal("500000") * company_id
                growth_factor = Decimal("1.2") ** (fy - 1)  # 20% YoY growth
                
                revenue = base_revenue * growth_factor
                fabrication_costs = revenue * Decimal("0.35")  # 35% of revenue
                operational_costs = revenue * Decimal("0.25")  # 25% of revenue
                
                inventory = Decimal("50000") * company_id * Decimal("1.1") ** (fy - 1)
                other_assets = Decimal("100000") * company_id * Decimal("1.05") ** (fy - 1)
                total_assets = inventory + other_assets
                
                total_debt = Decimal("150000") * company_id * Decimal("0.95") ** (fy - 1)  # Debt decreasing
                amortization = Decimal("20000") * company_id
                
                ebitda = revenue - fabrication_costs - operational_costs + amortization
                ebit = ebitda - amortization
                free_cash_flow = ebit - (total_assets * Decimal("0.1"))  # Simplified FCF
                
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
                        "cid": company_id,
                        "fy": fy,
                        "revenue": revenue,
                        "op_costs": operational_costs,
                        "fab_costs": fabrication_costs,
                        "inventory": inventory,
                        "other_assets": other_assets,
                        "total_assets": total_assets,
                        "debt": total_debt,
                        "amort": amortization,
                        "ebit": ebit,
                        "ebitda": ebitda,
                        "fcf": free_cash_flow
                    }
                )
    print("  ✓ Finance data populated for FY 1 and 2 (years 2000-2001)")
    
    # Associate first user with Company 1
    with repo.engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET company_id = 1 WHERE id = :uid"),
            {"uid": user_ids[0]}
        )
    print(f"\n✓ Associated user1@test.com with Company 1")
    
    # Verify
    companies = repo.list_companies()
    print(f"\n✅ Successfully populated database with {len(companies)} companies and {len(user_ids)} users")
    print("\n📋 Test credentials:")
    print("  • user1@test.com / password1 (Company User - associated with Company 1)")
    print("  • user2@test.com / password2 (Company User)")
    print("  • admin@test.com / admin123 (ADMIN - can see all companies)")
    
    for company in companies:
        products = repo.list_products(company.id)
        print(f"  • {company.name}: {len(products)} products")

if __name__ == "__main__":
    main()
