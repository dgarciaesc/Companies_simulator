import React from 'react';
import './Header.css';

const Header = ({ companyName, currentTurn, onLogout }) => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <div className="logo">
            <span className="logo-icon">📊</span>
            <span className="logo-text">Companies Simulator</span>
          </div>
          {companyName && (
            <div className="company-badge">
              <span className="company-name">{companyName}</span>
            </div>
          )}
        </div>
        <nav className="header-nav">
          <div className="fiscal-year">
            <span className="fiscal-year-label">Fiscal Year / Turn:</span>
            <span className="fiscal-year-value">{currentTurn || 1}</span>
          </div>
          <button className="next-turn-button">
            Next FY/Turn →
          </button>
          {onLogout && (
            <button className="nav-button logout-button" onClick={onLogout}>
              Sign Out
            </button>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;
