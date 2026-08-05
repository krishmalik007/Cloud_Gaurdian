import React, { useEffect, useState } from 'react';
import { motion, useMotionValue, useTransform, animate } from 'framer-motion';

export default function StatCard({
  title,
  value = 0,
  icon: Icon,
  trend, // { type: 'up' | 'down', value: '12%' }
  variant = 'info', // 'info' | 'success' | 'warning' | 'danger'
  loading = false,
}) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    if (loading) return;
    const controls = animate(0, value, {
      duration: 0.8,
      ease: 'easeOut',
      onUpdate: (latest) => setDisplayValue(Math.floor(latest)),
    });
    return () => controls.stop();
  }, [value, loading]);

  const variants = {
    info: 'border-primary-blue/10 bg-primary-blue/5 hover:border-primary-blue/30 text-primary-blue shadow-primary-blue/5',
    success: 'border-green/10 bg-green/5 hover:border-green/30 text-green shadow-green/5',
    warning: 'border-orange/10 bg-orange/5 hover:border-orange/30 text-orange shadow-orange/5',
    danger: 'border-red/10 bg-red/5 hover:border-red/30 text-red shadow-red/5',
  };

  const currentVariant = variants[variant] || variants.info;

  return (
    <motion.div
      whileHover={{ y: -3, transition: { duration: 0.2 } }}
      className={`relative bg-surface/40 backdrop-blur-md border border-border-color rounded-xl p-5 shadow-lg flex flex-col justify-between h-32 overflow-hidden select-none transition-colors ${currentVariant}`}
    >
      <div className="flex items-start justify-between">
        <span className="text-xs font-semibold text-text-secondary tracking-tight">
          {title}
        </span>
        {Icon && (
          <div className="p-1.5 rounded-lg bg-background/60 border border-border-color/40 text-current flex items-center justify-center">
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="flex items-end justify-between mt-2">
        {loading ? (
          <div className="h-9 w-24 bg-surface rounded animate-pulse" />
        ) : (
          <h2 className="text-3xl font-extrabold text-text-primary tracking-tight">
            {displayValue.toLocaleString()}
          </h2>
        )}

        {trend && !loading && (
          <div
            className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full border ${
              trend.type === 'down'
                ? 'bg-green/10 text-green border-green/20'
                : 'bg-red/10 text-red border-red/20'
            }`}
          >
            <span>{trend.type === 'down' ? '↓' : '↑'}</span>
            <span>{trend.value}</span>
          </div>
        )}
      </div>
    </motion.div>
  );
}
