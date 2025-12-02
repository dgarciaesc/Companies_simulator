import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './AdminDashboard.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function AdminDashboard() {
  const [companies, setCompanies] = useState([]);
  const [expandedCompany, setExpandedCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_URL}/api/admin/overview`);
      setCompanies(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error loading admin data:', err);
      setError('Failed to load admin data');
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercentage = (value) => {
    return (value * 100).toFixed(2) + '%';
  };

  const toggleCompanyExpand = (companyId) => {
    setExpandedCompany(expandedCompany === companyId ? null : companyId);
  };

  if (loading) {
    return <div className="admin-dashboard loading">Loading admin data...</div>;
  }

  if (error) {
    return <div className="admin-dashboard error">{error}</div>;
  }

  // Calculate totals
  const totalMarketValue = companies.reduce((sum, c) => sum + c.valuation, 0);
  const totalRevenue = companies.reduce((sum, c) => sum + c.total_revenue, 0);
  const totalProducts = companies.reduce((sum, c) => sum + c.product_count, 0);

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>
        <div className="admin-stats">
          <div className="stat-card">
            <span className="stat-label">Total Companies</span>
            <span className="stat-value">{companies.length}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Total Products</span>
            <span className="stat-value">{totalProducts}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Total Revenue</span>
            <span className="stat-value">{formatCurrency(totalRevenue)}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Total Market Value</span>
            <span className="stat-value">{formatCurrency(totalMarketValue)}</span>
          </div>
        </div>
      </div>

      <div className="companies-table">
        <table>
          <thead>
            <tr>
              <th>Company</th>
              <th>Turn</th>
              <th>Products</th>
              <th>Revenue</th>
              <th>Avg Market Share</th>
              <th>EBITDA</th>
              <th>Valuation</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {companies.map((company) => (
              <React.Fragment key={company.id}>
                <tr className="company-row">
                  <td className="company-name">{company.name}</td>
                  <td>{company.current_turn}</td>
                  <td>{company.product_count}</td>
                  <td className="currency">{formatCurrency(company.total_revenue)}</td>
                  <td className="percentage">{formatPercentage(company.avg_market_share)}</td>
                  <td className="currency">{formatCurrency(company.ebitda)}</td>
                  <td className="currency highlight">{formatCurrency(company.valuation)}</td>
                  <td>
                    <button
                      className="expand-btn"
                      onClick={() => toggleCompanyExpand(company.id)}
                    >
                      {expandedCompany === company.id ? '▼' : '►'} Details
                    </button>
                  </td>
                </tr>
                {expandedCompany === company.id && (
                  <tr className="expanded-row">
                    <td colSpan="8">
                      <div className="expanded-content">
                        <div className="company-details">
                          <div className="detail-section">
                            <h3>Financial Summary</h3>
                            <div className="detail-grid">
                              <div className="detail-item">
                                <span className="detail-label">Total Assets:</span>
                                <span className="detail-value">{formatCurrency(company.total_assets)}</span>
                              </div>
                              <div className="detail-item">
                                <span className="detail-label">Total Debt:</span>
                                <span className="detail-value negative">{formatCurrency(company.total_debt)}</span>
                              </div>
                              <div className="detail-item">
                                <span className="detail-label">Equity:</span>
                                <span className="detail-value">{formatCurrency(company.total_assets - company.total_debt)}</span>
                              </div>
                              <div className="detail-item">
                                <span className="detail-label">Debt/Assets:</span>
                                <span className="detail-value">{company.total_assets > 0 ? formatPercentage(company.total_debt / company.total_assets) : 'N/A'}</span>
                              </div>
                            </div>
                          </div>

                          <div className="detail-section">
                            <h3>Products ({company.products.length})</h3>
                            <table className="products-table">
                              <thead>
                                <tr>
                                  <th>Product</th>
                                  <th>SKU</th>
                                  <th>Cost</th>
                                  <th>Price</th>
                                  <th>Revenue</th>
                                  <th>Market Share</th>
                                </tr>
                              </thead>
                              <tbody>
                                {company.products.map((product) => (
                                  <tr key={product.id}>
                                    <td>{product.name}</td>
                                    <td className="sku">{product.sku || 'N/A'}</td>
                                    <td className="currency">{formatCurrency(product.marginal_cost)}</td>
                                    <td className="currency">{product.current_price ? formatCurrency(product.current_price) : 'N/A'}</td>
                                    <td className="currency">{formatCurrency(product.revenue)}</td>
                                    <td className="percentage">{formatPercentage(product.market_share)}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AdminDashboard;
