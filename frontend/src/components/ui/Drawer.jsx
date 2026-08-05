import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { IoClose } from 'react-icons/io5';

export const Drawer = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
}) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-xl',
    lg: 'max-w-3xl',
    xl: 'max-w-5xl',
  };

  const drawerWidth = sizes[size] || sizes.md;

  if (!isOpen) return null;

  return createPortal(
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex justify-end">
        {/* Backdrop overlay */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-background/60 backdrop-blur-xs"
        />

        {/* Drawer slide-in container */}
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'tween', duration: 0.3, ease: 'easeInOut' }}
          className={`relative bg-sidebar border-l border-border-color h-full w-full ${drawerWidth} shadow-2xl flex flex-col z-10`}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-border-color px-6 py-5 bg-background/40">
            <div>
              <h3 className="text-base font-semibold text-text-primary">
                {title}
              </h3>
            </div>
            <button
              onClick={onClose}
              className="text-text-muted hover:text-text-primary transition-colors p-1.5 hover:bg-background rounded-lg cursor-pointer"
            >
              <IoClose className="w-5 h-5" />
            </button>
          </div>

          {/* Body */}
          <div className="flex-1 overflow-y-auto px-6 py-6 text-sm text-text-secondary">
            {children}
          </div>

          {/* Footer */}
          {footer && (
            <div className="flex items-center justify-end gap-3 border-t border-border-color px-6 py-4 bg-background/80">
              {footer}
            </div>
          )}
        </motion.div>
      </div>
    </AnimatePresence>,
    document.body
  );
};
