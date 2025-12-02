import React from 'react';
import './WelcomeModal.css';

const WelcomeModal = ({ onClose }) => {
  return (
    <div className="welcome-modal-overlay">
      <div className="welcome-modal" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose} aria-label="Close">
          ×
        </button>
        
        <div className="welcome-header">
          <h2>Welcome to Your New Motorcycle Company!</h2>
        </div>
        
        <div className="welcome-body">
          <div className="assistant-intro">
            <img src="/images/john-toe.png" alt="John Toe" className="assistant-avatar" />
            <div className="assistant-text">
              <h3>🎯 Your Role as CEO</h3>
              <p>
                You've been hired as the <strong>Chief Executive Officer</strong> to drive this brand-new motorcycle company to success. Your decisions will shape the future of this business, from product strategy to market positioning.
              </p>
              <p>
                As CEO, you'll make strategic decisions across all aspects of the business:
              </p>
              <ul>
                <li><strong>Production:</strong> Manage manufacturing capacity and product development</li>
                <li><strong>Marketing:</strong> Build your brand and capture market share</li>
                <li><strong>Finance:</strong> Monitor cash flow, investments, and company valuation</li>
                <li><strong>Operations:</strong> Optimize efficiency and manage resources</li>
              </ul>
            </div>
          </div>
          
          <button className="welcome-button" onClick={onClose}>
            Let's Get Started
          </button>
        </div>
      </div>
    </div>
  );
};

export default WelcomeModal;
