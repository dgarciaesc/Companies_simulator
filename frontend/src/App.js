import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import Login from './components/Login';
import WelcomeModal from './components/WelcomeModal';
import SideNavigation from './components/SideNavigation';
import CompanySelector from './components/CompanySelector';
import ProductsList from './components/ProductsList';
import HistoricalChart from './components/HistoricalChart';
import MarketingWidget from './components/MarketingWidget';
import { fetchCompanies, fetchProducts, fetchAnnualMetrics } from './api';

function App() {
  const [user, setUser] = useState(null);
  const [showWelcome, setShowWelcome] = useState(false);
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [products, setProducts] = useState([]);
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState('marketing');

  // Check if user is already logged in
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    if (user) {
      loadCompanies();
    }
  }, [user]);

  useEffect(() => {
    if (selectedCompany) {
      loadCompanyData(selectedCompany.id);
    }
  }, [selectedCompany]);

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setShowWelcome(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
    setCompanies([]);
    setSelectedCompany(null);
    setProducts([]);
    setHistoricalData([]);
  };

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

  const handleProductUpdate = () => {
    if (selectedCompany) {
      loadCompanyData(selectedCompany.id);
    }
  };

  const handleCompanyNameUpdate = (newName) => {
    // Update the selected company name in state
    setSelectedCompany(prev => ({
      ...prev,
      name: newName
    }));
    
    // Update the companies list
    setCompanies(prev => 
      prev.map(company => 
        company.id === selectedCompany.id 
          ? { ...company, name: newName }
          : company
      )
    );
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

  // Show login if user is not authenticated
  if (!user) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="App">
      <Header companyName={selectedCompany?.name} onLogout={handleLogout} />
      {showWelcome && (
        <WelcomeModal 
          onClose={() => setShowWelcome(false)} 
          companyId={selectedCompany?.id}
          companyName={selectedCompany?.name}
          onCompanyNameUpdate={handleCompanyNameUpdate}
        />
      )}
      <div className="app-layout">
        <SideNavigation activeSection={activeSection} onSectionChange={setActiveSection} />
        <div className="main-container">
          <main className="content">
            {activeSection === 'marketing' && (
              <>
                <div className="dashboard-grid">
                  <div className="products-section">
                    <ProductsList products={products} onProductUpdate={handleProductUpdate} />
                  </div>
                  <div className="marketing-section">
                    {selectedCompany && <MarketingWidget companyId={selectedCompany.id} />}
                  </div>
                </div>
                <HistoricalChart data={historicalData} products={products} />
              </>
            )}
            {activeSection === 'finance' && <div className="section-placeholder">Finance Dashboard</div>}
            {activeSection === 'production' && <div className="section-placeholder">Production Dashboard</div>}
            {activeSection === 'research' && <div className="section-placeholder">Research Dashboard</div>}
            {activeSection === 'operations' && <div className="section-placeholder">Operations Dashboard</div>}
            {activeSection === 'geopolitics' && <div className="section-placeholder">Geopolitics Dashboard</div>}
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;
