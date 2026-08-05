import API from './api';

export const auditService = {
  getAuditLogs: async () => {
    const response = await API.get('/audit/');
    return response.data;
  },

  getAuditDetail: async (auditId) => {
    const response = await API.get(`/audit/${auditId}`);
    return response.data;
  },
};
