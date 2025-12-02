import os
from decimal import Decimal
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from companies_simulator.adapters.postgres_repository import PostgresRepository
from companies_simulator.services.company_service import CompanyService
from companies_simulator.services.auth_service import AuthService

load_dotenv()

app = Flask(__name__)
CORS(app)

# Add logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize repository and services
repository = PostgresRepository()
company_service = CompanyService(repository)
auth_service = AuthService(repository)


def decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


@app.route('/api/companies', methods=['GET'])
def get_companies():
    """Get all companies."""
    logger.info("Received GET request for all companies")
    try:
        companies = company_service.get_all_companies()
        logger.info(f"Found {len(companies)} companies")
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'current_turn': c.current_turn,
            'created_at': c.created_at.isoformat() if c.created_at else None
        } for c in companies])
    except Exception as e:
        logger.error(f"Error getting companies: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/overview', methods=['GET'])
def get_admin_overview():
    """Get complete overview of all companies with their products and metrics."""
    logger.info("Received GET request for admin overview")
    try:
        companies = company_service.get_all_companies()
        logger.info(f"Found {len(companies)} companies for admin overview")
        
        result = []
        for company in companies:
            # Get all products for this company
            products = repository.list_products(company.id)
            
            # Calculate total revenue and market share across all products
            total_revenue = Decimal('0')
            total_market_share = Decimal('0')
            product_count = 0
            
            product_list = []
            for product in products:
                # Get latest annual metrics
                annual_metrics = repository.list_annual_metrics(product.id)
                latest_metrics = annual_metrics[-1] if annual_metrics else None
                
                if latest_metrics:
                    total_revenue += latest_metrics.revenue
                    if latest_metrics.market_share:
                        total_market_share += latest_metrics.market_share
                    product_count += 1
                
                # Get pricing
                pricing = repository.get_pricing_state(product.id)
                
                product_list.append({
                    'id': product.id,
                    'name': product.name,
                    'sku': product.sku,
                    'marginal_cost': float(product.marginal_cost),
                    'current_price': float(pricing.current_price) if pricing else None,
                    'revenue': float(latest_metrics.revenue) if latest_metrics else 0,
                    'market_share': float(latest_metrics.market_share) if latest_metrics and latest_metrics.market_share else 0
                })
            
            # Get latest finance data
            finance_records = repository.list_finance_annual(company.id)
            latest_finance = finance_records[0] if finance_records else None
            
            # Calculate valuation (simplified: 10x EBITDA or 5x revenue if no EBITDA)
            valuation = 0
            if latest_finance:
                if latest_finance.ebitda > 0:
                    valuation = float(latest_finance.ebitda) * 10
                else:
                    valuation = float(latest_finance.revenue) * 5
            
            avg_market_share = float(total_market_share / product_count) if product_count > 0 else 0
            
            result.append({
                'id': company.id,
                'name': company.name,
                'current_turn': company.current_turn,
                'product_count': len(products),
                'products': product_list,
                'total_revenue': float(total_revenue),
                'avg_market_share': avg_market_share,
                'valuation': valuation,
                'ebitda': float(latest_finance.ebitda) if latest_finance else 0,
                'total_assets': float(latest_finance.total_assets) if latest_finance else 0,
                'total_debt': float(latest_finance.total_debt) if latest_finance else 0
            })
        
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error getting admin overview: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """Get a specific company."""
    logger.info(f"Received GET request for company {company_id}")
    try:
        company = company_service.get_company(company_id)
        if not company:
            logger.warning(f"Company {company_id} not found")
            return jsonify({'error': 'Company not found'}), 404
        
        logger.info(f"Found company {company_id}: {company.name}")
        return jsonify({
            'id': company.id,
            'name': company.name,
            'current_turn': company.current_turn,
            'created_at': company.created_at.isoformat() if company.created_at else None
        })
    except Exception as e:
        logger.error(f"Error getting company {company_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/companies/<int:company_id>/products', methods=['GET'])
def get_company_products(company_id):
    """Get all products for a company."""
    logger.info(f"Received GET request for products of company {company_id}")
    try:
        products = company_service.get_company_products(company_id)
        logger.info(f"Found {len(products)} products for company {company_id}")
        result = []
        for p in products:
            product_dict = {
                'id': p.id,
                'company_id': p.company_id,
                'name': p.name,
                'sku': p.sku,
                'marginal_cost': float(p.marginal_cost),
                'market_perception': p.market_perception,
                'additional_info': p.additional_info,
                'created_at': p.created_at.isoformat() if p.created_at else None
            }
            
            # Get current price from pricing_state
            pricing = repository.get_pricing_state(p.id)
            if pricing:
                product_dict['current_price'] = float(pricing.current_price)
                product_dict['current_demand'] = float(pricing.current_demand) if pricing.current_demand else None
                product_dict['current_market_share'] = float(pricing.current_market_share) if pricing.current_market_share else None
            
            result.append(product_dict)
        
        logger.info(f"Returning {len(result)} products for company {company_id}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting products for company {company_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/companies/<int:company_id>/products', methods=['POST'])
def create_product(company_id):
    """Create a new product for a company."""
    logger.info(f"Received POST request to create product for company {company_id}")
    try:
        data = request.get_json()
        logger.info(f"Request body: {data}")
        
        if not data:
            logger.error("Request body is empty")
            return jsonify({'error': 'Request body is required'}), 400
        
        # Validate required fields
        required_fields = ['name', 'marginal_cost', 'production_cost']
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return jsonify({'error': f'{field} is required'}), 400
        
        product_name = str(data['name']).strip()
        if not product_name:
            return jsonify({'error': 'Product name cannot be empty'}), 400
        
        marginal_cost = Decimal(str(data['marginal_cost']))
        production_cost = Decimal(str(data['production_cost']))
        
        logger.info(f"Creating product '{product_name}' with marginal_cost={marginal_cost}, production_cost={production_cost}")
        
        # Create product
        product = repository.create_product(company_id, product_name, marginal_cost, production_cost)
        logger.info(f"Product created successfully with ID: {product.id}")
        
        # Get pricing state to include in response
        pricing = repository.get_pricing_state(product.id)
        logger.info(f"Retrieved pricing state for product {product.id}")
        
        response_data = {
            'id': product.id,
            'company_id': product.company_id,
            'name': product.name,
            'sku': product.sku,
            'marginal_cost': float(product.marginal_cost),
            'market_perception': product.market_perception,
            'additional_info': product.additional_info,
            'created_at': product.created_at.isoformat() if product.created_at else None
        }
        
        if pricing:
            response_data['current_price'] = float(pricing.current_price)
            response_data['current_demand'] = float(pricing.current_demand) if pricing.current_demand else None
            response_data['current_market_share'] = float(pricing.current_market_share) if pricing.current_market_share else None
        
        logger.info(f"Successfully created product {product.id} for company {company_id}")
        return jsonify(response_data), 201
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error creating product: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>/price', methods=['PUT'])
def update_product_price(product_id):
    """Update product price."""
    logger.info(f"Received PUT request for product {product_id}")
    logger.info(f"Request data: {request.get_data()}")
    try:
        data = request.get_json()
        logger.info(f"Parsed JSON: {data}")
        if not data or 'price' not in data:
            return jsonify({'error': 'Price is required'}), 400
        
        price = Decimal(str(data['price']))
        logger.info(f"Updating product {product_id} with price {price}")
        repository.update_product_price(product_id, price)
        
        return jsonify({'success': True, 'product_id': product_id, 'price': float(price)})
    except Exception as e:
        import traceback
        traceback.print_exc()  # Print full traceback to console
        logger.error(f"Error updating price: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/companies/<int:company_id>/finance', methods=['GET'])
def get_company_finance(company_id):
    """Get finance metrics for a company across all fiscal years."""
    logger.info(f"Received GET request for finance data of company {company_id}")
    try:
        finance_records = repository.list_finance_annual(company_id)
        logger.info(f"Found {len(finance_records)} finance records for company {company_id}")
        
        result = []
        for f in finance_records:
            result.append({
                'id': f.id,
                'company_id': f.company_id,
                'fiscal_year': f.fiscal_year,
                'revenue': float(f.revenue),
                'operational_costs': float(f.operational_costs),
                'fabrication_costs': float(f.fabrication_costs),
                'inventory_value': float(f.inventory_value),
                'other_assets': float(f.other_assets),
                'total_assets': float(f.total_assets),
                'total_debt': float(f.total_debt),
                'amortization': float(f.amortization),
                'ebit': float(f.ebit),
                'ebitda': float(f.ebitda),
                'free_cash_flow': float(f.free_cash_flow),
                'created_at': f.created_at.isoformat() if f.created_at else None
            })
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting finance data for company {company_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/companies/<int:company_id>/finance/<int:fiscal_year>', methods=['GET'])
def get_company_finance_by_year(company_id, fiscal_year):
    """Get finance metrics for a specific company and fiscal year."""
    logger.info(f"Received GET request for finance data of company {company_id}, FY {fiscal_year}")
    try:
        finance = repository.get_finance_annual(company_id, fiscal_year)
        if not finance:
            logger.warning(f"No finance data found for company {company_id}, FY {fiscal_year}")
            return jsonify({'error': 'Finance data not found'}), 404
        
        result = {
            'id': finance.id,
            'company_id': finance.company_id,
            'fiscal_year': finance.fiscal_year,
            'revenue': float(finance.revenue),
            'operational_costs': float(finance.operational_costs),
            'fabrication_costs': float(finance.fabrication_costs),
            'inventory_value': float(finance.inventory_value),
            'other_assets': float(finance.other_assets),
            'total_assets': float(finance.total_assets),
            'total_debt': float(finance.total_debt),
            'amortization': float(finance.amortization),
            'ebit': float(finance.ebit),
            'ebitda': float(finance.ebitda),
            'free_cash_flow': float(finance.free_cash_flow),
            'created_at': finance.created_at.isoformat() if finance.created_at else None
        }
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting finance data: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/companies/<int:company_id>/revenue-details/<int:fiscal_year>', methods=['GET'])
def get_revenue_details(company_id, fiscal_year):
    """Get detailed revenue breakdown by product for a specific fiscal year."""
    logger.info(f"Received GET request for revenue details of company {company_id}, FY {fiscal_year}")
    try:
        # Convert fiscal year to actual year (FY 1 = 2000, FY 2 = 2001, etc.)
        actual_year = 1999 + fiscal_year
        logger.info(f"Converting FY {fiscal_year} to actual year {actual_year}")
        
        # Get all products for this company
        products = repository.list_products(company_id)
        logger.info(f"Found {len(products)} products for company {company_id}")
        
        result = []
        for product in products:
            # Get annual metrics for this product and year
            annual_metrics = repository.list_annual_metrics(product.id)
            logger.info(f"Product {product.id}: Found {len(annual_metrics)} annual metrics, years: {[m.year for m in annual_metrics]}")
            
            # Find the metrics for the requested year
            metrics_for_year = next((m for m in annual_metrics if m.year == actual_year), None)
            
            if metrics_for_year:
                logger.info(f"Product {product.id}: Found metrics for year {actual_year}, price={metrics_for_year.price}, items_sold={metrics_for_year.items_sold}")
                if metrics_for_year.price and metrics_for_year.items_sold:
                    result.append({
                        'product_id': product.id,
                        'product_name': product.name,
                        'price': float(metrics_for_year.price),
                        'items_sold': metrics_for_year.items_sold,
                        'total_revenue': float(metrics_for_year.revenue),
                        'marginal_cost': float(metrics_for_year.marginal_cost) if metrics_for_year.marginal_cost else float(product.marginal_cost),
                        'market_perception': product.market_perception
                    })
            else:
                logger.warning(f"Product {product.id}: No metrics found for year {actual_year}")
        
        logger.info(f"Returning {len(result)} revenue details")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting revenue details: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>/name', methods=['PUT'])
def update_product_name(product_id):
    """Update product name."""
    logger.info(f"Received PUT request for product name {product_id}")
    try:
        data = request.get_json()
        logger.info(f"Request data: {data}")
        if not data or 'name' not in data:
            logger.warning(f"Invalid request: name is required")
            return jsonify({'error': 'Name is required'}), 400
        
        name = str(data['name'])
        logger.info(f"Updating product {product_id} with name {name}")
        repository.update_product_name(product_id, name)
        logger.info(f"Successfully updated product {product_id} name to {name}")
        
        return jsonify({'success': True, 'product_id': product_id, 'name': name})
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error updating name: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/companies/<int:company_id>/name', methods=['PUT'])
def update_company_name(company_id):
    """Update company name."""
    logger.info(f"Received PUT request for company name {company_id}")
    try:
        data = request.get_json()
        logger.info(f"Request data: {data}")
        if not data or 'name' not in data:
            logger.warning(f"Invalid request: name is required")
            return jsonify({'error': 'Name is required'}), 400
        
        name = str(data['name'])
        logger.info(f"Updating company {company_id} with name {name}")
        repository.update_company_name(company_id, name)
        logger.info(f"Successfully updated company {company_id} name to {name}")
        
        return jsonify({'success': True, 'company_id': company_id, 'name': name})
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error updating company name: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>/metrics', methods=['GET'])
def get_product_metrics(product_id):
    """Get annual metrics for a product."""
    logger.info(f"Received GET request for metrics of product {product_id}")
    try:
        metrics = company_service.get_product_metrics(product_id)
        logger.info(f"Found {len(metrics)} metrics for product {product_id}")
        return jsonify([{
            'id': m.id,
            'product_id': m.product_id,
            'year': m.year,
            'revenue': float(m.revenue),
            'market_share': float(m.market_share) if m.market_share else None,
            'demand': float(m.demand) if m.demand else None,
            'created_at': m.created_at.isoformat() if m.created_at else None
        } for m in metrics])
    except Exception as e:
        logger.error(f"Error getting metrics for product {product_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>/metrics/<int:year>', methods=['GET'])
def get_product_metrics_by_year(product_id, year):
    """Get metrics for a specific product and year."""
    logger.info(f"Received GET request for metrics of product {product_id} for year {year}")
    try:
        metrics = company_service.get_product_metrics_by_year(product_id, year)
        if not metrics:
            logger.warning(f"Metrics not found for product {product_id} and year {year}")
            return jsonify({'error': 'Metrics not found'}), 404
        
        logger.info(f"Found metrics for product {product_id} and year {year}")
        return jsonify({
            'id': metrics.id,
            'product_id': metrics.product_id,
            'year': metrics.year,
            'revenue': float(metrics.revenue),
            'market_share': float(metrics.market_share) if metrics.market_share else None,
            'demand': float(metrics.demand) if metrics.demand else None,
            'created_at': metrics.created_at.isoformat() if metrics.created_at else None
        })
    except Exception as e:
        logger.error(f"Error getting metrics for product {product_id} and year {year}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login endpoint."""
    logger.info("Received POST request for login")
    try:
        data = request.get_json()
        logger.info(f"Login attempt for email: {data.get('email', 'N/A') if data else 'No data'}")
        if not data or 'email' not in data or 'password' not in data:
            logger.warning("Login failed: missing email or password")
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = auth_service.login(data['email'], data['password'])
        if not user:
            logger.warning(f"Login failed: invalid credentials for {data['email']}")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'company_id': user.company_id,
                'is_admin': user.is_admin
            }
        })
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register endpoint."""
    logger.info("Received POST request for registration")
    try:
        data = request.get_json()
        logger.info(f"Registration attempt for email: {data.get('email', 'N/A') if data else 'No data'}")
        if not data or 'email' not in data or 'password' not in data:
            logger.warning("Registration failed: missing email or password")
            return jsonify({'error': 'Email and password are required'}), 400
        
        company_id = data.get('company_id')
        user = auth_service.register(data['email'], data['password'], company_id)
        
        if not user:
            logger.warning(f"Registration failed: email {data['email']} already exists")
            return jsonify({'error': 'Email already exists'}), 409
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'company_id': user.company_id
            }
        }), 201
    except Exception as e:
        logger.error(f"Register error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/companies/<int:company_id>/marketing', methods=['GET'])
def get_company_marketing(company_id):
    """Get marketing data for a company."""
    logger.info(f"Received GET request for marketing data of company {company_id}")
    try:
        marketing_state = repository.get_marketing_state(company_id)
        if not marketing_state:
            # Return default marketing state if none exists
            marketing_state = {
                'current_budget_spent': 0,
                'current_brand_perception': 0.5,
            }
        else:
            marketing_state = {
                'current_budget_spent': float(marketing_state.current_budget_spent),
                'current_brand_perception': float(marketing_state.current_brand_perception),
            }
        
        # Get historical data (last 3 years)
        historical = repository.list_marketing_annual(company_id)
        logger.info(f"Found {len(historical)} historical marketing records for company {company_id}")
        marketing_state['historical'] = [
            {
                'year': m.year,
                'budget_spent': float(m.budget_spent),
                'brand_perception': float(m.brand_perception),
            }
            for m in historical
        ]
        
        logger.info(f"Returning marketing data for company {company_id}")
        return jsonify(marketing_state)
    except Exception as e:
        logger.error(f"Error getting marketing data: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 8000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
