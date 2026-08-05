import React, { forwardRef } from 'react';

export const Input = forwardRef(({
  label,
  type = 'text',
  error,
  icon: Icon,
  className = '',
  containerClassName = '',
  rightElement,
  ...props
}, ref) => {
  return (
    <div className={`flex flex-col gap-1.5 w-full ${containerClassName}`}>
      {label && (
        <label className="text-xs font-semibold text-text-secondary select-none">
          {label}
        </label>
      )}
      <div className="relative flex items-center w-full">
        {Icon && (
          <div className="absolute left-3 text-text-muted pointer-events-none">
            <Icon className="w-4 h-4" />
          </div>
        )}
        <input
          type={type}
          ref={ref}
          className={`w-full bg-background border rounded-lg py-2 px-3 text-sm text-text-primary placeholder-text-muted transition-all duration-200 outline-none focus:border-primary-blue focus:ring-1 focus:ring-primary-blue/30 disabled:opacity-50 disabled:bg-background/80 ${
            Icon ? 'pl-9' : ''
          } ${
            rightElement ? 'pr-10' : ''
          } ${
            error ? 'border-red focus:border-red focus:ring-red/30' : 'border-border-color'
          } ${className}`}
          {...props}
        />
        {rightElement && (
          <div className="absolute right-3 text-text-muted flex items-center justify-center">
            {rightElement}
          </div>
        )}
      </div>
      {error && (
        <span className="text-xs text-red font-medium leading-none select-none">
          {error.message || error}
        </span>
      )}
    </div>
  );
});

Input.displayName = 'Input';
