import React, { useState } from 'react';
import './ProductsList.css';
import { updateProductPrice, updateProductName } from '../api';

const ProductsList = ({ products, onProductUpdate }) => {
  const [editingPriceId, setEditingPriceId] = useState(null);
  const [editingNameId, setEditingNameId] = useState(null);
  const [priceValues, setPriceValues] = useState({});
  const [nameValues, setNameValues] = useState({});
  const [showInfoModal, setShowInfoModal] = useState(null);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const handlePriceEdit = (productId, currentPrice) => {
    setEditingPriceId(productId);
    setPriceValues({ ...priceValues, [productId]: currentPrice || 0 });
  };

  const handlePriceChange = (productId, value) => {
    setPriceValues({ ...priceValues, [productId]: value });
  };

  const handlePriceSave = async (productId) => {
    try {
      await updateProductPrice(productId, priceValues[productId]);
      setEditingPriceId(null);
      if (onProductUpdate) {
        onProductUpdate();
      }
    } catch (error) {
      console.error('Error saving price:', error);
      alert('Error saving price. Please try again.');
    }
  };

  const handlePriceCancel = () => {
    setEditingPriceId(null);
  };

  const handleNameEdit = (productId, currentName) => {
    setEditingNameId(productId);
    setNameValues({ ...nameValues, [productId]: currentName || '' });
  };

  const handleNameChange = (productId, value) => {
    setNameValues({ ...nameValues, [productId]: value });
  };

  const handleNameSave = async (productId) => {
    try {
      await updateProductName(productId, nameValues[productId]);
      setEditingNameId(null);
      if (onProductUpdate) {
        onProductUpdate();
      }
    } catch (error) {
      console.error('Error saving name:', error);
      alert('Error saving product name. Please try again.');
    }
  };

  const handleNameCancel = () => {
    setEditingNameId(null);
  };

  return (
    <div className="products-list">
      <h2 className="products-title">Products</h2>
      <div className="products-grid">
        {products.map(product => (
          <div key={product.id} className="product-card">
            <div className="product-header">
              <div className="product-title-section">
                {editingNameId === product.id ? (
                  <div className="name-edit-container">
                    <input
                      type="text"
                      className="name-input"
                      value={nameValues[product.id] || ''}
                      onChange={(e) => handleNameChange(product.id, e.target.value)}
                      autoFocus
                    />
                    <button 
                      className="edit-action-btn save-btn"
                      onClick={() => handleNameSave(product.id)}
                    >
                      ✓
                    </button>
                    <button 
                      className="edit-action-btn cancel-btn"
                      onClick={handleNameCancel}
                    >
                      ✗
                    </button>
                  </div>
                ) : (
                  <h3 
                    className="product-name editable-name" 
                    onClick={() => handleNameEdit(product.id, product.name)}
                    title="Click to edit"
                  >
                    {product.name}
                  </h3>
                )}
                <button 
                  className="info-button"
                  onClick={() => setShowInfoModal(product)}
                  title="More information"
                >
                  ℹ️
                </button>
              </div>
              {product.sku && <span className="product-sku">{product.sku}</span>}
            </div>
            <div className="product-metrics">
              <div className="metric">
                <span className="metric-label">Precio</span>
                {editingPriceId === product.id ? (
                  <div className="price-edit-container">
                    <input
                      type="number"
                      step="0.01"
                      className="price-input"
                      value={priceValues[product.id] || 0}
                      onChange={(e) => handlePriceChange(product.id, e.target.value)}
                      autoFocus
                    />
                    <button className="save-btn" onClick={() => handlePriceSave(product.id)}>✓</button>
                    <button className="cancel-btn" onClick={handlePriceCancel}>✗</button>
                  </div>
                ) : (
                  <span 
                    className="metric-value price editable"
                    onClick={() => handlePriceEdit(product.id, product.current_price || 0)}
                    title="Click para editar"
                  >
                    {product.current_price ? formatCurrency(product.current_price) : 'N/A'}
                  </span>
                )}
              </div>
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

      {showInfoModal && (
        <div className="modal-overlay" onClick={() => setShowInfoModal(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{showInfoModal.name}</h3>
              <button className="modal-close" onClick={() => setShowInfoModal(null)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="info-section">
                <h4>Market Perception</h4>
                <p>
                  {showInfoModal.market_perception || `This product has a ${
                    showInfoModal.current_market_share > 0.3 ? 'very positive' : 
                    showInfoModal.current_market_share > 0.2 ? 'positive' : 'neutral'
                  } perception in the market with a market share of ${
                    showInfoModal.current_market_share 
                      ? (showInfoModal.current_market_share * 100).toFixed(1) 
                      : '0'
                  }%.`}
                </p>
              </div>
              <div className="info-section">
                <h4>Additional Information</h4>
                {showInfoModal.additional_info ? (
                  <p>{showInfoModal.additional_info}</p>
                ) : (
                  <ul>
                    <li><strong>SKU:</strong> {showInfoModal.sku || 'N/A'}</li>
                    <li><strong>Coste Marginal:</strong> {showInfoModal.marginal_cost ? formatCurrency(showInfoModal.marginal_cost) : 'N/A'}</li>
                    <li><strong>Precio Actual:</strong> {showInfoModal.current_price ? formatCurrency(showInfoModal.current_price) : 'N/A'}</li>
                    <li><strong>Demanda:</strong> {showInfoModal.current_demand || 'N/A'}</li>
                  </ul>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductsList;
