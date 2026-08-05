import React, { useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { IoClose } from 'react-icons/io5';

export const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
  closeOnOverlayClick = true,
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
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  };

  const modalSize = sizes[size] || sizes.md;

  if (!isOpen) return null;

  return createPortal(
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop overlay */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={closeOnOverlayClick ? onClose : undefined}
          className="absolute inset-0 bg-background/60 backdrop-blur-sm"
        />

        {/* Modal content box */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 15 }}
          transition={{ type: 'spring', duration: 0.35, bounce: 0.15 }}
          className={`relative bg-surface border border-border-color rounded-xl w-full ${modalSize} shadow-2xl flex flex-col max-h-[90vh] z-10`}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-border-color px-6 py-4">
            <h3 className="text-base font-semibold text-text-primary">
              {title}
            </h3>
            <button
              onClick={onClose}
              className="text-text-muted hover:text-text-primary transition-colors p-1.5 hover:bg-background rounded-lg cursor-pointer"
            >
              <IoClose className="w-5 h-5" />
            </button>
          </div>

          {/* Body */}
          <div className="flex-1 overflow-y-auto px-6 py-5 text-sm text-text-secondary">
            {children}
          </div>

          {/* Footer */}
          {footer && (
            <div className="flex items-center justify-end gap-3 border-t border-border-color px-6 py-4 bg-sidebar/20">
              {footer}
            </div>
          )}
        </motion.div>
      </div>
    </AnimatePresence>,
    document.body
  );
};
