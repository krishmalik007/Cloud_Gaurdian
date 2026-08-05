import React from 'react';

export const Button = ({
  children,
  type = 'button',
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  icon: Icon,
  iconPosition = 'left',
  onClick,
  className = '',
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-background disabled:opacity-50 disabled:pointer-events-none cursor-pointer';
  
  const variants = {
    primary: 'bg-primary-blue hover:bg-primary-blue/90 text-text-primary focus:ring-primary-blue/50 shadow-lg shadow-primary-blue/20',
    secondary: 'bg-surface hover:bg-surface/80 text-text-secondary border border-border-color focus:ring-surface/50',
    outline: 'bg-transparent border border-border-color hover:bg-surface/40 hover:text-text-primary text-text-secondary focus:ring-border-color',
    danger: 'bg-red hover:bg-red/90 text-text-primary focus:ring-red/50 shadow-lg shadow-red/20',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-5 py-2.5 text-base',
  };

  const currentVariant = variants[variant] || variants.primary;
  const currentSize = sizes[size] || sizes.md;

  return (
    <button
      type={type}
      disabled={disabled || isLoading}
      onClick={onClick}
      className={`${baseStyles} ${currentVariant} ${currentSize} ${className}`}
      {...props}
    >
      {isLoading ? (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      ) : Icon && iconPosition === 'left' ? (
        <Icon className={`mr-2 ${size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4'}`} />
      ) : null}

      <span>{children}</span>

      {!isLoading && Icon && iconPosition === 'right' ? (
        <Icon className={`ml-2 ${size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4'}`} />
      ) : null}
    </button>
  );
};
