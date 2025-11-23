import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import CompanySelector from './components/CompanySelector';
import ProductsList from './components/ProductsList';
import HistoricalChart from './components/HistoricalChart';
import { fetchCompanies, fetchProducts, fetchAnnualMetrics } from './api';

function App() {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [products, setProducts] = useState([]);
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCompanies();
  }, []);

  useEffect(() => {
    if (selectedCompany) {
      loadCompanyData(selectedCompany.id);
    }
  }, [selectedCompany]);

  const loadCompanies = async () => {
    try {
      const data = await fetchCompanies();
      setCompanies(data);
      if (data.length > 0) {
        setSelectedCompany(data[0]);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error loading companies:', error);
      setLoading(false);
    }
  };

  const loadCompanyData = async (companyId) => {
    try {
      const productsData = await fetchProducts(companyId);
      setProducts(productsData);

      // Load historical data for all products
      const allMetrics = await Promise.all(
        productsData.map(product => fetchAnnualMetrics(product.id))
      );

      // Combine and format historical data
      const formatted = formatHistoricalData(productsData, allMetrics);
      setHistoricalData(formatted);
    } catch (error) {
      console.error('Error loading company data:', error);
    }
  };

  const formatHistoricalData = (products, metricsArrays) => {
    const yearMap = {};

    products.forEach((product, index) => {
      const metrics = metricsArrays[index];
      metrics.forEach(metric => {
        if (!yearMap[metric.year]) {
          yearMap[metric.year] = { year: metric.year };
        }
        yearMap[metric.year][`${product.name}_revenue`] = parseFloat(metric.revenue);
        yearMap[metric.year][`${product.name}_market_share`] = metric.market_share ? parseFloat(metric.market_share) : null;
      });
    });

    return Object.values(yearMap).sort((a, b) => a.year - b.year);
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="App">
      <Header companyName={selectedCompany?.name} />
      <div className="main-container">
        <aside className="sidebar">
          <CompanySelector
            companies={companies}
            selectedCompany={selectedCompany}
            onSelectCompany={setSelectedCompany}
          />
        </aside>
        <main className="content">
          <ProductsList products={products} />
          <HistoricalChart data={historicalData} products={products} />
        </main>
      </div>
    </div>
  );
}

export default App;
