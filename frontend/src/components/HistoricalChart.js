import React, { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import './HistoricalChart.css';

const COLORS = ['#f97316', '#3b82f6', '#10b981', '#8b5cf6', '#ec4899', '#f59e0b'];

const HistoricalChart = ({ data, products }) => {
  const [metricType, setMetricType] = useState('revenue');

  const formatYAxis = (value) => {
    if (metricType === 'revenue') {
      return `$${(value / 1000).toFixed(0)}K`;
    }
    return `${(value * 100).toFixed(0)}%`;
  };

  const formatTooltip = (value) => {
    if (metricType === 'revenue') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0
      }).format(value);
    }
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <div className="historical-chart">
      <div className="chart-header">
        <h2 className="chart-title">Historical Data</h2>
        <div className="metric-toggle">
          <button
            className={`toggle-button ${metricType === 'revenue' ? 'active' : ''}`}
            onClick={() => setMetricType('revenue')}
          >
            Revenue
          </button>
          <button
            className={`toggle-button ${metricType === 'market_share' ? 'active' : ''}`}
            onClick={() => setMetricType('market_share')}
          >
            Market Share
          </button>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="year"
            stroke="#6b7280"
            style={{ fontSize: '0.875rem' }}
          />
          <YAxis
            tickFormatter={formatYAxis}
            stroke="#6b7280"
            style={{ fontSize: '0.875rem' }}
          />
          <Tooltip
            formatter={formatTooltip}
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '12px'
            }}
          />
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />
          {products.map((product, index) => (
            <Line
              key={product.id}
              type="monotone"
              dataKey={`${product.name}_${metricType}`}
              name={product.name}
              stroke={COLORS[index % COLORS.length]}
              strokeWidth={3}
              dot={{ fill: COLORS[index % COLORS.length], r: 4 }}
              activeDot={{ r: 6 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default HistoricalChart;
