import API from './api';

export const iocService = {
  getIOCs: async () => {
    const response = await API.get('/iocs/');
    return response.data;
  },

  createIOC: async (iocData) => {
    const response = await API.post('/iocs/', iocData);
    return response.data;
  },

  updateIOC: async (iocId, updates) => {
    const response = await API.put(`/iocs/${iocId}`, updates);
    return response.data;
  },

  deleteIOC: async (iocId) => {
    const response = await API.delete(`/iocs/${iocId}`);
    return response.data;
  },
};
