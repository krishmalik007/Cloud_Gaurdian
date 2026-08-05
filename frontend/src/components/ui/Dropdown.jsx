import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export const Dropdown = ({
  trigger,
  items = [],
  align = 'right',
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const alignments = {
    left: 'left-0 origin-top-left',
    right: 'right-0 origin-top-right',
  };

  const currentAlign = alignments[align] || alignments.right;

  return (
    <div className={`relative inline-block text-left ${className}`} ref={dropdownRef}>
      <div onClick={() => setIsOpen(!isOpen)} className="cursor-pointer">
        {trigger}
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -4 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -4 }}
            transition={{ duration: 0.15 }}
            className={`absolute z-40 mt-1.5 w-48 rounded-lg bg-surface border border-border-color shadow-2xl py-1 focus:outline-none ${currentAlign}`}
          >
            {items.map((item, idx) => {
              if (item.divider) {
                return <div key={idx} className="h-px bg-border-color my-1" />;
              }
              const Icon = item.icon;
              return (
                <button
                  key={idx}
                  onClick={(e) => {
                    setIsOpen(false);
                    if (item.onClick) item.onClick(e);
                  }}
                  className={`w-full text-left px-4 py-2 text-xs flex items-center gap-2.5 transition-colors cursor-pointer ${
                    item.danger
                      ? 'text-red hover:bg-red/10'
                      : 'text-text-secondary hover:bg-background hover:text-text-primary'
                  }`}
                >
                  {Icon && <Icon className="w-4 h-4 text-current" />}
                  <span>{item.label}</span>
                </button>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
