import React from 'react';
import { useNavigate } from 'react-router-dom';
import { HiOutlineServer } from 'react-icons/hi';
import { Button } from '../../components/ui/Button';
import { ROUTES } from '../../constants/routes';

export default function Error500() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6 text-center select-none">
      <div className="flex flex-col items-center max-w-md gap-4">
        <HiOutlineServer className="w-16 h-16 text-red animate-bounce" />
        <div className="flex flex-col gap-1">
          <h1 className="text-4xl font-extrabold text-text-primary tracking-tight">500</h1>
          <h2 className="text-lg font-bold text-text-secondary">Internal Platform Error</h2>
          <p className="text-xs text-text-muted">
            The security correlation server encountered an unexpected error. Please check backend service logs.
          </p>
        </div>
        <div className="flex items-center gap-3 mt-4">
          <Button variant="outline" size="sm" onClick={() => window.location.reload()}>
            Retry Connection
          </Button>
          <Button variant="primary" size="sm" onClick={() => navigate(ROUTES.DASHBOARD)}>
            Go to SOC Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}
