import os
from decimal import Decimal
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from companies_simulator.adapters.postgres_repository import PostgresRepository
from companies_simulator.services.company_service import CompanyService

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize repository and service
repository = PostgresRepository()
company_service = CompanyService(repository)


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
        return jsonify([{
            'id': p.id,
            'company_id': p.company_id,
            'name': p.name,
            'sku': p.sku,
            'marginal_cost': float(p.marginal_cost),
            'created_at': p.created_at.isoformat() if p.created_at else None
        } for p in products])
    except Exception as e:
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


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 8000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
