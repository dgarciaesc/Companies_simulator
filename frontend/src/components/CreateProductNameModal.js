import React, { useState } from 'react';
import './CreateProductModal.css';

const CreateProductNameModal = ({ productType, onProductCreate, onClose }) => {
  const [productName, setProductName] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!productName.trim()) {
      setError('Please enter a product name');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await onProductCreate(productName.trim());
    } catch (err) {
      setError(err.message || 'Failed to create product');
      setIsLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content name-input-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Name Your Product</h2>
          <button className="close-btn" onClick={onClose} disabled={isLoading}>✕</button>
        </div>
        
        <div className="modal-body">
          <p className="modal-subtitle">
            Creating a <strong>{productType.name}</strong> motorcycle
          </p>
          
          <form className="name-input-form" onSubmit={handleSubmit}>
            <div className="name-input-group">
              <label htmlFor="productName">Product Name</label>
              <input
                id="productName"
                type="text"
                value={productName}
                onChange={(e) => {
                  setProductName(e.target.value);
                  setError('');
                }}
                placeholder="Enter a unique product name..."
                disabled={isLoading}
                autoFocus
              />
              {error && <div className="error-message">{error}</div>}
            </div>

            <div className="modal-actions">
              <button
                type="button"
                className="modal-btn modal-btn-secondary"
                onClick={onClose}
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="modal-btn modal-btn-primary"
                disabled={isLoading || !productName.trim()}
              >
                {isLoading ? 'Creating...' : 'Create Product'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateProductNameModal;
