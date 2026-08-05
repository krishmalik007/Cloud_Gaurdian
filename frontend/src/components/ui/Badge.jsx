import React from 'react';

export const Badge = ({
  children,
  variant = 'info',
  size = 'md',
  className = '',
  dot = false,
}) => {
  const baseStyles = 'inline-flex items-center font-medium rounded-full border leading-none select-none';
  
  const variants = {
    success: 'bg-green/10 text-green border-green/20',
    warning: 'bg-orange/10 text-orange border-orange/20',
    danger: 'bg-red/10 text-red border-red/20',
    info: 'bg-primary-blue/10 text-primary-blue border-primary-blue/20',
    purple: 'bg-purple/10 text-purple border-purple/20',
    muted: 'bg-text-muted/10 text-text-secondary border-border-color',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-[10px]',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3 py-1.5 text-xs font-semibold',
  };

  const currentVariant = variants[variant] || variants.info;
  const currentSize = sizes[size] || sizes.md;

  const dotColors = {
    success: 'bg-green',
    warning: 'bg-orange',
    danger: 'bg-red',
    info: 'bg-primary-blue',
    purple: 'bg-purple',
    muted: 'bg-text-secondary',
  };
  const dotColor = dotColors[variant] || dotColors.info;

  return (
    <span className={`${baseStyles} ${currentVariant} ${currentSize} ${className}`}>
      {dot && (
        <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${dotColor}`} />
      )}
      {children}
    </span>
  );
};
