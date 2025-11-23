import os
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import text as sa_text

from companies_simulator.adapters.postgres_repository import PostgresRepository


# Fixture: Gets the database connection URL from environment variables
# Scope: session - runs once per test session
# Purpose: Provides the PostgreSQL connection string for tests
# If TEST_DATABASE_URL or DATABASE_URL is not configured, skips the tests
@pytest.fixture(scope="session")
def db_url() -> str:
    # Allow explicit TEST_DATABASE_URL for tests, fall back to DATABASE_URL
    url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL (or DATABASE_URL) to run DB integration tests")
    return url


# Fixture: Creates an instance of the PostgreSQL repository
# Scope: session - the same instance is reused for all tests
# Purpose: Provides access to the repository that encapsulates DB operations
@pytest.fixture(scope="session")
def repo(db_url):
    return PostgresRepository(db_url=db_url)


# Fixture: Prepares and cleans the database schema before and after each test
# Scope: function - runs before and after each test function
# Purpose: 
#   - Setup: Drops existing tables, recreates schema from sql/schema.sql
#   - Teardown: Cleans up tables after the test to maintain isolation
# This ensures each test starts with a clean database
@pytest.fixture(scope="function")
def setup_db(repo):
    # Load and (re)create schema for a clean test database
    project_root = Path(__file__).resolve().parents[1]
    schema_path = project_root / "sql" / "schema.sql"
    if not schema_path.exists():
        pytest.skip("schema.sql not found in project `sql/` folder")

    schema_sql = schema_path.read_text()

    # Drop tables if they exist to ensure idempotent setup
    drop_stmt = """
    DROP TABLE IF EXISTS product_annual_metrics CASCADE;
    DROP TABLE IF EXISTS product_pricing_state CASCADE;
    DROP TABLE IF EXISTS product CASCADE;
    DROP TABLE IF EXISTS company CASCADE;
    """

    with repo.engine.begin() as conn:
        conn.exec_driver_sql(drop_stmt)
        conn.exec_driver_sql(schema_sql)
        conn.exec_driver_sql(
            """
            -- Grant permissions on the public schema
            GRANT ALL PRIVILEGES ON SCHEMA public TO test;
            GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO test;
            GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO test;

            -- Configure default permissions for future objects
            ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO test;
            ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO test;
            """
        )

    yield

    # Teardown: drop the tables after test
    with repo.engine.begin() as conn:
        conn.exec_driver_sql(drop_stmt)


# Test: Inserts 5 companies with 2 products each and verifies retrieval
# Purpose: Validate that the repository can:
#   1. Insert data into the database (companies and products)
#   2. Retrieve all companies using list_companies()
#   3. Retrieve products by company using list_products(company_id)
#   4. Maintain referential integrity (correct company_id in products)
#   5. Preserve data types (Decimal for marginal_cost)
# 
# Test structure:
#   - Inserts 5 companies ("Company 1" to "Company 5")
#   - Each company has 2 products with unique SKU (e.g., "C1-P1", "C1-P2")
#   - Verifies exactly 5 companies are retrieved
#   - Verifies each company has exactly 2 products
#   - Verifies products have the correct company_id
#   - Verifies marginal_cost is of type Decimal (not float)
def test_insert_and_retrieve(setup_db, repo):
    # Insert 5 companies, each with 2 products
    inserted = []  # list of (company_id, [product_ids])
    with repo.engine.begin() as conn:
        for i in range(5):
            r = conn.execute(sa_text("INSERT INTO company (name) VALUES (:name) RETURNING id"), {"name": f"Company {i+1}"})
            company_id = int(r.scalar_one())
            product_ids = []
            for j in range(2):
                sku = f"C{company_id}-P{j+1}"
                mc = Decimal("1.00") + Decimal(i + j)
                pr = conn.execute(
                    sa_text(
                        "INSERT INTO product (company_id, name, sku, marginal_cost) VALUES (:cid, :name, :sku, :mc) RETURNING id"
                    ),
                    {"cid": company_id, "name": f"Product {j+1} of C{company_id}", "sku": sku, "mc": mc},
                )
                product_ids.append(int(pr.scalar_one()))
            inserted.append((company_id, product_ids))

    # Verify retrieval via repository API
    companies = repo.list_companies()
    assert len(companies) == 5, f"Expected 5 companies, got {len(companies)}"

    for company_id, product_ids in inserted:
        products = repo.list_products(company_id)
        assert len(products) == 2, f"Company {company_id} should have 2 products"
        # Verify the marginal_cost types and product company_id
        for p in products:
            assert p.company_id == company_id
            assert isinstance(p.marginal_cost, Decimal)


# Test: Inserts annual metrics for products and verifies retrieval
# Purpose: Validate that the repository can:
#   1. Insert annual metrics (revenue, market_share, demand) for products
#   2. Retrieve metrics using list_annual_metrics(product_id)
#   3. Retrieve specific year metrics using get_annual_metrics(product_id, year)
#   4. Preserve data types (Decimal for numeric fields)
# 
# Test structure:
#   - Uses the companies and products from previous test setup
#   - Inserts 3 years of metrics (2021-2023) for each product
#   - Verifies retrieval of all metrics for a product
#   - Verifies retrieval of specific year metrics
def test_annual_metrics(setup_db, repo):
    # Insert a company and product first
    with repo.engine.begin() as conn:
        r = conn.execute(sa_text("INSERT INTO company (name) VALUES (:name) RETURNING id"), {"name": "Test Company"})
        company_id = int(r.scalar_one())
        
        pr = conn.execute(
            sa_text("INSERT INTO product (company_id, name, sku, marginal_cost) VALUES (:cid, :name, :sku, :mc) RETURNING id"),
            {"cid": company_id, "name": "Test Product", "sku": "TEST-001", "mc": Decimal("10.00")}
        )
        product_id = int(pr.scalar_one())
        
        # Insert annual metrics for 3 years
        for year in [2021, 2022, 2023]:
            revenue = Decimal("100000.00") * year // 2020
            market_share = Decimal("0.25") + Decimal(year - 2021) * Decimal("0.05")
            demand = Decimal("5000.00") + Decimal(year - 2021) * Decimal("1000.00")
            
            conn.execute(
                sa_text(
                    "INSERT INTO product_annual_metrics (product_id, year, revenue, market_share, demand) VALUES (:pid, :year, :rev, :ms, :dem)"
                ),
                {"pid": product_id, "year": year, "rev": revenue, "ms": market_share, "dem": demand}
            )
    
    # Verify retrieval of all metrics
    metrics = repo.list_annual_metrics(product_id)
    assert len(metrics) == 3, f"Expected 3 annual metrics, got {len(metrics)}"
    
    # Verify metrics are sorted by year
    assert metrics[0].year == 2021
    assert metrics[1].year == 2022
    assert metrics[2].year == 2023
    
    # Verify data types
    for m in metrics:
        assert isinstance(m.revenue, Decimal)
        assert isinstance(m.market_share, Decimal) or m.market_share is None
        assert isinstance(m.demand, Decimal) or m.demand is None
    
    # Verify specific year retrieval
    metrics_2022 = repo.get_annual_metrics(product_id, 2022)
    assert metrics_2022 is not None
    assert metrics_2022.year == 2022
    assert metrics_2022.product_id == product_id
