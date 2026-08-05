import API from './api';

export const dashboardService = {
  getSummary: async () => {
    const response = await API.get('/dashboard/summary');
    return response.data;
  },

  getProviderStats: async () => {
    const response = await API.get('/dashboard/provider-stats');
    return response.data;
  },

  getRiskDistribution: async () => {
    const response = await API.get('/dashboard/risk-distribution');
    return response.data;
  },

  getRecentIncidents: async (limit = 10) => {
    const response = await API.get(`/dashboard/recent-incidents?limit=${limit}`);
    return response.data;
  },

  getHealth: async () => {
    const response = await API.get('/health/');
    return response.data;
  },
};
