import axios from 'axios';

const api = axios.create({
  // Set your MCP server URL here. Use VITE_API_BASE_URL for environment flexibility.
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Add a global response interceptor for 401 errors
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // Clear token and user info
      localStorage.removeItem('authToken');
      // Optionally clear other user info
      // Redirect to login with a message
      if (window.location.pathname !== '/login') {
        window.location.href = '/login?session=expired';
      }
    }
    return Promise.reject(error);
  }
);

export default api; 