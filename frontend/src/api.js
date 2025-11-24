import axios from 'axios';

// Use relative path since we have proxy configured in package.json
const API_BASE_URL = '/api';

export const fetchCompanies = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/companies`);
    return response.data;
  } catch (error) {
    console.error('Error fetching companies:', error);
    // Return mock data for development
    return [
      { id: 1, name: 'Company 1' },
      { id: 2, name: 'Company 2' },
      { id: 3, name: 'Company 3' }
    ];
  }
};

export const fetchProducts = async (companyId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/companies/${companyId}/products`);
    return response.data;
  } catch (error) {
    console.error('Error fetching products:', error);
    // Return mock data for development
    return [
      { id: 1, name: 'Product A', sku: 'SKU-001', current_market_share: 0.35, current_revenue: 150000 },
      { id: 2, name: 'Product B', sku: 'SKU-002', current_market_share: 0.28, current_revenue: 120000 }
    ];
  }
};

export const fetchAnnualMetrics = async (productId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/products/${productId}/metrics`);
    return response.data;
  } catch (error) {
    console.error('Error fetching annual metrics:', error);
    // Return mock data for development
    return [
      { year: 2021, revenue: 100000, market_share: 0.25, demand: 5000 },
      { year: 2022, revenue: 125000, market_share: 0.30, demand: 6000 },
      { year: 2023, revenue: 150000, market_share: 0.35, demand: 7000 }
    ];
  }
};

export const updateProductPrice = async (productId, price) => {
  try {
    const response = await axios.put(`${API_BASE_URL}/products/${productId}/price`, { price });
    return response.data;
  } catch (error) {
    console.error('Error updating product price:', error);
    throw error;
  }
};

export const updateProductName = async (productId, name) => {
  try {
    const response = await axios.put(`${API_BASE_URL}/products/${productId}/name`, { name });
    return response.data;
  } catch (error) {
    console.error('Error updating product name:', error);
    throw error;
  }
};
