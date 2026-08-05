import React from 'react';
import { useNavigate } from 'react-router-dom';
import { HiOutlineLockClosed } from 'react-icons/hi';
import { Button } from '../../components/ui/Button';
import { ROUTES } from '../../constants/routes';

export default function Error401() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6 text-center select-none">
      <div className="flex flex-col items-center max-w-md gap-4">
        <HiOutlineLockClosed className="w-16 h-16 text-red" />
        <div className="flex flex-col gap-1">
          <h1 className="text-4xl font-extrabold text-text-primary tracking-tight">401</h1>
          <h2 className="text-lg font-bold text-text-secondary">Session Expired</h2>
          <p className="text-xs text-text-muted">
            Your authorization session has expired or is invalid. Please sign in again to access telemetry.
          </p>
        </div>
        <div className="mt-4">
          <Button variant="primary" size="sm" onClick={() => navigate(ROUTES.LOGIN)}>
            Sign In Again
          </Button>
        </div>
      </div>
    </div>
  );
}
