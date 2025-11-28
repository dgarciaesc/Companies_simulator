import React from 'react';
import './CreateProductModal.css';

const PRODUCT_TYPES = {
  luxe: {
    name: 'Luxe',
    productionCost: 2000000,
    marginalCost: 15000,
    description: 'Premium luxury motorcycle',
    icon: '👑'
  },
  premium: {
    name: 'Premium',
    productionCost: 1500000,
    marginalCost: 12000,
    description: 'High-end motorcycle',
    icon: '⭐'
  },
  medium: {
    name: 'Medium',
    productionCost: 1000000,
    marginalCost: 10000,
    description: 'Standard motorcycle',
    icon: '🏍️'
  },
  cheap: {
    name: 'Cheap',
    productionCost: 700000,
    marginalCost: 7000,
    description: 'Budget motorcycle',
    icon: '💰'
  },
  lowcost: {
    name: 'LowCost',
    productionCost: 500000,
    marginalCost: 5000,
    description: 'Economy motorcycle',
    icon: '🚗'
  }
};

const CreateProductTypeModal = ({ onTypeSelected, onClose }) => {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Product</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>
        
        <div className="modal-body">
          <p className="modal-subtitle">Select a product type to continue</p>
          
          <div className="product-types-grid">
            {Object.entries(PRODUCT_TYPES).map(([key, type]) => (
              <div
                key={key}
                className="product-type-card"
                onClick={() => onTypeSelected(key, type)}
              >
                <div className="type-icon">{type.icon}</div>
                <h3>{type.name}</h3>
                <p className="type-description">{type.description}</p>
                <div className="type-specs">
                  <div className="spec">
                    <span className="spec-label">Production Cost:</span>
                    <span className="spec-value">{formatCurrency(type.productionCost)}</span>
                  </div>
                  <div className="spec">
                    <span className="spec-label">Marginal Cost:</span>
                    <span className="spec-value">{formatCurrency(type.marginalCost)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateProductTypeModal;
