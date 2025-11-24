import React from 'react';
import './Header.css';

const Header = ({ companyName, onLogout }) => {
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
          <button className="nav-button active">Dashboard</button>
          <button className="nav-button">Analytics</button>
          <button className="nav-button">Reports</button>
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
