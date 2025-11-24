import axios from 'axios';

const API_BASE_URL = '/api';

export const login = async (email, password) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/auth/login`, { email, password });
    return response.data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

export const register = async (email, password, companyId = null) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/auth/register`, { 
      email, 
      password,
      company_id: companyId 
    });
    return response.data;
  } catch (error) {
    console.error('Register error:', error);
    throw error;
  }
};
