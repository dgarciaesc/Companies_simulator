import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './FinanceDashboard.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function FinanceDashboard({ companyId }) {
  const [financeData, setFinanceData] = useState([]);
  const [selectedYear, setSelectedYear] = useState(null);
  const [currentData, setCurrentData] = useState(null);
  const [revenueDetails, setRevenueDetails] = useState([]);
  const [showRevenueTooltip, setShowRevenueTooltip] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (companyId) {
      loadFinanceData();
    }
  }, [companyId]);

  useEffect(() => {
    if (financeData.length > 0) {
      // Default to most recent fiscal year (first in the list since ordered DESC)
      const latestYear = financeData[0].fiscal_year;
      setSelectedYear(latestYear);
      setCurrentData(financeData[0]);
    }
  }, [financeData]);

  useEffect(() => {
    if (selectedYear && companyId) {
      loadRevenueDetails(selectedYear);
    }
  }, [selectedYear, companyId]);

  const loadFinanceData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_URL}/api/companies/${companyId}/finance`);
      setFinanceData(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error loading finance data:', err);
      setError('Failed to load finance data');
      setLoading(false);
    }
  };

  const loadRevenueDetails = async (fiscalYear) => {
    try {
      console.log('Loading revenue details for fiscal year:', fiscalYear);
      const response = await axios.get(`${API_URL}/api/companies/${companyId}/revenue-details/${fiscalYear}`);
      console.log('Revenue details loaded:', response.data);
      setRevenueDetails(response.data);
    } catch (err) {
      console.error('Error loading revenue details:', err);
      setRevenueDetails([]);
    }
  };

  const handleYearChange = (event) => {
    const year = parseInt(event.target.value);
    setSelectedYear(year);
    const data = financeData.find(f => f.fiscal_year === year);
    setCurrentData(data);
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercentage = (value, total) => {
    if (!total || total === 0) return '0%';
    return ((value / total) * 100).toFixed(1) + '%';
  };

  if (loading) {
    return <div className="finance-dashboard loading">Loading finance data...</div>;
  }

  if (error) {
    return <div className="finance-dashboard error">{error}</div>;
  }

  if (!currentData) {
    return <div className="finance-dashboard">No finance data available</div>;
  }

  const netIncome = currentData.revenue - currentData.operational_costs - currentData.fabrication_costs;
  const profitMargin = (netIncome / currentData.revenue) * 100;

  return (
    <div className="finance-dashboard">
      <div className="finance-header">
        <h2>Finance Dashboard</h2>
        <div className="year-selector">
          <label htmlFor="fiscal-year">Fiscal Year: </label>
          <select 
            id="fiscal-year" 
            value={selectedYear || ''} 
            onChange={handleYearChange}
          >
            {financeData.map(f => (
              <option key={f.fiscal_year} value={f.fiscal_year}>
                FY {f.fiscal_year}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="finance-grid">
        {/* Income Statement Section */}
        <div className="finance-card">
          <h3>Income Statement</h3>
          <div className="finance-row">
            <span className="label bold revenue-label">
              Revenue
              <span 
                className="info-icon"
                onMouseEnter={() => {
                  console.log('Mouse enter - showing tooltip, revenueDetails:', revenueDetails);
                  setShowRevenueTooltip(true);
                }}
                onMouseLeave={() => {
                  console.log('Mouse leave - hiding tooltip');
                  setShowRevenueTooltip(false);
                }}
              >
                ?
                {showRevenueTooltip && revenueDetails.length > 0 && (
                  <div className="revenue-tooltip">
                    <h4>Revenue Breakdown (FY {selectedYear})</h4>
                    {revenueDetails.map(detail => (
                      <div key={detail.product_id} className="tooltip-row">
                        <div className="tooltip-product">{detail.product_name}</div>
                        <div className="tooltip-details">
                          <span>{detail.items_sold} units × {formatCurrency(detail.price)} = {formatCurrency(detail.total_revenue)}</span>
                        </div>
                      </div>
                    ))}
                    <div className="tooltip-total">
                      <strong>Total: {formatCurrency(currentData.revenue)}</strong>
                    </div>
                  </div>
                )}
              </span>
            </span>
            <span className="value positive bold">{formatCurrency(currentData.revenue)}</span>
          </div>
          <div className="finance-row">
            <span className="label indent">Fabrication Costs</span>
            <span className="value negative">-{formatCurrency(currentData.fabrication_costs)}</span>
            <span className="percentage">{formatPercentage(currentData.fabrication_costs, currentData.revenue)}</span>
          </div>
          <div className="finance-row">
            <span className="label indent">Operational Costs</span>
            <span className="value negative">-{formatCurrency(currentData.operational_costs)}</span>
            <span className="percentage">{formatPercentage(currentData.operational_costs, currentData.revenue)}</span>
          </div>
          <div className="finance-row separator">
            <span className="label bold">EBITDA</span>
            <span className="value bold">{formatCurrency(currentData.ebitda)}</span>
            <span className="percentage">{formatPercentage(currentData.ebitda, currentData.revenue)}</span>
          </div>
          <div className="finance-row">
            <span className="label indent">Amortization</span>
            <span className="value negative">-{formatCurrency(currentData.amortization)}</span>
          </div>
          <div className="finance-row separator">
            <span className="label bold">EBIT</span>
            <span className="value bold">{formatCurrency(currentData.ebit)}</span>
            <span className="percentage">{formatPercentage(currentData.ebit, currentData.revenue)}</span>
          </div>
          <div className="finance-row highlight">
            <span className="label bold">Net Income</span>
            <span className="value bold">{formatCurrency(netIncome)}</span>
            <span className="percentage">{profitMargin.toFixed(1)}%</span>
          </div>
        </div>

        {/* Balance Sheet Section */}
        <div className="finance-card">
          <h3>Balance Sheet</h3>
          <div className="finance-row">
            <span className="label bold">Assets</span>
          </div>
          <div className="finance-row">
            <span className="label indent">Inventory</span>
            <span className="value">{formatCurrency(currentData.inventory_value)}</span>
          </div>
          <div className="finance-row">
            <span className="label indent">Other Assets</span>
            <span className="value">{formatCurrency(currentData.other_assets)}</span>
          </div>
          <div className="finance-row separator">
            <span className="label bold">Total Assets</span>
            <span className="value bold">{formatCurrency(currentData.total_assets)}</span>
          </div>
          
          <div className="finance-row spacer">
            <span className="label bold">Liabilities</span>
          </div>
          <div className="finance-row">
            <span className="label indent">Total Debt</span>
            <span className="value negative">{formatCurrency(currentData.total_debt)}</span>
          </div>
          
          <div className="finance-row spacer separator">
            <span className="label bold">Equity</span>
            <span className="value bold">{formatCurrency(currentData.total_assets - currentData.total_debt)}</span>
          </div>
        </div>

        {/* Cash Flow Section */}
        <div className="finance-card">
          <h3>Cash Flow</h3>
          <div className="finance-row">
            <span className="label">EBIT</span>
            <span className="value">{formatCurrency(currentData.ebit)}</span>
          </div>
          <div className="finance-row">
            <span className="label">Capital Expenditures (Est.)</span>
            <span className="value negative">-{formatCurrency(currentData.total_assets * 0.1)}</span>
          </div>
          <div className="finance-row separator highlight">
            <span className="label bold">Free Cash Flow</span>
            <span className={`value bold ${currentData.free_cash_flow >= 0 ? 'positive' : 'negative'}`}>
              {formatCurrency(currentData.free_cash_flow)}
            </span>
          </div>
        </div>

        {/* Key Metrics Section */}
        <div className="finance-card">
          <h3>Key Metrics</h3>
          <div className="finance-row">
            <span className="label">Profit Margin</span>
            <span className="value">{profitMargin.toFixed(1)}%</span>
          </div>
          <div className="finance-row">
            <span className="label">EBITDA Margin</span>
            <span className="value">{formatPercentage(currentData.ebitda, currentData.revenue)}</span>
          </div>
          <div className="finance-row">
            <span className="label">Debt to Assets</span>
            <span className="value">{formatPercentage(currentData.total_debt, currentData.total_assets)}</span>
          </div>
          <div className="finance-row">
            <span className="label">Asset Turnover</span>
            <span className="value">{(currentData.revenue / currentData.total_assets).toFixed(2)}x</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FinanceDashboard;
