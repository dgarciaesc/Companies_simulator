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
    try:
        companies = company_service.get_all_companies()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'created_at': c.created_at.isoformat() if c.created_at else None
        } for c in companies])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """Get a specific company."""
    try:
        company = company_service.get_company(company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        return jsonify({
            'id': company.id,
            'name': company.name,
            'created_at': company.created_at.isoformat() if company.created_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/companies/<int:company_id>/products', methods=['GET'])
def get_company_products(company_id):
    """Get all products for a company."""
    try:
        products = company_service.get_company_products(company_id)
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
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/companies/<int:company_id>/products', methods=['POST'])
def create_product(company_id):
    """Create a new product for a company."""
    logger.info(f"Received POST request to create product for company {company_id}")
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Validate required fields
        required_fields = ['name', 'marginal_cost', 'production_cost']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        product_name = str(data['name']).strip()
        if not product_name:
            return jsonify({'error': 'Product name cannot be empty'}), 400
        
        marginal_cost = Decimal(str(data['marginal_cost']))
        production_cost = Decimal(str(data['production_cost']))
        
        logger.info(f"Creating product '{product_name}' with marginal_cost={marginal_cost}, production_cost={production_cost}")
        
        # Create product
        product = repository.create_product(company_id, product_name, marginal_cost, production_cost)
        
        # Get pricing state to include in response
        pricing = repository.get_pricing_state(product.id)
        
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


@app.route('/api/products/<int:product_id>/name', methods=['PUT'])
def update_product_name(product_id):
    """Update product name."""
    logger.info(f"Received PUT request for product name {product_id}")
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400
        
        name = str(data['name'])
        logger.info(f"Updating product {product_id} with name {name}")
        repository.update_product_name(product_id, name)
        
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
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400
        
        name = str(data['name'])
        logger.info(f"Updating company {company_id} with name {name}")
        repository.update_company_name(company_id, name)
        
        return jsonify({'success': True, 'company_id': company_id, 'name': name})
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error updating company name: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>/metrics', methods=['GET'])
def get_product_metrics(product_id):
    """Get annual metrics for a product."""
    try:
        metrics = company_service.get_product_metrics(product_id)
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
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>/metrics/<int:year>', methods=['GET'])
def get_product_metrics_by_year(product_id, year):
    """Get metrics for a specific product and year."""
    try:
        metrics = company_service.get_product_metrics_by_year(product_id, year)
        if not metrics:
            return jsonify({'error': 'Metrics not found'}), 404
        
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
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login endpoint."""
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = auth_service.login(data['email'], data['password'])
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'company_id': user.company_id
            }
        })
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register endpoint."""
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400
        
        company_id = data.get('company_id')
        user = auth_service.register(data['email'], data['password'], company_id)
        
        if not user:
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
        marketing_state['historical'] = [
            {
                'year': m.year,
                'budget_spent': float(m.budget_spent),
                'brand_perception': float(m.brand_perception),
            }
            for m in historical
        ]
        
        return jsonify(marketing_state)
    except Exception as e:
        logger.error(f"Error getting marketing data: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 8000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
