import React, { useState, useEffect } from 'react';
import './MarketingWidget.css';

const MarketingWidget = ({ companyId }) => {
  const [marketingData, setMarketingData] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showTooltip, setShowTooltip] = useState(false);

  useEffect(() => {
    if (companyId) {
      loadMarketingData();
    }
  }, [companyId]);

  const loadMarketingData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/companies/${companyId}/marketing`);
      if (!response.ok) {
        throw new Error('Failed to fetch marketing data');
      }
      const data = await response.json();
      setMarketingData(data);
      setHistoricalData(data.historical || []);
      setError(null);
    } catch (err) {
      console.error('Error loading marketing data:', err);
      setError(err.message);
      // Set default data if loading fails
      setMarketingData({
        current_budget_spent: 0,
        current_brand_perception: 0.5,
        historical: []
      });
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getPerceptionLabel = (perception) => {
    if (perception < 0.3) return 'Poor';
    if (perception < 0.5) return 'Fair';
    if (perception < 0.7) return 'Good';
    if (perception < 0.85) return 'Excellent';
    return 'Outstanding';
  };

  const getSparklineData = () => {
    if (!historicalData || historicalData.length === 0) {
      return [];
    }
    // Return last 3 years
    return historicalData.slice(-3).map(d => d.budget_spent);
  };

  const getMaxSpend = () => {
    const spends = getSparklineData();
    return Math.max(...spends, marketingData?.current_budget_spent || 0);
  };

  const renderMiniChart = () => {
    const spends = getSparklineData();
    if (spends.length === 0) {
      return <div className="no-data">No historical data</div>;
    }

    const maxSpend = getMaxSpend();
    const normalizedSpends = spends.map(s => (s / maxSpend) * 100);

    return (
      <div className="mini-chart">
        {normalizedSpends.map((height, index) => (
          <div key={index} className="chart-bar-container">
            <div
              className="chart-bar"
              style={{ height: `${height}%` }}
              title={`Year: ${historicalData[historicalData.length - 3 + index].year}`}
            ></div>
          </div>
        ))}
      </div>
    );
  };

  if (loading) {
    return <div className="marketing-widget loading">Loading marketing data...</div>;
  }

  if (!marketingData) {
    return <div className="marketing-widget error">Unable to load marketing data</div>;
  }

  const perception = marketingData.current_brand_perception || 0.5;
  const currentSpend = marketingData.current_budget_spent || 0;

  return (
    <div className="marketing-widget">
      <div className="widget-header">
        <div className="widget-title">
          <span className="marketing-icon">📢</span>
          <h3>Marketing</h3>
        </div>
        <div
          className="perception-badge"
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
        >
          <span className="perception-emoji">
            {perception < 0.3 ? '😞' : perception < 0.5 ? '😐' : perception < 0.7 ? '🙂' : perception < 0.85 ? '😊' : '🤩'}
          </span>
          {showTooltip && (
            <div className="tooltip">
              <div className="tooltip-content">
                <strong>Brand Perception</strong>
                <p>{getPerceptionLabel(perception)}</p>
                <p className="perception-value">{formatPercentage(perception)}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="widget-indicators">
        <div className="indicator">
          <label>Current Spend</label>
          <div className="indicator-value">{formatCurrency(currentSpend)}</div>
        </div>
        <div className="indicator">
          <label>Brand Perception</label>
          <div className="indicator-value">{formatPercentage(perception)}</div>
        </div>
      </div>

      <div className="widget-chart-section">
        <label className="chart-label">3-Year Spending Trend</label>
        {renderMiniChart()}
      </div>

      <div className="widget-footer">
      </div>
    </div>
  );
};

export default MarketingWidget;
