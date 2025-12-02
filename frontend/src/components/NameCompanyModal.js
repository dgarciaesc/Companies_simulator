import React, { useState } from 'react';
import './NameCompanyModal.css';

const NameCompanyModal = ({ onClose, companyId, companyName, onCompanyNameUpdate }) => {
  const [newCompanyName, setNewCompanyName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!newCompanyName.trim()) {
      setError('Please enter a company name');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const response = await fetch(`/api/companies/${companyId}/name`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newCompanyName.trim() }),
      });

      if (!response.ok) {
        throw new Error('Failed to update company name');
      }

      const data = await response.json();
      if (data.success) {
        if (onCompanyNameUpdate) {
          onCompanyNameUpdate(data.name);
        }
        onClose();
      } else {
        setError('Failed to update company name');
      }
    } catch (err) {
      setError(err.message || 'An error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="name-modal-overlay">
      <div className="name-modal" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose} aria-label="Close">
          ×
        </button>
        
        <div className="name-header">
          <h2>📝 Your First Decision</h2>
        </div>
        
        <div className="name-body">
          <div className="name-content">
            <h3>Choose a Company Name</h3>
            <p>
              Every great company starts with a memorable name. What will you call your motorcycle empire?
            </p>
            
            <form onSubmit={handleSubmit} className="company-name-form">
              <div className="form-group">
                <label htmlFor="companyName">Company Name:</label>
                <input
                  id="companyName"
                  type="text"
                  value={newCompanyName}
                  onChange={(e) => setNewCompanyName(e.target.value)}
                  placeholder={`Currently: ${companyName}`}
                  className="company-name-input"
                  disabled={isSubmitting}
                  autoFocus
                />
              </div>
              
              {error && <div className="error-message">{error}</div>}
              
              <button 
                type="submit" 
                className="name-button"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Saving...' : 'Start My Journey'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NameCompanyModal;
