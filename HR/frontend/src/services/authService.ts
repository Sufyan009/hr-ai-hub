import api from './api';

export const loginUser = async (credentials: any) => {
  const response = await api.post('/api/auth/login/', credentials);
  return response.data;
};

export const fetchUserProfile = async () => {
  const response = await api.get('/api/user-settings/');
  return response.data;
}; 