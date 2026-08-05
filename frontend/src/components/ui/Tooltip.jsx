import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export const Tooltip = ({
  children,
  content,
  position = 'top',
  className = '',
}) => {
  const [active, setActive] = useState(false);

  const showTip = () => {
    setActive(true);
  };

  const hideTip = () => {
    setActive(false);
  };

  const positions = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  const currentPosition = positions[position] || positions.top;

  return (
    <div
      className={`relative inline-flex ${className}`}
      onMouseEnter={showTip}
      onMouseLeave={hideTip}
      onFocus={showTip}
      onBlur={hideTip}
    >
      {children}
      <AnimatePresence>
        {active && content && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.12 }}
            className={`absolute z-50 px-2 py-1 text-[10px] font-semibold text-text-primary bg-sidebar border border-border-color rounded shadow-xl whitespace-nowrap pointer-events-none select-none ${currentPosition}`}
          >
            {content}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
