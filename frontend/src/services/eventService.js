import API from './api';

export const eventService = {
  getEvents: async () => {
    const response = await API.get('/events/');
    return response.data;
  },

  searchEvents: async (filters = {}) => {
    const params = new URLSearchParams();

    if (filters.provider) params.append('provider', filters.provider);
    if (filters.risk_level) params.append('risk_level', filters.risk_level);
    if (filters.status) params.append('status', filters.status);
    if (filters.username) params.append('username', filters.username);
    if (filters.event_name) params.append('event_name', filters.event_name);
    if (filters.event_type) params.append('event_type', filters.event_type);
    if (filters.region) params.append('region', filters.region);
    if (filters.is_incident !== undefined && filters.is_incident !== null) {
      params.append('is_incident', filters.is_incident);
    }
    if (filters.search) params.append('search', filters.search);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.page) params.append('page', filters.page);
    if (filters.size) params.append('size', filters.size);
    if (filters.sort_by) params.append('sort_by', filters.sort_by);
    if (filters.sort_order) params.append('sort_order', filters.sort_order);

    const response = await API.get(`/events/search?${params.toString()}`);
    return response.data;
  },

  getEvent: async (eventId) => {
    const response = await API.get(`/events/${eventId}`);
    return response.data;
  },

  getStats: async () => {
    const response = await API.get('/events/stats');
    return response.data;
  },
};
