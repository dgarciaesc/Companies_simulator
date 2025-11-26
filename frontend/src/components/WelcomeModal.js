import React, { useState } from 'react';
import './WelcomeModal.css';

const WelcomeModal = ({ onClose, companyId, companyName, onCompanyNameUpdate }) => {
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
    <div className="welcome-modal-overlay">
      <div className="welcome-modal" onClick={(e) => e.stopPropagation()}>
        <div className="welcome-header">
          <h2>Welcome to Your New Motorcycle Company!</h2>
        </div>
        <div className="welcome-body">
          <div className="assistant-intro">
            <img src="/images/john-toe.png" alt="John Toe" className="assistant-avatar" />
            <div className="assistant-text">
              <p className="assistant-greeting">
                <strong>Hello! I'm John Toe, your business consultant.</strong>
              </p>
              <p>
                Congratulations on starting your own <strong>motorcycle manufacturing company</strong>! This is an exciting journey, and I'm here to guide you every step of the way.
              </p>
            </div>
          </div>
          
          <div className="ceo-message">
            <h3>🎯 Your Role as CEO</h3>
            <p>
              You've been hired as the <strong>Chief Executive Officer</strong> to drive this brand-new company to success. Your decisions will shape the future of this business, from product strategy to market positioning.
            </p>
          </div>

          <div className="first-decision">
            <h3>📝 Your First Decision: Choose a Company Name</h3>
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
                className="welcome-button"
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

export default WelcomeModal;
