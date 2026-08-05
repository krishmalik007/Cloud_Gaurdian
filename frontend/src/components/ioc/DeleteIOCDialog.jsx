import React from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { HiOutlineExclamation } from 'react-icons/hi';

export default function DeleteIOCDialog({ isOpen, onClose, onConfirm, value, isDeleting }) {
  const footer = (
    <>
      <Button variant="outline" size="sm" onClick={onClose} disabled={isDeleting}>
        Cancel Action
      </Button>
      <Button variant="danger" size="sm" onClick={onConfirm} isLoading={isDeleting}>
        Destroy Watchlist Record
      </Button>
    </>
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Confirm Delete Indicator"
      footer={footer}
      closeOnOverlayClick={!isDeleting}
    >
      <div className="flex gap-4">
        <div className="p-2.5 rounded-lg bg-red/10 border border-red/20 text-red h-max">
          <HiOutlineExclamation className="w-6 h-6 animate-pulse" />
        </div>
        <div className="flex flex-col gap-2 text-left">
          <p className="text-sm font-semibold text-text-primary">
            Are you sure you want to permanently delete this indicator of compromise?
          </p>
          <span className="font-mono text-xs text-text-muted bg-background/50 border border-border-color rounded px-2.5 py-1.5 w-max">
            {value}
          </span>
          <p className="text-xs text-text-muted">
            Warning: This action will immediately remove the indicator from the correlation engine. Incoming logs matching this pattern will no longer be flagged.
          </p>
        </div>
      </div>
    </Modal>
  );
}
