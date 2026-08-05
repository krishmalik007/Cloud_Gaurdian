import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Initialize auth state
  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem('cg_access_token');
      if (token) {
        try {
          const userData = await authService.me();
          setUser(userData);
        } catch (error) {
          console.error('Failed to restore user session:', error);
          logout();
        }
      }
      setLoading(false);
    };

    fetchUser();

    // Listen for logout events from Axios interceptor
    const handleLogoutEvent = () => {
      logout();
    };

    window.addEventListener('cg-logout', handleLogoutEvent);
    return () => {
      window.removeEventListener('cg-logout', handleLogoutEvent);
    };
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const data = await authService.login({ email, password });
      localStorage.setItem('cg_access_token', data.access_token);
      localStorage.setItem('cg_refresh_token', data.refresh_token);
      
      const userData = await authService.me();
      setUser(userData);
      return userData;
    } catch (error) {
      setUser(null);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (username, email, password, role = 'ANALYST') => {
    setLoading(true);
    try {
      const response = await authService.register({ username, email, password, role });
      return response;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('cg_access_token');
    localStorage.removeItem('cg_refresh_token');
    setUser(null);
  };

  const hasRole = (...roles) => {
    return user && roles.includes(user.role);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
