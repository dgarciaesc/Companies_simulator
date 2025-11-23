import React from 'react';
import './CompanySelector.css';

const CompanySelector = ({ companies, selectedCompany, onSelectCompany }) => {
  return (
    <div className="company-selector">
      <h3 className="selector-title">Companies</h3>
      <div className="companies-list">
        {companies.map(company => (
          <button
            key={company.id}
            className={`company-item ${selectedCompany?.id === company.id ? 'active' : ''}`}
            onClick={() => onSelectCompany(company)}
          >
            <span className="company-icon">🏢</span>
            <span className="company-text">{company.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default CompanySelector;
