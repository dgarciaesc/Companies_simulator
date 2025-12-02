import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import Login from './components/Login';
import WelcomeModal from './components/WelcomeModal';
import NameCompanyModal from './components/NameCompanyModal';
import GuidedTooltip from './components/GuidedTooltip';
import SideNavigation from './components/SideNavigation';
import ProductsList from './components/ProductsList';
import HistoricalChart from './components/HistoricalChart';
import MarketingWidget from './components/MarketingWidget';
import FinanceDashboard from './components/FinanceDashboard';
import AdminDashboard from './components/AdminDashboard';
import { fetchCompanies, fetchProducts, fetchAnnualMetrics } from './api';

function App() {
  const [user, setUser] = useState(null);
  const [showWelcome, setShowWelcome] = useState(false);
  const [showNameModal, setShowNameModal] = useState(false);
  const [guidedTourStep, setGuidedTourStep] = useState(null);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const productsRef = React.useRef(null);
  const marketingRef = React.useRef(null);
  const [products, setProducts] = useState([]);
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState('general');

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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCompany]);

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setShowWelcome(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
    setSelectedCompany(null);
    setProducts([]);
    setHistoricalData([]);
  };

  const loadCompanies = async () => {
    try {
      const data = await fetchCompanies();
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
  };

  const getTourStep = (stepNumber) => {
    const steps = {
      1: {
        currentStep: 1,
        totalSteps: 2,
        title: '🏍️ Your Products',
        description: 'This is where you manage your motorcycle products. Each product represents a different model in your lineup.',
        details: [
          'Set prices for each product to compete in the market',
          'Adjust production costs to optimize your margins',
          'Track market share and demand for each model',
          'Monitor revenue and performance over time'
        ]
      },
      2: {
        currentStep: 2,
        totalSteps: 2,
        title: '📢 Marketing Strategy',
        description: 'Control your marketing investments to boost brand awareness and drive sales. Strategic marketing spending can significantly impact your market position.',
        details: [
          'Allocate budget across different marketing channels',
          'Increase brand awareness to attract more customers',
          'Monitor ROI on your marketing investments',
          'Adjust spending based on market conditions and competition'
        ]
      }
    };
    return steps[stepNumber] || null;
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

  // Show admin dashboard if user is admin
  if (user.is_admin) {
    return (
      <div className="App">
        <Header companyName="Admin Panel" currentTurn={null} onLogout={handleLogout} />
        <div className="app-layout">
          <div className="main-container">
            <main className="content">
              <AdminDashboard />
            </main>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <Header companyName={selectedCompany?.name} currentTurn={selectedCompany?.current_turn} onLogout={handleLogout} />
      {showWelcome && (
        <WelcomeModal 
          onClose={() => {
            setShowWelcome(false);
            setShowNameModal(true);
          }}
        />
      )}
      {showNameModal && selectedCompany && (
        <NameCompanyModal
          onClose={() => {
            setShowNameModal(false);
            setTimeout(() => setGuidedTourStep(1), 500);
          }}
          companyId={selectedCompany.id}
          companyName={selectedCompany.name}
          onCompanyNameUpdate={handleCompanyNameUpdate}
        />
      )}

      {guidedTourStep && (
        <GuidedTooltip
          targetRef={guidedTourStep === 1 ? productsRef : guidedTourStep === 2 ? marketingRef : null}
          step={getTourStep(guidedTourStep)}
          onNext={() => {
            if (guidedTourStep < 2) {
              setGuidedTourStep(guidedTourStep + 1);
            } else {
              setGuidedTourStep(null);
              localStorage.setItem('hasSeenGuidedTour', 'true');
            }
          }}
          onSkip={() => {
            setGuidedTourStep(null);
            localStorage.setItem('hasSeenGuidedTour', 'true');
          }}
        />
      )}
      <div className="app-layout">
        <SideNavigation activeSection={activeSection} onSectionChange={setActiveSection} />
        <div className="main-container">
          <main className="content">
            {activeSection === 'general' && (
              <>
                <div className="dashboard-grid">
                  <div className="products-section" ref={productsRef}>
                    <ProductsList products={products} onProductUpdate={handleProductUpdate} companyId={selectedCompany?.id} />
                  </div>
                  <div className="marketing-section" ref={marketingRef}>
                    {selectedCompany && <MarketingWidget companyId={selectedCompany.id} />}
                  </div>
                </div>
                <HistoricalChart data={historicalData} products={products} />
              </>
            )}
            {activeSection === 'marketing' && (
              <>
                <div className="dashboard-grid">
                  <div className="products-section">
                    <ProductsList products={products} onProductUpdate={handleProductUpdate} companyId={selectedCompany?.id} />
                  </div>
                  <div className="marketing-section">
                    {selectedCompany && <MarketingWidget companyId={selectedCompany.id} />}
                  </div>
                </div>
                <HistoricalChart data={historicalData} products={products} />
              </>
            )}
            {activeSection === 'finance' && selectedCompany && (
              <FinanceDashboard companyId={selectedCompany.id} />
            )}
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
