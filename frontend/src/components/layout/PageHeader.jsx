import React from 'react';

export const PageHeader = ({
  title,
  subtitle,
  action,
  className = '',
}) => {
  return (
    <div className={`flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6 select-none ${className}`}>
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-bold text-text-primary tracking-tight leading-tight">
          {title}
        </h1>
        {subtitle && (
          <p className="text-xs text-text-secondary font-medium">
            {subtitle}
          </p>
        )}
      </div>
      {action && (
        <div className="flex items-center gap-3">
          {action}
        </div>
      )}
    </div>
  );
};
