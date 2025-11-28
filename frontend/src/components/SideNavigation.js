import React from 'react';
import './SideNavigation.css';

const SideNavigation = ({ activeSection, onSectionChange }) => {
  const sections = [
    { id: 'general', label: 'General', icon: '📊' },
    { id: 'finance', label: 'Finance', icon: '💰' },
    { id: 'production', label: 'Production', icon: '🏭' },
    { id: 'research', label: 'Research', icon: '🔬' },
    { id: 'operations', label: 'Operations', icon: '⚙️' },
    { id: 'geopolitics', label: 'Geopolitics', icon: '🌍' },
    { id: 'marketing', label: 'Marketing', icon: '📢' },
  ];

  return (
    <nav className="side-navigation">
      <ul className="nav-list">
        {sections.map(section => (
          <li key={section.id}>
            <button
              className={`nav-link ${activeSection === section.id ? 'active' : ''}`}
              onClick={() => onSectionChange(section.id)}
              title={section.label}
            >
              <span className="nav-icon">{section.icon}</span>
              <span className="nav-label">{section.label}</span>
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default SideNavigation;
