import API from './api';

export const incidentService = {
  getIncidents: async () => {
    const response = await API.get('/incidents/');
    return response.data;
  },

  searchIncidents: async (filters = {}) => {
    const params = new URLSearchParams();
    
    if (filters.provider) params.append('provider', filters.provider);
    if (filters.risk_level) params.append('risk_level', filters.risk_level);
    if (filters.status) params.append('status', filters.status);
    if (filters.username) params.append('username', filters.username);
    if (filters.page) params.append('page', filters.page);
    if (filters.size) params.append('size', filters.size);
    if (filters.sort_by) params.append('sort_by', filters.sort_by);
    if (filters.sort_order) params.append('sort_order', filters.sort_order);

    const response = await API.get(`/incidents/search?${params.toString()}`);
    return response.data;
  },

  getIncident: async (incidentId) => {
    const response = await API.get(`/incidents/${incidentId}`);
    return response.data;
  },

  deleteIncident: async (incidentId) => {
    const response = await API.delete(`/incidents/${incidentId}`);
    return response.data;
  },
};
