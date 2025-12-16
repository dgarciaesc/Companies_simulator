import React from 'react';
import './DashboardTutorialModal.css';

const DashboardTutorialModal = ({ onClose }) => {
  return (
    <div className="tutorial-modal-overlay">
      <div className="tutorial-modal">
        <button className="tutorial-close-button" onClick={onClose} aria-label="Close">
          ×
        </button>
        
        <div className="tutorial-header">
          <h2>📊 Welcome to the General Dashboard</h2>
        </div>
        
        <div className="tutorial-body">
          <div className="tutorial-content">
            <img src="/images/john-toe.png" alt="John Toe" className="tutorial-avatar" />
            <div className="tutorial-text">
              <h3>Your Command Center</h3>
              <p>
                Welcome to your <strong>General Dashboard</strong> - your central hub for managing your motorcycle company's day-to-day operations.
              </p>
              
              <div className="tutorial-section">
                <h4>📈 Key Metrics Overview</h4>
                <p>
                  At the top of this dashboard, you'll see your company's vital statistics:
                </p>
                <ul>
                  <li><strong>Revenue:</strong> Total income from product sales</li>
                  <li><strong>Market Share:</strong> Your portion of the total market</li>
                  <li><strong>Products:</strong> Number of motorcycles in your lineup</li>
                </ul>
              </div>
              
              <div className="tutorial-section">
                <h4>🏍️ Product Management</h4>
                <p>
                  This is where you define your <strong>product strategy</strong>:
                </p>
                <ul>
                  <li><strong>Set Prices:</strong> Adjust pricing for each motorcycle model</li>
                  <li><strong>View Costs:</strong> Monitor marginal costs and profitability</li>
                  <li><strong>Create Products:</strong> Launch new motorcycle models</li>
                  <li><strong>Track Performance:</strong> See sales trends over time</li>
                </ul>
              </div>
              
              <div className="tutorial-section">
                <h4>💡 Getting Started</h4>
                <p>
                  Start by reviewing your existing products and their current pricing. Adjust prices strategically to maximize revenue while maintaining market competitiveness.
                </p>
              </div>
              
              <button className="tutorial-button" onClick={onClose}>
                Got It! Let's Start
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardTutorialModal;
