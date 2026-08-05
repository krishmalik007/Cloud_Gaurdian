import React from 'react';
import { motion } from 'framer-motion';

export const Card = ({
  children,
  title,
  subtitle,
  headerAction,
  className = '',
  animate = false,
  onClick,
  ...props
}) => {
  const CardComponent = onClick ? 'button' : 'div';
  const Wrapper = animate ? motion.div : CardComponent;

  const baseStyles = 'bg-surface border border-border-color rounded-xl p-5 text-left w-full relative overflow-hidden transition-shadow duration-300';
  const interactiveStyles = onClick ? 'hover:shadow-lg hover:shadow-background/50 cursor-pointer focus:outline-none focus:ring-1 focus:ring-primary-blue/50' : '';

  const animationProps = animate && onClick
    ? {
        whileHover: { y: -2, transition: { duration: 0.2 } },
        whileTap: { scale: 0.99 },
      }
    : animate
    ? {
        initial: { opacity: 0, y: 10 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.3 },
      }
    : {};

  return (
    <Wrapper
      className={`${baseStyles} ${interactiveStyles} ${className}`}
      onClick={onClick}
      {...animationProps}
      {...props}
    >
      {(title || subtitle || headerAction) && (
        <div className="flex items-start justify-between gap-4 mb-4 select-none">
          <div className="flex flex-col gap-0.5">
            {title && (
              <h3 className="text-sm font-semibold text-text-primary tracking-tight">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="text-xs text-text-muted">
                {subtitle}
              </p>
            )}
          </div>
          {headerAction && (
            <div className="flex items-center">
              {headerAction}
            </div>
          )}
        </div>
      )}
      <div className="text-sm text-text-secondary h-full">
        {children}
      </div>
    </Wrapper>
  );
};
