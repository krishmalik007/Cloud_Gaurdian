import React from 'react';

export const Skeleton = ({
  className = '',
  circle = false,
  ...props
}) => {
  return (
    <div
      className={`animate-pulse bg-surface/50 border border-border-color/10 ${
        circle ? 'rounded-full' : 'rounded-md'
      } ${className}`}
      {...props}
    />
  );
};
