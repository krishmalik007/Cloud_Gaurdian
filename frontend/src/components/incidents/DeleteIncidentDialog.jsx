import React from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { HiOutlineExclamation } from 'react-icons/hi';

export default function DeleteIncidentDialog({ isOpen, onClose, onConfirm, incidentId, isDeleting }) {
  const footer = (
    <>
      <Button variant="outline" size="sm" onClick={onClose} disabled={isDeleting}>
        Cancel Action
      </Button>
      <Button variant="danger" size="sm" onClick={onConfirm} isLoading={isDeleting}>
        Destroy Record
      </Button>
    </>
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Confirm Delete Incident"
      footer={footer}
      closeOnOverlayClick={!isDeleting}
    >
      <div className="flex gap-4">
        <div className="p-2.5 rounded-lg bg-red/10 border border-red/20 text-red h-max">
          <HiOutlineExclamation className="w-6 h-6 animate-pulse" />
        </div>
        <div className="flex flex-col gap-2 text-left">
          <p className="text-sm font-semibold text-text-primary">
            Are you sure you want to permanently delete incident record:
          </p>
          <span className="font-mono text-xs text-text-muted bg-background/50 border border-border-color rounded px-2.5 py-1.5 w-max">
            {incidentId}
          </span>
          <p className="text-xs text-text-muted">
            Warning: This action is irreversible. All associated correlation indices will be dropped from OpenSearch.
          </p>
        </div>
      </div>
    </Modal>
  );
}
