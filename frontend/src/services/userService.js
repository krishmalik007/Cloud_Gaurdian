import API from './api';

export const userService = {
  getUsers: async () => {
    const response = await API.get('/users/');
    return response.data;
  },

  getUser: async (userId) => {
    const response = await API.get(`/users/${userId}`);
    return response.data;
  },

  updateRole: async (userId, role) => {
    const response = await API.put(`/users/${userId}/role`, { role });
    return response.data;
  },

  updateStatus: async (userId, enabled) => {
    const response = await API.put(`/users/${userId}/status`, { enabled });
    return response.data;
  },

  deleteUser: async (userId) => {
    const response = await API.delete(`/users/${userId}`);
    return response.data;
  },
};
