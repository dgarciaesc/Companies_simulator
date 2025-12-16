# Add product_historical_data table to existing database
# Run this without stopping the API server

Write-Host "=== Adding product_historical_data table ===" -ForegroundColor Cyan
Write-Host ""

$DbUser = "companies_user"
$DbName = "companies_db"
$env:PGPASSWORD = "0589Allez85"

# Apply the migration
Write-Host "Applying migration..." -ForegroundColor Cyan
& psql -U $DbUser -h localhost -d $DbName -f ".\scripts\add_product_historical_table.sql"

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Table created" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Failed to create table" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Now populating historical data ===" -ForegroundColor Cyan
Write-Host ""

# Populate product historical data
$env:DATABASE_URL = "postgresql://companies_user:0589Allez85@localhost:5432/companies_db"

# Run Python script to populate only product historical data
python -c @"
import os
from decimal import Decimal
from sqlalchemy import text, create_engine

db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)

print('Populating product historical data...')

with engine.begin() as conn:
    # Get all products
    products = conn.execute(text('SELECT id, marginal_cost, company_id FROM product ORDER BY id')).fetchall()
    
    for product in products:
        product_id = product[0]
        marginal_cost = Decimal(str(product[1]))
        
        # Insert historical data for fiscal years 1, 2, 3
        for fy in [1, 2, 3]:
            # Check if already exists
            existing = conn.execute(
                text('SELECT id FROM product_historical_data WHERE product_id = :pid AND fiscal_year = :fy'),
                {'pid': product_id, 'fy': fy}
            ).first()
            
            if not existing:
                price = marginal_cost * Decimal('2.5')
                items_sold = 800 + (product_id * 50) + (fy * 100)
                total_revenue = price * items_sold
                
                perceptions = ['Good', 'Excellent', 'Outstanding']
                perception = perceptions[fy - 1]
                
                conn.execute(
                    text('''
                        INSERT INTO product_historical_data 
                        (product_id, fiscal_year, price, marginal_cost, market_perception, items_sold, total_revenue)
                        VALUES (:pid, :fy, :price, :mc, :mp, :items, :revenue)
                    '''),
                    {
                        'pid': product_id,
                        'fy': fy,
                        'price': price,
                        'mc': marginal_cost,
                        'mp': perception,
                        'items': items_sold,
                        'revenue': total_revenue
                    }
                )
                print(f'  - Product {product_id}, FY {fy}: {items_sold} items sold at {float(price):.2f} = {float(total_revenue):.2f}')

print('\n[OK] Product historical data populated!')
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== Migration Complete ===" -ForegroundColor Green
    Write-Host "The product_historical_data table has been added and populated." -ForegroundColor Green
    Write-Host "Your API server should now work with the revenue details endpoint." -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Failed to populate data" -ForegroundColor Red
    exit 1
}
