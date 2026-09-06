import API from './api';

export const authService = {
  login: async (credentials) => {
    const response = await API.post('/auth/login', credentials);
    return response.data;
  },

  register: async (userData) => {
    const response = await API.post('/auth/register', userData);
    return response.data;
  },

  me: async () => {
    const response = await API.get('/auth/me');
    return response.data;
  },

  logout: async () => {
    try {
      await API.post('/auth/logout');
    } catch (e) {
      console.warn("Logout request failed or network issue", e);
    }
  },
};
