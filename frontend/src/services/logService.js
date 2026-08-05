import API from './api';

export const logService = {
  uploadLog: async (logData) => {
    const response = await API.post('/logs/', logData);
    return response.data;
  },
};
