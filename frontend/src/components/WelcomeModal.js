import React from 'react';
import './WelcomeModal.css';

const WelcomeModal = ({ onClose }) => {
  return (
    <div className="welcome-modal-overlay" onClick={onClose}>
      <div className="welcome-modal" onClick={(e) => e.stopPropagation()}>
        <div className="welcome-header">
          <h2>Welcome to the Company Management Dashboard</h2>
        </div>
        <div className="welcome-body">
          <div className="assistant-intro">
            <img src="/images/john-toe.png" alt="John Toe" className="assistant-avatar" />
            <div className="assistant-text">
              <p className="assistant-greeting">
                <strong>My name is John Toe, your virtual assistant.</strong> I will guide you through the essential decisions that will shape the future of our company. Together, we will work to strengthen performance, drive sustainable growth, and ensure that all stakeholders remain confident and satisfied.
              </p>
            </div>
          </div>
          
          <div className="dashboard-description">
            <p>
              This interface is the <strong>Company Management Dashboard</strong>. Here, you will find all the tools you need to run the organization effectively:
            </p>
            <ul>
              <li>Pricing and sales management</li>
              <li>Financial monitoring and strategic planning</li>
              <li>Marketing operations and campaign oversight</li>
              <li>Market trends, competition insights, and industry indicators</li>
              <li>And a full suite of key performance metrics critical to informed decision-making</li>
            </ul>
          </div>
          
          <div className="assistant-closing">
            <p>
              I'll be here to support you every step of the way.
            </p>
            <p className="emphasis">
              Let's begin building a successful future for the company.
            </p>
          </div>
        </div>
        <div className="welcome-footer">
          <button className="welcome-button" onClick={onClose}>
            Get Started
          </button>
        </div>
      </div>
    </div>
  );
};

export default WelcomeModal;
