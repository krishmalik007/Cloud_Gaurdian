import axios from 'axios';
import { ROUTES } from '../constants/routes';

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach access token
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('cg_access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle token refresh on 401
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

API.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Skip refresh logic for auth endpoints to prevent loops
    if (
      originalRequest.url.includes('/auth/login') ||
      originalRequest.url.includes('/auth/refresh') ||
      originalRequest.url.includes('/auth/register')
    ) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return API(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('cg_refresh_token');
      if (!refreshToken) {
        isRefreshing = false;
        // No refresh token, trigger logout redirect
        window.dispatchEvent(new Event('cg-logout'));
        return Promise.reject(error);
      }

      try {
        const response = await axios.post(`${API.defaults.baseURL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token } = response.data;
        localStorage.setItem('cg_access_token', access_token);
        
        API.defaults.headers.common.Authorization = `Bearer ${access_token}`;
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        
        processQueue(null, access_token);
        isRefreshing = false;
        
        return API(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        isRefreshing = false;
        // Refresh token failed, clear credentials and logout
        window.dispatchEvent(new Event('cg-logout'));
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default API;
