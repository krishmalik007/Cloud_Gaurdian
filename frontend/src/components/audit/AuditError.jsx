import React from 'react';
import { HiOutlineShieldExclamation } from 'react-icons/hi';
import { Button } from '../ui/Button';

export default function AuditError({ error, onRetry }) {
  const message = error?.response?.data?.detail || error?.message || 'Failed to fetch audit log database';

  return (
    <div className="flex flex-col items-center justify-center py-20 px-4 text-center select-none bg-red/5 border border-red/20 rounded-xl w-full">
      <div className="p-3 bg-red/10 border border-red/25 rounded-full text-red mb-4">
        <HiOutlineShieldExclamation className="w-10 h-10 animate-bounce" />
      </div>
      
      <h3 className="text-sm font-bold text-text-primary mb-1">
        Access Denied / Connection Failed
      </h3>
      
      <p className="text-xs text-text-secondary max-w-sm mb-5 leading-relaxed">
        {message}. Note that Audit logs are restricted to platform Administrators.
      </p>

      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          Refresh Feeds
        </Button>
      )}
    </div>
  );
}
