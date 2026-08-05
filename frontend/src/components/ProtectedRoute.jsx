import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ROUTES } from '../constants/routes';
import { Loader } from './ui/Loader';

export const ProtectedRoute = ({ children, allowedRoles = [] }) => {
  const { isAuthenticated, user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <Loader fullScreen />;
  }

  if (!isAuthenticated) {
    // Redirect to login page and save target URL for redirect after login
    return <Navigate to={ROUTES.LOGIN} state={{ from: location }} replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    // User does not have the required role, redirect to forbidden
    return <Navigate to={ROUTES.FORBIDDEN} replace />;
  }

  return children;
};
