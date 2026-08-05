import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import { HiOutlineShieldCheck } from 'react-icons/hi';
import { useAuth } from '../context/AuthContext';
import { ROUTES } from '../constants/routes';

export const AuthLayout = () => {
  const { isAuthenticated, loading } = useAuth();

  // If already authenticated, redirect to dashboard
  if (!loading && isAuthenticated) {
    return <Navigate to={ROUTES.DASHBOARD} replace />;
  }

  return (
    <div className="min-h-screen bg-background flex flex-col lg:flex-row items-center justify-center p-4 lg:p-0">
      {/* Left side panel: Decorative logo and theme statement */}
      <div className="hidden lg:flex flex-col justify-between w-1/2 h-screen bg-sidebar p-12 border-r border-border-color select-none">
        <div className="flex items-center gap-3">
          <HiOutlineShieldCheck className="w-8 h-8 text-primary-blue" />
          <span className="font-bold text-lg text-text-primary">
            Cloud<span className="text-primary-blue">Guardian</span>
          </span>
        </div>
        
        <div className="max-w-md my-auto flex flex-col gap-4">
          <div className="inline-flex items-center justify-center bg-primary-blue/10 border border-primary-blue/20 rounded-full px-3.5 py-1 text-xs text-primary-blue font-semibold w-max">
            Enterprise Security Suite
          </div>
          <h2 className="text-3xl font-extrabold text-text-primary tracking-tight leading-tight">
            Correlate Multi-Cloud Threat Intelligence in Real Time.
          </h2>
          <p className="text-sm text-text-secondary">
            CloudGuardian aggregates, processes, and correlates raw log streams across AWS, Azure, and GCP to surface high-fidelity alerts.
          </p>
        </div>

        <div className="text-[10px] text-text-muted">
          &copy; {new Date().getFullYear()} CloudGuardian Enterprise Platform.
        </div>
      </div>

      {/* Right side panel: Form views */}
      <div className="w-full lg:w-1/2 flex items-center justify-center min-h-[80vh] lg:min-h-screen">
        <div className="w-full max-w-md px-6 py-8 md:px-8 bg-surface border border-border-color lg:border-transparent lg:bg-transparent rounded-2xl shadow-xl lg:shadow-none">
          {/* Logo showing only on mobile */}
          <div className="flex lg:hidden items-center gap-2 mb-8 justify-center select-none">
            <HiOutlineShieldCheck className="w-8 h-8 text-primary-blue" />
            <span className="font-bold text-lg text-text-primary">
              Cloud<span className="text-primary-blue">Guardian</span>
            </span>
          </div>

          <Outlet />
        </div>
      </div>
    </div>
  );
};
