import React from 'react';
import './ProductsList.css';

const ProductsList = ({ products }) => {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <div className="products-list">
      <h2 className="products-title">Products</h2>
      <div className="products-grid">
        {products.map(product => (
          <div key={product.id} className="product-card">
            <div className="product-header">
              <h3 className="product-name">{product.name}</h3>
              {product.sku && <span className="product-sku">{product.sku}</span>}
            </div>
            <div className="product-metrics">
              <div className="metric">
                <span className="metric-label">Market Share</span>
                <span className="metric-value market-share">
                  {product.current_market_share 
                    ? formatPercentage(product.current_market_share) 
                    : 'N/A'}
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Revenue</span>
                <span className="metric-value revenue">
                  {product.current_revenue 
                    ? formatCurrency(product.current_revenue) 
                    : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductsList;
