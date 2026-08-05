import API from './api';

export const threatService = {
  checkIP: async (ip) => {
    const response = await API.get(`/threat/ip/${encodeURIComponent(ip)}`);
    return response.data;
  },

  checkDomain: async (domain) => {
    const response = await API.get(`/threat/domain/${encodeURIComponent(domain)}`);
    return response.data;
  },

  checkUser: async (username) => {
    const response = await API.get(`/threat/user/${encodeURIComponent(username)}`);
    return response.data;
  },
};
